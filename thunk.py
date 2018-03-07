
from cfg import nil, identical


class Thunk:
    """For delayed evaluation of function calls."""
    def __init__(self, environment, param_names, body, arglist):
        self.environment = environment
        self.param_names = param_names
        self.body = body
        self.arglist = arglist
        self.resolved = None

    def __eq__(self, value):
        return (isinstance(value, Thunk)
                and identical(self.environment, value.environment)
                and self.param_names == value.param_names
                and identical(self.body, value.body)
                and identical(self.arglist, value.arglist))

    def __str__(self):
        return "Thunk(%s, %s, %s)" % (self.body, self.param_names,
                                      self.arglist)

    def __repr__(self):
        return str(self)
    
    def resolve(self):
        """Perform a tail-recursive function call.

Tail-recursion can include if, eval, macros, and cons. If the result
after eliminating if, eval, and macros is another thunk, the caller
is expected to resolve it (so that resolution uses a loop, not
recursion). If there are non-tail-recursive nested calls, they are
fully resolved.
"""
        if self.resolved is not None:
            return self.resolved
        body = self.body
        with self.environment.new_scope() as local_names:
            # Bind arg values to param names in the new local scope
            try:
                self.environment.bind_params(self.param_names,
                                             self.arglist,
                                             local_names)
            except TypeError:
                # There was a problem with binding the parameters
                # (bind_params already gave the error message)
                return nil
            # Eliminate any macros, ifs, and evals
            head = None
            tail = None
            if body and isinstance(body, tuple):
                head = self.environment.asl_eval(body[0])
                tail = body[1]
                try:
                    head, tail = self.environment.resolve_macros(head, tail)
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
                # If so, calculate updated param names, function body,
                # and arglist, and return a new Thunk (to be resolved
                # in the calling context)
                function = head
                raw_args = tail
                try:
                    call_data = self.environment.call_data(function, raw_args)
                except TypeError:
                    # There was a problem with the structure of the
                    # supposed function (call_data already gave the
                    # error message)
                    return nil
                else:
                    return_val = Thunk(self.environment, *call_data)
            else:
                # Otherwise, just eval the final expression
                return_val = self.environment.asl_eval(body)
        self.resolved = return_val
        return return_val


def resolve_thunks(value):
    while isinstance(value, Thunk):
        value = value.resolve()
    return value


def cons_iter(nested_tuple):
    """Iterate over a cons chain of nested tuples."""
    nested_tuple = resolve_thunks(nested_tuple)
    while nested_tuple:
        yield nested_tuple[0]
        nested_tuple = resolve_thunks(nested_tuple[1])

