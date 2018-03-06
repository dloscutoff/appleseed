# Appleseed

Appleseed is a purely functional, highly extensible Lisp dialect. From a small core of builtins, it leverages the power of Lisp to grow a full-featured standard library. It is a successor to the earlier, simpler language [tinylisp](https://github.com/dloscutoff/Esolangs/tree/master/tinylisp).

## Features

Appleseed is still very much under construction. The following features have been implemented:

- A simple yet powerful macro system that allows for defining new syntactic constructs.
- [Tail-call optimization](https://en.wikipedia.org/wiki/Tail_call)--including [modulo cons](https://en.wikipedia.org/wiki/Tail_call#Tail_recursion_modulo_cons)--allowing unlimited recursion depth for properly written functions.
- [Lazy evaluation](https://en.wikipedia.org/wiki/Lazy_evaluation) of lists.
- An events system that allows for non-functional behaviors like I/O and randomness (currently in the beginning stages).

The following features are planned:

- Lexical scope and [closures](https://en.wikipedia.org/wiki/Closure_(computer_programming)).
- A fully extensible type system.
- Exception handling.

## Running Appleseed

The quickest way to run Appleseed code is at [Try It Online](https://tio.run/##DcjBDYAgDAXQu1MUTjRxEDfwXNNvYlKBQOP6lXd80rthAhpRFDdNl@FpIyom76VCBR@q85p1fTzVE@UDZm2nsw3TlJk54gc), provided by [Dennis](https://github.com/DennisMitchell).

If you `git clone` Appleseed to your computer (note: requires [Python 3](https://www.python.org/downloads/)), you have two options: run a file, or use the interactive REPL prompt.

- To run code from a file, pass the filename as a command-line argument to the interpreter: `./appleseed file.asl` (Linux) or `appleseed.py file.asl` (Windows).
- To run code from the interactive prompt, run the interpreter without command-line arguments.

Helpful commands when using the REPL:

- `(help)` displays a help document.
- `(restart)` clears all user-defined names, starting over from scratch.
- `(quit)` ends the session.
