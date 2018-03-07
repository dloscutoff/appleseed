
import sys
import os
from contextlib import contextmanager
from itertools import zip_longest, islice

from cfg import nil
import cfg
from parsing import parse
from thunk import Thunk, resolve_thunks, cons_iter
import help_text


# Appleseed built-in functions and macros
# Key = implementation name; value = Appleseed name

builtins = {"asl_cons": "cons",
            "asl_head": "head",
            "asl_tail": "tail",
            "asl_add": "add",
            "asl_sub": "sub",
            "asl_mul": "mul",
            "asl_div": "div",
            "asl_mod": "mod",
            "asl_less": "less?",
            "asl_equal": "equal?",
            "asl_eval": "eval",
            "asl_type": "type",
            "asl_debug": "debug",
            "asl_str": "str",
            "asl_chars": "chars",
            "asl_repr": "repr",
            "asl_bool": "bool",
            # The following are macros:
            "asl_def": "def",
            "asl_if": "if",
            "asl_quote": "q",
            "asl_object": "object",
            "asl_has_property": "has-property?",
            "asl_get_property": "get-property",
            "asl_copy": "copy",
            "asl_load": "load",
            # The following are intended for repl use:
            "asl_help": "help",
            "asl_restart": "restart",
            "asl_quit": "quit",
            }

# These are macros that cannot be called from other functions or
# macros, only from the top level

top_level_macros = ["asl_def", "asl_load"]

# These are macros that can only be called at top level in the repl

repl_macros = ["asl_help", "asl_restart", "asl_quit"]


# Decorators for member functions that implement builtins

def macro(pyfunc):
    pyfunc.is_macro = True
    pyfunc.name = pyfunc.__name__
    return pyfunc


def function(pyfunc):
    pyfunc.is_macro = False
    pyfunc.name = pyfunc.__name__
    return pyfunc


def params(min_param_count, max_param_count=None):
    def params_decorator(pyfunc):
        pyfunc.min_param_count = min_param_count
        if max_param_count is not None:
            pyfunc.max_param_count = max_param_count
        else:
            pyfunc.max_param_count = min_param_count
        return pyfunc
    return params_decorator


def no_thunks(pyfunc):
    def resolve_thunks_and_call(*args, **kwargs):
        resolved_args = []
        for value in args:
            value = resolve_thunks(value)
            resolved_args.append(value)
        return pyfunc(*resolved_args, **kwargs)
    resolve_thunks_and_call.__name__ = pyfunc.__name__
    return resolve_thunks_and_call


class Program:
    def __init__(self, repl=False, max_list_items=None):
        self.repl = repl
        self.max_list_items = max_list_items
        self.modules = []
        self.module_paths = [os.path.abspath(os.path.dirname(__file__))]
        self.extensions = []
        self.names = [{}]
        self.depth = 0
        self.builtins = []
        self.global_names = self.names[0]
        self.local_names = self.global_names
        # Go through the Appleseed builtins and put the corresponding
        # member functions into the top-level symbol table
        for func_name, asl_func_name in builtins.items():
            builtin = getattr(self, func_name)
            self.builtins.append(builtin)
            self.global_names[asl_func_name] = builtin
        # Load the standard library
        self.asl_load("library")

    def execute(self, code):
        if isinstance(code, str):
            # Determine whether the code is in single-line or
            # multiline form:
            # In single-line form, the code is parsed one line at a time
            # with closing parentheses inferred at the end of each line
            # In multiline form, the code is parsed as a whole, with
            # closing parentheses inferred only at the end
            # If any line in the code contains more closing parens than
            # opening parens, the code is assumed to be in multiline
            # form; otherwise, it's single-line
            codelines = code.split("\n")
            multiline = any(line.count(")") > line.count("(")
                            for line in codelines)
            result = None
            if multiline:
                # Parse code as a whole
                for expr in parse(code):
                    result = self.execute_expression(expr)
            else:
                # Parse each line separately
                for codeline in codelines:
                    for expr in parse(codeline):
                        result = self.execute_expression(expr)
            return result
        else:
            raise NotImplementedError("Argument to execute() must be "
                                      "str, not %s" % type(code))
    
    def execute_expression(self, expr):
        """Evaluate an expression; display it if in repl mode."""
        result = self.asl_eval(expr, top_level=True)
        # If running in repl mode, display the result
        if self.repl:
            self.display(result)
        return result

    def call_data(self, function, raw_args):
        """Returns parameter names, body, and list of eval'd args."""
        # Function should be a nested-tuple structure containing
        # parameter names and function body
        function_parts = list(islice(cons_iter(function), 3))
        if len(function_parts) == 2:
            param_names, body = function_parts
            # Function arguments are evaluated
            arglist = [self.asl_eval(arg) for arg in cons_iter(raw_args)]
        elif len(function_parts) > 2:
            cfg.error("list callable as function must have 2 elements,",
                      "not more")
            raise TypeError
        else:
            cfg.error("list callable as function must have 2 elements, not",
                      len(function_parts))
            raise TypeError
        return param_names, body, arglist

    def bind_params(self, param_names, arguments, namespace):
        """Binds arguments to param_names in namespace."""
        arguments = resolve_thunks(arguments)
        if isinstance(arguments, list):
            # This is a function with a Python list of eval'd arguments
            arg_iter = iter(arguments)
            procedure_type = "function"
        elif isinstance(arguments, tuple):
            # This is a macro with a nested tuple of uneval'd arguments
            arg_iter = cons_iter(arguments)
            procedure_type = "macro"
        else:
            # Not sure what's going on here
            raise NotImplementedError("arguments should be Python list or "
                                      "nested tuple, not "
                                      + str(type(arguments)))
        param_names = resolve_thunks(param_names)
        if isinstance(param_names, tuple):
            name_iter = cons_iter(param_names)
            required_param_count = 0
            optional_param_count = 0
            arg_count = 0
            for name, arg in zip_longest(name_iter, arg_iter):
                name = resolve_thunks(name)
                if name is None:
                    # Ran out of argument names
                    arg_count += 1
                elif isinstance(name, tuple):
                    # This is probably an argname + default value pair
                    default_pair = list(islice(cons_iter(name), 3))
                    if len(default_pair) == 2:
                        name, default_val = map(resolve_thunks, default_pair)
                        if not isinstance(name, str):
                            cfg.error("parameter list must contain names, not",
                                      self.asl_type(name))
                            raise TypeError
                        elif name in self.global_names:
                            cfg.warn(procedure_type, "parameter name shadows",
                                     "global name", name)
                        if arg is None:
                            # No argument given; use default value
                            namespace[name] = self.asl_eval(default_val)
                        else:
                            # Use argument given
                            namespace[name] = arg
                            arg_count += 1
                        optional_param_count += 1
                    elif name == nil:
                        cfg.error("parameter list must contain names, not ()")
                        raise TypeError
                    elif len(default_pair) == 1:
                        cfg.error("missing default value for",
                                  resolve_thunks(default_pair[0]))
                        raise TypeError
                    elif len(default_pair) > 2:
                        cfg.error("too many elements in parameter default",
                                  "value specification list")
                        raise TypeError
                elif arg is None:
                    # Ran out of argument values
                    required_param_count += 1
                elif isinstance(name, str):
                    if optional_param_count > 0:
                        cfg.error("required parameter", name, "must come",
                                  "before optional parameters")
                        raise TypeError
                    if name in self.global_names:
                        cfg.warn(procedure_type, "parameter name shadows",
                                 "global name", name)
                    namespace[name] = arg
                    required_param_count += 1
                    arg_count += 1
                else:
                    cfg.error("parameter list must contain names, not",
                              self.asl_type(name))
                    raise TypeError
            min_name_count = required_param_count
            max_name_count = required_param_count + optional_param_count
            if arg_count < required_param_count:
                # Not enough arguments
                cfg.error(procedure_type, "takes at least", min_name_count,
                          "arguments, got", arg_count)
                raise TypeError
            elif arg_count > max_name_count:
                # Too many arguments
                cfg.error(procedure_type, "takes at most", max_name_count,
                          "arguments, got", arg_count)
                raise TypeError
        elif isinstance(param_names, str):
            # Single name, bind entire arglist to it
            arglist_name = param_names
            if arglist_name in self.global_names:
                cfg.warn(procedure_type, "parameter name shadows global name",
                         arglist_name)
            if procedure_type == "function":
                # Repackage arglist into nested tuples and assign
                args = nil
                for arg in reversed(arguments):
                    args = (arg, args)
                namespace[arglist_name] = args
            elif procedure_type == "macro":
                # Quote arglist and assign
                namespace[arglist_name] = ("q", (arguments, ()))
            else:
                # Code should never get here
                raise NotImplementedError("procedure_type should be either "
                                          "function or macro")
        else:
            cfg.error("parameters must either be name or list of names,",
                      "not", self.asl_type(param_names))
            raise TypeError

    def call(self, function, raw_args):
        """Generate a deferred call of a user-defined function."""
        try:
            call_data = self.call_data(function, raw_args)
        except TypeError:
            # There was a problem with the structure of the supposed
            # function (call_data already gave the error message)
            return nil
        else:
            return Thunk(self, *call_data)

    def resolve_macros(self, head, raw_args):
        """Given head and tail of an expression, rewrite any macros.

This function eliminates the builtins <if> and <eval>, as well as any
user-defined macros.
- If the head of the expression is <if>, evaluate the condition and
  replace the expression with the true or false branch.
- If the head of the expression is <eval>, evaluate the argument and
  replace the expression with the result.
- If the head of the expression is a user-defined macro, call the
  macro with the arguments unevaluated; then evaluate its return
  value and replace the expression with that.
"""
        head = resolve_thunks(head)
        is_udef_macro = self.is_macro(head)
        while head == self.asl_if or head == self.asl_eval or is_udef_macro:
            if head == self.asl_if:
                # The head is (some name for) asl_if
                # If needs exactly three arguments
                if_args = list(islice(cons_iter(raw_args), 4))
                if len(if_args) == 3:
                    condition = self.asl_eval(if_args[0])
                    if self.asl_bool(condition):
                        # Use the true branch
                        expression = if_args[1]
                    else:
                        # Use the false branch
                        expression = if_args[2]
                elif len(if_args) > 3:
                    cfg.error("if takes 3 arguments, not more")
                    raise TypeError
                else:
                    cfg.error("if takes 3 arguments, not", len(if_args))
                    raise TypeError
            elif head == self.asl_eval:
                # The head is (some name for) asl_eval
                # Eval needs exactly one argument
                eval_args = list(islice(cons_iter(raw_args), 2))
                if len(eval_args) == 1:
                    expression = self.asl_eval(eval_args[0])
                elif len(eval_args) > 1:
                    cfg.error("eval takes 1 argument, not more")
                    raise TypeError
                else: # zero arguments given
                    cfg.error("eval requires an argument")
                    raise TypeError
            elif is_udef_macro:
                # The head is a list representing a user-defined macro
                flag, macro_params, macro_body = cons_iter(head)
                macro_names = {}
                try:
                    self.bind_params(macro_params, raw_args, macro_names)
                except TypeError:
                    raise
                # Substitute the arguments for the parameter names in
                # the macro body expression
                expression = self.replace(macro_names,
                                          resolve_thunks(macro_body))
            expression = resolve_thunks(expression)
            if expression and isinstance(expression, tuple):
                # The result was a nonempty s-expression which could be
                # another macro invocation, so set up for another trip
                # through the loop
                head, raw_args = expression
                head = resolve_thunks(self.asl_eval(head))
                is_udef_macro = self.is_macro(head)
            else:
                # The result was nil or something other than an
                # s-expression; just return it, with a head of None
                return None, expression
        # We exit the loop when we have an s-expression whose head is
        # no longer a macro--finish its evaluation somewhere else
        return head, raw_args

    def is_macro(self, expression):
        """Does an expression represent a user-defined macro?"""
        expression = resolve_thunks(expression)
        # A macro must be a nonempty list (i.e. nested tuple)
        if expression and isinstance(expression, tuple):
            # Its first element must be an integer
            head = resolve_thunks(expression[0])
            if head == 0 or head == "0":
                # And it must have two other elements (params and body)
                tail = list(islice(cons_iter(expression[1]), 3))
                return (len(tail) == 2)
            else:
                return False
        else:
            return False

    def replace(self, bindings, expression):
        """Replaces names in expression with their values from bindings.

Bindings is a dictionary; expression is any expression.
Names that aren't in bindings are left untouched.
"""
        if expression and isinstance(expression, tuple):
            # An s-expression
            head, tail = map(resolve_thunks, expression)
            return (self.replace(bindings, head),
                    self.replace(bindings, tail))
        elif isinstance(expression, str) and expression in bindings:
            # A name that needs to be replaced
            return bindings[expression]
        else:
            # Empty list, non-bound names, etc.
            return expression

    def display(self, value):
        if value is not None and not self.quiet:
            print(self.asl_repr(value))

    def inform(self, *messages):
        if self.repl and not self.quiet:
            print(*messages)
    
    @contextmanager
    def new_scope(self):
        self.depth += 1
        self.names.append({})
        self.local_names = self.names[self.depth]
        try:
            yield self.local_names
        finally:
            self.names.pop()
            self.depth -= 1
            self.local_names = self.names[self.depth]

    @function
    @params(2)
    def asl_cons(self, head, tail):
        if isinstance(tail, tuple) or isinstance(tail, Thunk):
            # TODO: do we need to resolve a tail thunk one level to
            # make sure it's a list?
            return (head, tail)
        else:
            cfg.error("cannot cons to", self.asl_type(tail), "in Appleseed")
            return nil

    @function
    @params(1)
    @no_thunks
    def asl_head(self, lyst):
        if isinstance(lyst, tuple):
            if lyst == nil:
                return nil
            else:
                return lyst[0]
        else:
            cfg.error("cannot get head of", self.asl_type(lyst))
            return nil

    @function
    @params(1)
    @no_thunks
    def asl_tail(self, lyst):
        if isinstance(lyst, tuple):
            if lyst == nil:
                return nil
            else:
                return lyst[1]
        else:
            cfg.error("cannot get tail of", self.asl_type(lyst))
            return nil

    @function
    @params(2)
    @no_thunks
    def asl_add(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            # Note: this case includes booleans, since in Python they
            # are special cases of int
            return arg1 + arg2
        else:
            cfg.error("cannot add", self.asl_type(arg1), "and",
                      self.asl_type(arg2))
            return nil

    @function
    @params(2)
    @no_thunks
    def asl_sub(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 - arg2
        else:
            cfg.error("cannot subtract", self.asl_type(arg1), "and",
                      self.asl_type(arg2))
            return nil

    @function
    @params(2)
    @no_thunks
    def asl_mul(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 * arg2
        else:
            cfg.error("cannot multiply", self.asl_type(arg1), "and",
                      self.asl_type(arg2))
            return nil

    @function
    @params(2)
    @no_thunks
    def asl_div(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            if arg2 != 0:
                return arg1 // arg2
            else:
                cfg.error("division by zero")
                return nil
        else:
            cfg.error("cannot divide", self.asl_type(arg1), "and",
                      self.asl_type(arg2))
            return nil

    @function
    @params(2)
    @no_thunks
    def asl_mod(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            if arg2 != 0:
                return arg1 % arg2
            else:
                cfg.error("mod by zero")
                return nil
        else:
            cfg.error("cannot mod", self.asl_type(arg1), "and",
                      self.asl_type(arg2))
            return nil

    @function
    @params(2)
    @no_thunks
    def asl_less(self, arg1, arg2):
        while isinstance(arg1, tuple) and isinstance(arg2, tuple):
            if arg1 and not arg2:
                # arg2 is nil and arg1 is non-nil
                return False
            elif arg2 and not arg1:
                # arg1 is nil and arg2 is non-nil
                return True
            elif not arg1 and not arg2:
                # Both are nil
                return False
            elif self.asl_less(arg1[0], arg2[0]):
                # arg1's head is less than arg2's head
                return True
            elif self.asl_less(arg2[0], arg1[0]):
                # arg2's head is less than arg1's head
                return False
            else:
                # The heads are equal, so compare the tails; but do
                # it with a loop, not recursion
                arg1 = resolve_thunks(arg1[1])
                arg2 = resolve_thunks(arg2[1])
        if (isinstance(arg1, int) and isinstance(arg2, int)
                or isinstance(arg1, str) and isinstance(arg2, str)):
            return arg1 < arg2
        else:
            cfg.error("cannot use less? to compare", self.asl_type(arg1),
                      "and", self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_equal(self, arg1, arg2):
        if arg1 == arg2:
            # Two identical values or thunks
            return True
        arg1 = resolve_thunks(arg1)
        arg2 = resolve_thunks(arg2)
        while isinstance(arg1, tuple) and isinstance(arg2, tuple):
            if arg1 == arg2:
                # Both nil, or identical heads and identical tails
                # (possibly involving thunks)
                return True
            elif arg1 == nil or arg2 == nil:
                # One argument is nil and the other is non-nil
                return False
            elif not self.asl_equal(arg1[0], arg2[0]):
                # arg1's head is not equal to arg2's head
                return False
            else:
                # The heads are equal, so compare the tails; but do
                # it with a loop, not recursion
                arg1 = resolve_thunks(arg1[1])
                arg2 = resolve_thunks(arg2[1])
        return arg1 == arg2

    @function
    @params(1)
    @no_thunks
    def asl_eval(self, code, top_level=False):
        if code and isinstance(code, tuple):
            # A function/macro call
            function = self.asl_eval(code[0])
            raw_args = code[1]
            # Eliminate any macro calls, including <if> and <eval>
            try:
                function, raw_args = self.resolve_macros(function, raw_args)
            except TypeError:
                # resolve_macros encountered an error condition (it
                # already gave the error message)
                return nil
            function = resolve_thunks(function)
            if function is None:
                # After resolving macros, the result was a simple
                # value, not an s-expression
                code = raw_args
            elif function and isinstance(function, tuple):
                # User-defined function or macro
                return self.call(function, raw_args)
            elif function in self.builtins:
                # Builtin function or macro
                if not self.repl and function.name in repl_macros:
                    cfg.error(builtins[function.name], "can only be used",
                              "in repl mode")
                    return nil
                if not top_level and (function.name in top_level_macros
                                      or function.name in repl_macros):
                    cfg.error(builtins[function.name],
                              "cannot be called from a user-defined function")
                    return nil
                if function.is_macro:
                    # Macros receive their args unevaluated
                    args = list(cons_iter(raw_args))
                else:
                    # Functions receive their args evaluated
                    args = [self.asl_eval(arg) for arg in cons_iter(raw_args)]
                try:
                    return function(*args)
                except TypeError as err:
                    # Wrong number of arguments to builtin
                    if len(args) < function.min_param_count:
                        cfg.error(builtins[function.name], "takes at least",
                                  function.min_param_count, "arguments, got",
                                  len(args))
                    elif len(args) > function.max_param_count:
                        cfg.error(builtins[function.name], "takes at most",
                                  function.max_param_count, "arguments, got",
                                  len(args))
                    else:
                        # Code should never get here--just re-raise
                        # the TypeError
                        raise
                    return nil
            else:
                # Trying to call something other than a builtin or
                # user-defined function
                cfg.error(function, "is not a function or macro")
                return nil
        if code == nil:
            # Nil evaluates to itself
            return nil
        elif isinstance(code, str):
            # Name
            if code in self.local_names:
                return self.local_names[code]
            elif code in self.global_names:
                return self.global_names[code]
            else:
                cfg.error("referencing undefined name", code)
                return nil
        elif (isinstance(code, int) or isinstance(code, dict)
              or code in self.builtins):
            # Int, Bool, Object, or Builtin evaluates to itself
            return code
        else:
            # Code should never get here
            raise NotImplementedError("unknown type in asl_eval: %s"
                                      % type(code))

    @function
    @params(1)
    @no_thunks
    def asl_type(self, value):
        # TODO: change this to base-type?
        if isinstance(value, bool):
            return "Bool"
        elif isinstance(value, int):
            return "Int"
        elif isinstance(value, str):
            return "String"
        elif isinstance(value, tuple):
            return "List"
        elif isinstance(value, dict):
            return "Object"
        elif value in self.builtins:
            return "Builtin"
        else:
            # Code should never get here
            raise NotImplementedError("unknown type in asl_type")

    @function
    @params(2)
    @no_thunks
    def asl_debug(self, output, expression):
        if output is not None:
            print(self.asl_repr(output), file=sys.stderr)
        return expression

    @function
    @params(1)
    @no_thunks
    def asl_repr(self, value):
        if value == nil:
            result = "()"
        elif isinstance(value, tuple):
            # List (as nested tuple)
            result = "("
            beginning = True
            for index, item in enumerate(cons_iter(value)):
                if beginning:
                    beginning = False
                else:
                    result += " "
                if self.max_list_items and index >= self.max_list_items:
                    # Don't show all of a long list--it could be infinite
                    result += "..."
                    break
                else:
                    result += self.asl_repr(item)
            result += ")"
        elif isinstance(value, bool):
            # Boolean
            result = "true" if value else "false"
        elif isinstance(value, int):
            # Integer
            result = str(value)
        elif isinstance(value, str):
            # String
            if any(c in value for c in cfg.SPECIAL_CHARS):
                result = value.replace(cfg.TOKEN_DELIMITER,
                                       cfg.TOKEN_DELIMITER * 2)
                result = cfg.TOKEN_DELIMITER + result + cfg.TOKEN_DELIMITER
            else:
                result = value
        elif isinstance(value, dict):
            # Object
            result = "{"
            if "type" in value:
                result += "(type %s)" % self.asl_repr(value["type"])
                beginning = False
            else:
                beginning = True
            for property_name, property_value in value.items():
                if property_name != "type":
                    if beginning:
                        beginning = False
                    else:
                        result += " "
                    result += "(%s %s)" % (self.asl_repr(property_name),
                                           self.asl_repr(property_value))
            result += "}"
        elif value in self.builtins:
            # One of the builtin functions or macros
            result = ("<builtin %s %s>"
                      % ("macro" if value.is_macro else "function",
                         builtins[value.name]))
        else:
            # Code should never get here
            raise NotImplementedError("unknown type in asl_repr")
        return result
    
    @function
    @params(1)
    @no_thunks
    def asl_str(self, value):
        if isinstance(value, tuple):
            result = ""
            for char_code in cons_iter(value):
                if isinstance(char_code, int):
                    try:
                        result += chr(char_code)
                    except ValueError:
                        # Can't convert this number to a character
                        cfg.warn("cannot convert", char_code, "to character")
                        pass
                else:
                    cfg.error("argument of str must be list of Ints, not of",
                              self.asl_type(char_code))
                    return nil
            return result
        else:
            cfg.error("argument of str must be list of Ints, not",
                      self.asl_type(value),
                      "\nDid you mean to use repr instead?")
            return nil

    @function
    @params(1)
    @no_thunks
    def asl_chars(self, value):
        if isinstance(value, str):
            result = nil
            for char in reversed(value):
                result = (ord(char), result)
            return result
        else:
            cfg.error("argument of chars must be String, not",
                      self.asl_type(value))
            return nil

    @function
    @params(1)
    @no_thunks
    def asl_bool(self, value):
        return value not in (0, False, nil, "", {})

    @macro
    @params(2)
    def asl_def(self, name, value):
        if isinstance(name, str):
            if name in self.global_names:
                cfg.error("name", name, "already in use")
                return nil
            else:
                self.global_names[name] = self.asl_eval(value)
                return name
        else:
            cfg.error("cannot define", self.asl_type(name),
                      self.asl_repr(name))
            return nil

    @macro
    @params(3)
    def asl_if(self, cond, trueval, falseval):
        # Arguments are not pre-evaluated, so cond needs to be evaluated
        # here
        cond = self.asl_eval(cond)
        if self.asl_bool(cond):
            return self.asl_eval(trueval)
        else:
            return self.asl_eval(falseval)

    @macro
    @params(1)
    def asl_quote(self, quoted):
        return quoted

    @macro
    @params("variadic")
    def asl_object(self, *properties):
        obj = {}
        for prop in properties:
            name_value_pair = list(islice(cons_iter(prop), 3))
            if len(name_value_pair) == 2:
                prop_name, expression = name_value_pair
                prop_value = self.asl_eval(expression)
                obj[prop_name] = prop_value
                # TBD: warn when overwriting an existing property?
            elif len(name_value_pair) > 2:
                cfg.error("(name value) lists in object constructor must have",
                          "2 elements, not more")
                return nil
            else:
                cfg.error("(name value) lists in object constructor must have",
                          "2 elements, not", len(name_value_pair))
                return nil
        return obj

    @macro
    @params(2)
    def asl_has_property(self, obj, prop_name):
        obj = resolve_thunks(self.asl_eval(obj))
        if isinstance(obj, dict):
            # TBD: error if prop_name is a list or something?
            return prop_name in obj
        else:
            cfg.error(self.asl_type(obj), "does not have properties")
            return nil

    @macro
    @params(2, 3)
    def asl_get_property(self, obj, prop_name, default=None):
        obj = resolve_thunks(self.asl_eval(obj))
        if isinstance(obj, dict):
            if prop_name in obj:
                # The object has this property; return it
                return obj[prop_name]
            elif default is not None:
                # The object doesn't have the property; return the
                # default value
                return self.asl_eval(default)
            else:
                # The object doesn't have the property and no default
                # was provided; error
                cfg.error("object does not have property", prop_name)
                return nil
        else:
            cfg.error("cannot get property of", self.asl_type(obj))
            return nil

    @macro
    @params(1, "variadic")
    def asl_copy(self, obj, *new_properties):
        obj = resolve_thunks(self.asl_eval(obj))
        if isinstance(obj, dict):
            # Create a new Object from this one, possibly with some
            # properties added or changed
            new_obj = obj.copy()
            for prop in new_properties:
                name_value_pair = list(islice(cons_iter(prop), 3))
                if len(name_value_pair) == 2:
                    prop_name, expression = name_value_pair
                    prop_value = self.asl_eval(expression)
                    new_obj[prop_name] = prop_value
                elif len(name_value_pair) > 2:
                    cfg.error("(name value) lists in object copy must have",
                              "2 elements, not more")
                    return nil
                else:
                    cfg.error("(name value) lists in object copy must have",
                              "2 elements, not", len(name_value_pair))
                    return nil
            return new_obj
        else:
            # If copy is given something that isn't an object, we
            # can't modify any properties; but we'll still return
            # the object as-is
            if new_properties:
                cfg.warn("cannot set properties of", self.asl_type(obj))
            return obj

    @macro
    @params(1)
    def asl_load(self, module):
        if isinstance(module, str):
            if not module.endswith(".asl"):
                module += ".asl"
            abspath = os.path.abspath(os.path.join(self.module_paths[-1],
                                                   module))
            module_directory, module_name = os.path.split(abspath)
            if abspath not in self.modules:
                # Module has not already been loaded
                try:
                    with open(abspath) as f:
                        module_code = f.read()
                except (FileNotFoundError, IOError):
                    cfg.error("could not load", module_name, "from",
                              module_directory)
                else:
                    # Add the module to the list of loaded modules
                    self.modules.append(abspath)
                    # Push the module's directory to the stack of module
                    # directories--this allows relative paths in load
                    # calls from within the module
                    self.module_paths.append(module_directory)
                    # Execute the module code
                    self.execute(module_code)
                    # Put everything back the way it was before loading
                    self.module_paths.pop()
                    self.inform("Loaded", module)
            else:
                self.inform("Already loaded", module)
        else:
            cfg.error("load requires module name, not", self.asl_repr(module))
        return None

    @macro
    @params(0)
    def asl_help(self):
        self.inform(help_text.help_text)
        return None

    @macro
    @params(0)
    def asl_restart(self):
        self.__init__(repl=self.repl, max_list_items=self.max_list_items)
        self.inform("Restarting...")
        return None

    @macro
    @params(0)
    def asl_quit(self):
        raise cfg.UserQuit

    @property
    def quiet(self):
        # True (suppress output) while in process of loading modules
        return len(self.module_paths) > 1


