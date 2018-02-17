
import cfg


def scan(code):
    """Take a string and yield a series of tokens."""
    # Add a newline to the end to allow peeking at the next character
    # without requiring a check for end-of-string
    code += "\n"
    i = 0
    while i < len(code):
        char = code[i]
        if char in cfg.WHITESPACE:
            # Whitespace--ignore
            pass
        elif char == cfg.LINE_COMMENT_CHAR:
            # Start of a comment--scan till newline
            while code[i+1] != "\n":
                i += 1
        elif code[i:i+2] == cfg.BLOCK_COMMENT_OPEN:
            # Start of a block comment--this will be handled by the
            # parser
            yield code[i:i+2]
            i += 1
        elif char in cfg.SYMBOLS:
            # Reserved symbol
            yield char
        elif char == cfg.TOKEN_DELIMITER:
            # Start of an extended token--scan till the end of it
            # An extended token looks like:
            #  `chars ``and`` backtick pairs`
            # which represents this token:
            #  chars `and` backtick pairs
            # which is a name. Extended tokens allow the inclusion of
            # special characters such as ( )"; in tokens
            # TBD: how should a token be displayed that contains
            # literal newlines?
            a = i
            try:
                while code[i] == cfg.TOKEN_DELIMITER:
                    while code[i+1] != cfg.TOKEN_DELIMITER:
                        i += 1
                    i += 2
            except IndexError:
                # code[i+1] is past the end of the token; in this
                # case, code[i] is the final newline, so yield
                # everything but the newline, with a supplied
                # closing delimiter, as the extended token
                warn("unterminated backtick-enclosed token")
                yield code[a:i] + cfg.TOKEN_DELIMITER
            else:
                # For properly terminated extended tokens, the while
                # loop takes us past the closing delimiter, so
                # back up a notch and then yield the token
                i -= 1
                yield code[a:i+1]
        elif char == cfg.STRING_DELIMITER:
            # Start of a literal string--scan till the end of it
            # A literal string looks like:
            #  "chars \"and\" escapes"
            # which represents this string:
            #  chars "and" escapes
            # This will be parsed as a (possibly extended) token,
            # quoted with q.
            a = i
            i += 1
            while code[i] != cfg.STRING_DELIMITER:
                if code[i] == "\n":
                    warn("unterminated string literal")
                    yield code[a:i] + cfg.STRING_DELIMITER
                    i -= 1
                    break
                elif code[i] == cfg.STRING_ESCAPE_CHAR:
                    if code[i+1] == "\n":
                        warn("unterminated string literal")
                        yield (code[a:i+1]
                               + cfg.STRING_ESCAPE_CHAR
                               + cfg.STRING_DELIMITER)
                        break
                    else:
                        # Include the whole escape sequence together
                        i += 2
                else:
                    # Include a single character
                    i += 1
            else:
                yield code[a:i+1]
        else:
            # Start of a regular, non-extended token (name or literal)
            # Scan till the end of it
            a = i
            while code[i+1] not in cfg.SPECIAL_CHARS:
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
        elif token == cfg.BLOCK_COMMENT_OPEN:
            rest_of_comment = parse(code)
            return parse(code)
        elif token == ")":
            return ()
        elif token.startswith(cfg.TOKEN_DELIMITER):
            # Extended token
            # Strip the delimiters from the outside
            element = token[1:-1]
            # Replace the doubled-delimiter escape sequences
            element = element.replace(cfg.TOKEN_DELIMITER * 2,
                                      cfg.TOKEN_DELIMITER)
        elif token.startswith(cfg.STRING_DELIMITER):
            # Literal strings are auto-quoted tokens
            # Strip the delimiters from the outside
            token = token[1:-1]
            # Replace the escape sequences
            i = 0
            string = ""
            while i < len(token):
                if token[i] == cfg.STRING_ESCAPE_CHAR:
                    i += 1
                    if token[i] in [cfg.STRING_ESCAPE_CHAR,
                                    cfg.STRING_DELIMITER]:
                        string += token[i]
                    elif token[i] == "n":
                        string += "\n"
                    elif token[i] == "t":
                        string += "\t"
                    else:
                        string += cfg.STRING_ESCAPE_CHAR + token[i]
                else:
                    string += token[i]
                i += 1
            element = ("q", (string, ()))
        else:
            element = token
        return (element, parse(code))

