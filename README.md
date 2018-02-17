# Appleseed

Appleseed is a minimalist, purely functional, highly extensible Lisp dialect. From a small core of builtins, it leverages the power of Lisp to grow a full-featured standard library. It is a successor to the earlier, simpler language [tinylisp](https://github.com/dloscutoff/Esolangs/tree/master/tinylisp).

## Features

Appleseed is currently very much under construction, but the following features either exist in the language or are planned:

- A simple yet powerful macro system that allows for defining new syntactic constructs.
- [Tail-call optimization](https://en.wikipedia.org/wiki/Tail_call)--including [modulo cons](https://en.wikipedia.org/wiki/Tail_call#Tail_recursion_modulo_cons)--allowing unlimited recursion depth for properly written functions.
- [Lazy evaluation](https://en.wikipedia.org/wiki/Lazy_evaluation) of lists.
- Lexical scope and [closures](https://en.wikipedia.org/wiki/Closure_(computer_programming)).
- Extensions that allow for non-functional behaviors like I/O and randomness.
- A fully extensible type system.
- Exception handling.

## Running Appleseed

There are two ways of running Appleseed: from a file, or from the interactive REPL prompt.

- To run code from one or more files, pass the filenames as command-line arguments to the interpreter: `./appleseed.py file1.asl file2.asl`.
- To run code from the interactive prompt, run the interpreter without command-line arguments.

Helpful commands when using the REPL:

- `(help)` displays a help document.
- `(restart)` clears all user-defined names, starting over from scratch.
- `(quit)` ends the session.
