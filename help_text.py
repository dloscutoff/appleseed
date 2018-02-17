

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
- To create a macro, proceed as with a function, but add the number 0
  at the beginning of the list.

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

