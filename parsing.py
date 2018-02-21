
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
                cfg.warn("unterminated backtick-enclosed token")
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
                    cfg.warn("unterminated string literal")
                    yield code[a:i] + cfg.STRING_DELIMITER
                    i -= 1
                    break
                elif code[i] == cfg.STRING_ESCAPE_CHAR:
                    if code[i+1] == "\n":
                        cfg.warn("unterminated string literal")
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
    """Take a series of expressions, yield a series of parse trees.

The code can be a string or an iterator that yields tokens.
Each resulting parse tree is an Appleseed list (i.e. nested tuples).
"""
    if isinstance(code, str):
        # If we're given a raw codestring, scan it before parsing
        code = scan(code)
    try:
        while True:
            token = next(code)
            if token == "(":
                # After an opening parenthesis, parse expressions until
                # the matching closing parenthesis and yield the
                # resulting nested-tuple list
                yield parse_expressions(code)
            elif token == cfg.BLOCK_COMMENT_OPEN:
                # After a block comment opener, parse expressions until
                # the matching closing parenthesis and discard
                parse_expressions(code)
            elif token == ")":
                cfg.warn("unmatched closing parenthesis")
            else:
                yield parse_name_or_literal(token)
    except StopIteration:
        # Everything has been parsed
        pass
    

def parse_expressions(code):
    """Take a token iterator and parse expressions from it until ).

This function assumes we're parsing an s-expression and that the
opening parenthesis has already been processed. So we parse the items
or [sub]expressions in the s-expr one after the other, turning them
into a cons list of nested tuples. When we go to parse another item
and we find a closing parenthesis, we've hit the end of the s-expr, so
we return nil.
"""
    try:
        token = next(code)
    except StopIteration:
        # If the s-expression is unfinished and we've run out of tokens,
        # supply the missing close-paren
        # TODO: some kind of warning about implicit close-parens
        token = ")"
    if token == ")":
        return cfg.nil
    elif token == "(":
        # The subexpression is itself a list
        expr = parse_expressions(code)
    elif token == cfg.BLOCK_COMMENT_OPEN:
        rest_of_comment = parse_expressions(code)
        return parse_expressions(code)
    else:
        expr = parse_name_or_literal(token)
    return (expr, parse_expressions(code))


def parse_name_or_literal(token):
    if token.startswith(cfg.STRING_DELIMITER):
        # Literal strings are auto-quoted String tokens
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
        return ("q", (string, ()))
    if token.startswith(cfg.TOKEN_DELIMITER):
        # `Extended `` token`
        token = token[1:-1]
        token = token.replace(cfg.TOKEN_DELIMITER * 2, cfg.TOKEN_DELIMITER)
    if token.isdigit() or token.startswith("-") and token[1:].isdigit():
        # Integer literal
        return int(token)
    else:
        # If it's not any kind of recognized literal, it's a name
        return token

