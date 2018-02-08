#!/usr/bin/python3

import sys
import os
from contextlib import contextmanager
from itertools import zip_longest


VERSION = "0.0.1"

WHITESPACE = " \t\n\r"
SYMBOLS = "()"
LINE_COMMENT_CHAR = ";"
BLOCK_COMMENT_OPEN = "(;"
STRING_DELIMITER = '"'
SPECIAL_CHARS = WHITESPACE + SYMBOLS + LINE_COMMENT_CHAR + STRING_DELIMITER

# The empty tuple represents the empty list, nil
nil = ()


# Shortcut functions for print without newline and print to stderr
def write(*args):
    print(*args, end="")


def error(*args):
    print("Error:", *args, file=sys.stderr)


def warn(*args):
    print("Warning:", *args, file=sys.stderr)


def scan(code):
    """Take a string and yield a series of tokens."""
    # Add a newline to the end to allow peeking at the next character
    # without requiring a check for end-of-string
    code += "\n"
    i = 0
    while i < len(code):
        char = code[i]
        if char in WHITESPACE:
            # WHITESPACE (ignore)
            pass
        elif char == LINE_COMMENT_CHAR:
            # Start of a comment--scan till newline
            while code[i+1] != "\n":
                i += 1
        elif code[i:i+2] == BLOCK_COMMENT_OPEN:
            # Start of a block comment--this will be handled by the
            # parser
            yield code[i:i+2]
            i += 1
        elif char in SYMBOLS:
            # Reserved symbol
            yield char
        elif char == STRING_DELIMITER:
            # Start of a literal string--scan till the end of it
            # A literal string looks like "chars ""and"" quote-pairs"
            # (which represents this string: chars "and" quote-pairs)
            # TBD: should a string be able to contain literal newlines?
            # Should there be escape codes for such things?
            a = i
            try:
                while code[i] == STRING_DELIMITER:
                    while code[i+1] != STRING_DELIMITER:
                        i += 1
                    i += 2
            except IndexError:
                # code[i+1] is past the end of the string; in this
                # case, code[i] is the final newline, so yield
                # everything but the newline, with a supplied
                # closing delimiter, as the string token
                warn("unterminated string")
                yield code[a:i] + STRING_DELIMITER
            else:
                # The while loop took us past the closing delimiter,
                # so back up a notch and then yield the string token
                i -= 1
                yield code[a:i+1]
        else:
            # Start of a name or literal integer--scan till the end of it
            a = i
            while code[i+1] not in SPECIAL_CHARS:
                i += 1
            yield code[a:i+1]
        i += 1


def parse(code):
    """Take code and turn it into a parse tree.

The code can be a string or an iterator that yields tokens.
The resulting parse tree is an Appleseed list (i.e. nested tuples).
"""
    if isinstance(code, str):
        # If we're given a raw codestring, scan it before parsing
        code = scan(code)
    rest = None
    while rest is None:
        try:
            token = next(code)
        except StopIteration:
            # If there's still more to parse and we've run out of tokens,
            # supply missing close-parens
            token = ")"
        if token == "(":
            element = parse(code)
        elif token == BLOCK_COMMENT_OPEN:
            rest_of_comment = parse(code)
            return parse(code)
        elif token == ")":
            return nil
        elif token.isdigit() or token.startswith("-") and token[1:].isdigit():
            element = int(token)
        elif token.startswith(STRING_DELIMITER):
            # Literal strings are modeled as auto-quoted names
            # Strip the delimiters from the outside
            string = token[1:-1]
            # Replace the doubled delimiters with single delimiters
            string = string.replace(STRING_DELIMITER * 2, STRING_DELIMITER)
            element = ("q", (string, ()))
        else:
            element = token
        return (element, parse(code))


def cons_iter(nested_tuple):
    """Iterate over a cons chain of nested tuples."""
    while nested_tuple:
        yield nested_tuple[0]
        nested_tuple = nested_tuple[1]


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
            # The following four are macros:
            "asl_def": "def",
            "asl_if": "if",
            "asl_quote": "q",
            "asl_load": "load",
            # The following three are intended for repl use:
            "asl_help": "help",
            "asl_restart": "restart",
            "asl_quit": "quit",
            }

# These are functions and macros that should not output their return
# values when called at the top level (except in repl mode)

top_level_quiet_fns = ["asl_def", "asl_load"]

# These are functions and macros that cannot be called from other
# functions or macros, only from the top level

top_level_only_fns = ["asl_load", "asl_help", "asl_restart", "asl_quit"]


# Decorators for member functions that implement builtins

def macro(pyfunc):
    pyfunc.is_macro = True
    return pyfunc


def function(pyfunc):
    pyfunc.is_macro = False
    return pyfunc


def params(param_count):
    def params_decorator(pyfunc):
        pyfunc.param_count = param_count
        return pyfunc
    return params_decorator


# Exception that is raised by the (quit) macro

class UserQuit(BaseException):
    pass


class Program:
    def __init__(self, repl=False):
        self.repl = repl
        self.modules = []
        self.module_paths = [os.path.abspath(os.path.dirname(__file__))]
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

    def execute(self, code):
        if isinstance(code, str):
            # First determine whether the code is in single-line or
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
            if not multiline:
                for codeline in codelines:
                    result = self.execute(parse(codeline))
                return result
            else:
                code = parse(code)
        # Evaluate each expression in the code and (possibly) display it
        result = nil
        for expr in cons_iter(code):
            # Figure out which function the outermost call is
            outer_function = None
            if expr and isinstance(expr, tuple) and isinstance(expr[0], str):
                outer_function = self.asl_eval(expr[0])
                if outer_function in self.builtins:
                    outer_function = outer_function.__name__
            result = self.asl_eval(expr, top_level=True)
            # If outer function is in the top_level_quiet_fns list,
            # suppress output--but always show output when running in
            # repl mode
            # TODO: output result only when in repl mode
            if self.repl or outer_function not in top_level_quiet_fns:
                self.display(result)
        return result

    def call_data(self, function, raw_args):
        """Returns parameter names, body, and list of eval'd args."""
        # Function should be a nested-tuple structure containing
        # parameter names and function body
        if function and function[1]:
            if not function[1][1]:
                param_names = function[0]
                body = function[1][0]
                # Function arguments are evaluated
                arglist = [self.asl_eval(arg) for arg in cons_iter(raw_args)]
            else:
                error("list too long to be interpreted as function")
                raise TypeError
        else:
            error("list too short to be interpreted as function")
            raise TypeError
        return param_names, body, arglist

    def bind_params(self, param_names, arguments, namespace):
        """Binds arguments to param_names in namespace."""
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
        if isinstance(param_names, tuple):
            name_iter = cons_iter(param_names)
            required_param_count = 0
            optional_param_count = 0
            arg_count = 0
            for name, arg in zip_longest(name_iter, arg_iter):
                if name is None:
                    # Ran out of argument names
                    arg_count += 1
                elif isinstance(name, tuple):
                    if (name and isinstance(name[0], str) and name[1]
                            and not name[1][1]):
                        # This is an argname + default value pair
                        default_val = name[1][0]
                        name = name[0]
                        if name in self.global_names:
                            warn(procedure_type, "parameter name shadows",
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
                        error("parameter list must contain names, not ()")
                        raise TypeError
                    elif not isinstance(name[0], str):
                        error("parameter list must contain names, not",
                              self.asl_type(name[0]))
                        raise TypeError
                    elif not name[1]:
                        error("missing default value for", name[0])
                        raise TypeError
                    elif name[1][1]:
                        error("too many elements in parameter default",
                              "value specification list")
                        raise TypeError
                elif arg is None:
                    # Ran out of argument values
                    required_param_count += 1
                elif isinstance(name, str):
                    if optional_param_count > 0:
                        error("required parameter", name, "must come before",
                              "optional parameters")
                        raise TypeError
                    if name in self.global_names:
                        warn(procedure_type, "parameter name shadows",
                             "global name", name)
                    namespace[name] = arg
                    required_param_count += 1
                    arg_count += 1
                else:
                    error("parameter list must contain names, not",
                          self.asl_type(name))
                    raise TypeError
            min_name_count = required_param_count
            max_name_count = required_param_count + optional_param_count
            if arg_count < required_param_count:
                # Not enough arguments
                error(procedure_type, "takes at least", min_name_count,
                      "arguments, got", arg_count)
                raise TypeError
            elif arg_count > max_name_count:
                # Too many arguments
                error(procedure_type, "takes at most", max_name_count,
                      "arguments, got", arg_count)
                raise TypeError
        elif isinstance(param_names, str):
            # Single name, bind entire arglist to it
            arglist_name = param_names
            if arglist_name in self.global_names:
                warn(procedure_type, "parameter name shadows global name",
                     arglist_name)
            if procedure_type == "function":
                # Repackage arglist into nested tuples and assign
                args = nil
                while arguments:
                    args = (arguments.pop(), args)
                namespace[arglist_name] = args
            elif procedure_type == "macro":
                # Quote arglist and assign
                namespace[arglist_name] = ("q", (arguments, ()))
            else:
                # Code should never get here
                raise NotImplemented("procedure_type should be either "
                                     "function or macro")
        else:
            error("parameters must either be name or list of names,",
                  "not", self.asl_type(param_names))
            raise TypeError

    def call(self, function, raw_args):
        """Perform a function call with a user-defined function."""
        try:
            param_names, body, arglist = self.call_data(function, raw_args)
        except TypeError:
            # There was a problem with the structure of the supposed
            # function (call_data already gave the error message)
            return nil
        with self.new_scope():
            # Loop while recursive calls are optimizable tail-calls
            while function is not None:
                # Bind arg values to param names in local scope
                try:
                    self.bind_params(param_names, arglist, self.local_names)
                except TypeError:
                    # There was a problem with binding the paramters
                    # (bind_params already gave the error message)
                    return nil
                # Eliminate any macros, ifs, and evals
                head = None
                tail = None
                if body and isinstance(body, tuple):
                    head = self.asl_eval(body[0])
                    tail = body[1]
                    try:
                        head, tail = self.resolve_macros(head, tail)
                    except TypeError:
                        # resolve_macros encountered an error condition
                        # (it already gave the error message)
                        return nil
                    if head is None:
                        # After resolving macros, the result was a
                        # simple value, not an s-expression
                        body = tail
                # Are we left with a tail call to a user-defined
                # function (either the same one or a different one)?
                if head and isinstance(head, tuple):
                    # If so, swap out the args from the original call
                    # for the updated args, the function for the new
                    # function (which might be the same function), and
                    # loop for the recursive call
                    function = head
                    raw_args = tail
                    try:
                        param_names, body, arglist = self.call_data(function,
                                                                    raw_args)
                    except TypeError:
                        # There was a problem with the structure of the
                        # supposed function (call_data already gave the
                        # error message)
                        return nil
                    # Clear the local scope to prepare for the next
                    # iteration
                    self.local_names.clear()
                else:
                    # Otherwise, eval the final expression, break out
                    # of the loop, and return it
                    return_val = self.asl_eval(body)
                    function = None
        return return_val

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
        is_udef_macro = self.is_macro(head)
        while head == self.asl_if or head == self.asl_eval or is_udef_macro:
            if head == self.asl_if:
                # The head is (some name for) asl_if
                # If needs exactly three arguments
                if raw_args and raw_args[1] and raw_args[1][1]:
                    if not raw_args[1][1][1]:
                        condition = self.asl_eval(raw_args[0])
                        if condition == 0 or condition == nil:
                            expression = raw_args[1][1][0]
                        else:
                            expression = raw_args[1][0]
                    else:
                        # TODO: exact numbers
                        error("too many arguments for if")
                        raise TypeError
                else:
                    error("not enough arguments for if")
                    raise TypeError
            elif head == self.asl_eval:
                # The head is (some name for) asl_eval
                # Eval needs exactly one argument
                if raw_args:
                    if not raw_args[1]:
                        expression = self.asl_eval(raw_args[0])
                    else:
                        # TODO: exact numbers
                        error("too many arguments for eval")
                        raise TypeError
                else:
                    error("not enough arguments for eval")
                    raise TypeError
            elif is_udef_macro:
                # The head is a list representing a user-defined macro
                macro_params = head[1][0]
                macro_body = head[1][1][0]
                macro_names = {}
                try:
                    self.bind_params(macro_params, raw_args, macro_names)
                except TypeError:
                    raise
                # Substitute the arguments for the parameter names in
                # the macro body expression
                expression = self.replace(macro_names, macro_body)
            if expression and isinstance(expression, tuple):
                # The result was a nonempty s-expression which could be
                # another macro invocation, so set up for another trip
                # through the loop
                head, raw_args = expression
                head = self.asl_eval(head)
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
        if (expression and isinstance(expression, tuple)
                and isinstance(expression[0], int) and expression[1]
                and expression[1][1] and not expression[1][1][1]):
            return True
        else:
            return False

    def replace(self, bindings, expression):
        """Replaces names in expression with their values from bindings.

Bindings is a dictionary; expression is any expression.
Names that aren't in bindings are left untouched.
"""
        if expression and isinstance(expression, tuple):
            # An s-expression
            head, tail = expression
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
        if not self.quiet:
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
        if isinstance(tail, tuple):
            return (head, tail)
        else:
            error("cannot cons to", self.asl_type(tail), "in Appleseed")
            return nil

    @function
    @params(1)
    def asl_head(self, lyst):
        if isinstance(lyst, tuple):
            if lyst == nil:
                return nil
            else:
                return lyst[0]
        else:
            error("cannot get head of", self.asl_type(lyst))
            return nil

    @function
    @params(1)
    def asl_tail(self, lyst):
        if isinstance(lyst, tuple):
            if lyst == nil:
                return nil
            else:
                return lyst[1]
        else:
            error("cannot get tail of", self.asl_type(lyst))
            return nil

    @function
    @params(2)
    def asl_add(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 + arg2
        else:
            error("cannot add", self.asl_type(arg1), "and",
                  self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_sub(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 - arg2
        else:
            error("cannot subtract", self.asl_type(arg1), "and",
                  self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_mul(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            return arg1 * arg2
        else:
            error("cannot multiply", self.asl_type(arg1), "and",
                  self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_div(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            if arg2 != 0:
                return arg1 // arg2
            else:
                error("division by zero")
                return nil
        else:
            error("cannot divide", self.asl_type(arg1), "and",
                  self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_mod(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int):
            if arg2 != 0:
                return arg1 % arg2
            else:
                error("mod by zero")
                return nil
        else:
            error("cannot mod", self.asl_type(arg1), "and",
                  self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_less(self, arg1, arg2):
        try:
            return int(arg1 < arg2)
        except TypeError:
            error("cannot use less? to compare", self.asl_type(arg1),
                  "and", self.asl_type(arg2))
            return nil

    @function
    @params(2)
    def asl_equal(self, arg1, arg2):
        return int(arg1 == arg2)

    @function
    @params(1)
    def asl_eval(self, code, top_level=False):
        if isinstance(code, tuple):
            if code == nil:
                # Nil evaluates to itself
                return nil
            # Otherwise, it's a function/macro call
            function = self.asl_eval(code[0])
            raw_args = code[1]
            # Eliminate any macro calls, including <if> and <eval>
            try:
                function, raw_args = self.resolve_macros(function, raw_args)
            except TypeError:
                # resolve_macros encountered an error condition (it
                # already gave the error message)
                return nil
            if function is None:
                # After resolving macros, the result was a simple
                # value, not an s-expression
                code = raw_args
            elif function and isinstance(function, tuple):
                # User-defined function or macro
                return self.call(function, raw_args)
            elif function in self.builtins:
                # Builtin function or macro
                if function.__name__ in top_level_only_fns and not top_level:
                    error("call to", function.__name__, "cannot be nested")
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
                    error(function.__name__, "takes", function.param_count,
                          "arguments, got", len(args))
                    return nil
            else:
                # Trying to call an int or unevaluated string
                error(function, "is not a function or macro")
                return nil
        if isinstance(code, int):
            # Integer literal
            return code
        elif isinstance(code, str):
            # Name; look up its value
            if code in self.local_names:
                return self.local_names[code]
            elif code in self.global_names:
                return self.global_names[code]
            else:
                error("referencing undefined name", code)
                return nil
        else:
            # Probably a builtin
            return code

    @function
    @params(1)
    def asl_type(self, value):
        if isinstance(value, int):
            return "Int"
        elif isinstance(value, str):
            return "String"
        elif isinstance(value, tuple):
            return "List"
        else:
            return "Builtin"

    @function
    @params(2)
    def asl_debug(self, output, expression):
        if output is not None:
            print(self.asl_repr(output), file=sys.stderr)
        return expression

    @function
    @params(1)
    def asl_repr(self, value):
        if value == nil:
            result = "()"
        elif isinstance(value, tuple):
            # List (as nested tuple)
            result = "("
            beginning = True
            for item in cons_iter(value):
                if beginning:
                    beginning = False
                else:
                    result += " "
                result += self.asl_repr(item)
            result += ")"
        elif value in self.builtins:
            # One of the builtin functions or macros
            result = ("<builtin %s %s>"
                      % ("macro" if value.is_macro else "function",
                         value.__name__))
        elif isinstance(value, str):
            # String
            if any(c in value for c in WHITESPACE + SYMBOLS):
                result = '"' + value + '"'
            else:
                result = value
        else:
            # Integer
            result = str(value)
        return result
    
    @function
    @params(1)
    def asl_str(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int):
            # TBD: chr(value) instead?
            return str(value)
        elif isinstance(value, tuple):
            result = ""
            for char_code in cons_iter(value):
                if isinstance(char_code, int):
                    try:
                        result += chr(char_code)
                    except ValueError:
                        # Can't convert this number to a character
                        warn("cannot convert", char_code, "to character")
                        pass
                else:
                    error("argument of str must be list of Ints, not of",
                          self.asl_type(char_code))
                    return nil
            return result
        else:
            # Builtin
            return value.__name__

    @function
    @params(1)
    def asl_chars(self, value):
        if isinstance(value, str):
            result = nil
            for char in reversed(value):
                result = (ord(char), result)
            return result
        else:
            error("argument of chars must be String, not",
                  self.asl_type(value))
            return nil

    @macro
    @params(2)
    def asl_def(self, name, value):
        if isinstance(name, str):
            if name in self.global_names:
                error("name", name, "already in use")
                return nil
            else:
                self.global_names[name] = self.asl_eval(value)
                return name
        else:
            error("cannot define", asl_type(name))
            return nil

    @macro
    @params(3)
    def asl_if(self, cond, trueval, falseval):
        # Arguments are not pre-evaluated, so cond needs to be evaluated
        # here
        cond = self.asl_eval(cond)
        if cond == 0 or cond == nil:
            return self.asl_eval(falseval)
        else:
            return self.asl_eval(trueval)

    @macro
    @params(1)
    def asl_quote(self, quoted):
        return quoted

    @macro
    @params(1)
    def asl_load(self, module):
        if not module.endswith(".asl"):
            module += ".asl"
        abspath = os.path.abspath(os.path.join(self.module_paths[-1], module))
        module_directory, module_name = os.path.split(abspath)
        if abspath not in self.modules:
            # Module has not already been loaded
            try:
                with open(abspath) as f:
                    module_code = f.read()
            except (FileNotFoundError, IOError):
                error("could not load", module_name, "from", module_directory)
            else:
                # Add the module to the list of loaded modules
                self.modules.append(abspath)
                # Push the module's directory to the stack of module
                # directories--this allows relative paths in load calls
                # from within the module
                self.module_paths.append(module_directory)
                # Execute the module code
                self.execute(module_code)
                # Put everything back the way it was before loading
                self.module_paths.pop()
                self.inform("Loaded", module)
        else:
            self.inform("Already loaded", module)
        return None

    @macro
    @params(0)
    def asl_help(self):
        self.inform(help_text)
        return None

    @macro
    @params(0)
    def asl_restart(self):
        self.__init__(repl=self.repl)
        self.inform("Restarting...")
        return None

    @macro
    @params(0)
    def asl_quit(self):
        raise UserQuit

    @property
    def quiet(self):
        # True (suppress output) while in process of loading modules
        return len(self.module_paths) > 1


def run_file(filename, environment=None):
    if environment is None:
        environment = Program(repl=False)
    try:
        with open(filename) as f:
            code = f.read()
    except FileNotFoundError:
        error("could not find", filename)
    except IOError:
        error("could not read", filename)
    else:
        try:
            environment.execute(code)
        except UserQuit:
            pass


def repl(environment=None):
    print("Appleseed", VERSION)
    print("Type (help) for information")
    if environment is None:
        environment = Program(repl=True)
    instruction = input_instruction()
    while True:
        try:
            last_value = environment.execute(instruction)
            environment.global_names["_"] = last_value
        except KeyboardInterrupt:
            error("calculation interrupted by user.")
        except RecursionError:
            error("recursion depth exceeded. How could you forget "
                  "to use tail calls?!")
        except UserQuit:
            break
        except Exception as err:
            error(err)
            break
        instruction = input_instruction()
    print("Bye!")


def input_instruction():
    try:
        instruction = input("asl> ")
    except (EOFError, KeyboardInterrupt):
        instruction = "(quit)"
    return instruction


help_text = """
Enter expressions at the prompt.

- Any run of digits (with optional minus sign) is an integer literal.
- () is the empty list, nil.
- Anything in "double quotes" is a string literal.
- A series of expressions enclosed in parentheses is a function call.
- Anything else is a name, which returns the value bound to it or
  errors if it is unbound; if quoted with q, it is treated as a string.

Builtin functions and macros:

- cons[truct list]. Takes a value and a list and returns a new list
     obtained by placing the value at the front of the list.
- head (car, in Lisp terminology). Takes a list and returns the first
     item in it, or nil if given nil.
- tail (cdr, in Lisp terminology). Takes a list and returns a new
     list containing all but the first item, or nil if given nil.
- add, sub, mul, div, mod. Each takes two integers and performs the
     appropriate mathematical operation on them. Note that div is
     integer division.
- less?. Takes two integers, strings, or lists; returns 1 if the first
     is less than the second, 0 otherwise.
- equal?. Takes two values; returns 1 if the two are identical, 0
     otherwise.
- str. Takes a list of integers representing character codes and
     converts it to a string.
- chars. Takes a string and converts it to a list of integers
     representing character codes.
- repr. Takes a value and returns a string representing that value;
     e.g. (repr (cons 1 (q (a)))) => "(1 a)".
- type. Takes a value and returns its type, one of Int, String, List,
     or Builtin.
- eval. Takes a value, representing an expression, and evaluates it.
- q[uote] (macro). Takes an expression and returns it unevaluated.
- if (macro). Takes a condition value, an if-true expression, and an
     if-false expression. If the condition value evaluates to 0 or nil,
     evaluates and returns the if-false expression. Otherwise,
     evaluates and returns the if-true expression.
- def (macro). Takes a name and an expression. Evaluates the
     expression and binds it to the name at global scope, then returns
     the name. A name cannot be redefined once it has been defined.
- load (macro). Takes a filename and evaluates that file as code.
- debug. Takes a debug message and an expression. Writes the debug
     message to stderr, then evaluates and returns the expression.

You can create your own functions and macros. (A macro doesn't evaluate
its arguments; it substitutes them wherever their names appear in its
expression and evaluates the result in the calling context.)

- To create a function, construct a list of two items. The first item
  should be a list of parameter names. Alternately, it can be a single
  name, in which case it will receive a list of all arguments. The
  second item should be the return expression.
- To create a macro, proceed as with a function, but add an integer
  (by convention, 0) at the beginning of the list.

Use (load library) to access the standard library. It includes
convenience functions and macros (list, lambda, etc.), list
manipulation, metafunctions, integer arithmetic, string operations,
and more.

Special features in the interactive prompt:

- The name _ is bound to the value of the last evaluated expression.
- (restart) clears all user-defined names, starting over from scratch.
- (help) displays this help text.
- (quit) ends the session.
"""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User specified one or more files--run them
        environment = Program()
        for filename in sys.argv[1:]:
            run_file(filename, environment)
    else:
        # No filename specified, so...
        repl()
