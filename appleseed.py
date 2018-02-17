#!/usr/bin/env python3

import sys
import os

import run


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User specified a filename--run it
        run.run_file(sys.argv[1])
    elif sys.stdin.isatty():
        # No filename specified, and the input is coming from a terminal
        run.repl()
    else:
        # No filename specified, but input is piped in from a file or
        # another process
        code = sys.stdin.read()
        # Reset stdin so the program can take user input
        if os.name == "posix":
            try:
                sys.stdin = open("/dev/tty", "r")
            except OSError:
                # This system doesn't have a terminal; we just leave
                # stdin alone and let any user input actions in the
                # program fail
                # TODO: more graceful ways to handle this?
                pass
        elif os.name == "nt":
            try:
                sys.stdin = open("CON", "r")
            except OSError:
                pass
        run.run_program(code)
