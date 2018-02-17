
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


# Exception that is raised by the (quit) macro

class UserQuit(BaseException):
    pass

