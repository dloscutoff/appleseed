
import sys

# Scanning/parsing related constants
WHITESPACE = " \t\n\r"
SYMBOLS = "()"
LINE_COMMENT_CHAR = ";"
BLOCK_COMMENT_OPEN = "(;"
TOKEN_DELIMITER = "`"
STRING_DELIMITER = '"'
STRING_ESCAPE_CHAR = "\\"
SPECIAL_CHARS = (WHITESPACE + SYMBOLS + LINE_COMMENT_CHAR
                 + TOKEN_DELIMITER + STRING_DELIMITER)

# Repl prompt string
PROMPT = "asl> "

# The empty tuple represents the empty list, nil
nil = ()


# Shortcut functions for print without newline and print to stderr
def write(*args):
    print(*args, end="")


def error(*args):
    print("Error:", *args, file=sys.stderr)


def warn(*args):
    print("Warning:", *args, file=sys.stderr)


def interrupted_error():
    error("calculation interrupted by user.")


def recursion_error():
    error("recursion depth exceeded. How could you forget to use tail calls?!")


# Exception that is raised by the (quit) macro

class UserQuit(BaseException):
    pass


def identical(value1, value2):
    while isinstance(value1, tuple) and isinstance(value2, tuple):
        if value1 == value2 == ():
            return True
        elif value1 == () or value2 == ():
            return False
        else:
            if identical(value1[0], value2[0]):
                value1 = value1[1]
                value2 = value2[1]
            else:
                return False
    if isinstance(value1, list) and isinstance(value2, list):
        return all(map(identical, value1, value2))
    else:
        return value1 == value2 and type(value1) == type(value2)
