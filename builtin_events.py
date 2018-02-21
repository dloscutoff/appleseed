
import sys

from cfg import nil
import cfg
import execution
import thunk

builtin_event_names = ["start!", "receive-line!"]


def event_loop(environment):
    # Go through the events we might have, and link them with their
    # event handler functions (whichever ones have had handlers defined)
    event_names = builtin_event_names
    for extension in environment.extensions:
        event_names += extension.event_names
    event_handlers = {}
    for event_name in event_names:
        if event_name in environment.global_names:
            event_handlers[event_name] = environment.global_names[event_name]
    # Fire the start! event to kick things off
    # TODO: use an actual queue type for event_queue instead of a list?
    event_queue = [{"type": "Event", "name": "start!"}]
    while event_queue:
        event = event_queue.pop(0)
        if event["name"] in event_handlers:
            action = environment.call(event_handlers[event["name"]],
                                      (event, nil))
            action_results = perform_action(action)
            # The action may have resulted in the firing of one or more
            # new events
            event_queue.extend(action_results)


def perform_action(action):
    action = thunk.resolve_thunks(action)
    action_results = []
    if isinstance(action, tuple):
        # List of actions
        for subaction in thunk.cons_iter(action):
            action_results.extend(perform_action(subaction))
    elif isinstance(action, dict) and "name" in action:
        # Single action
        action_func = builtin_actions.get(action["name"])
        if action_func is not None:
            result = action_func(action)
            if result is not None:
                action_results.append(result)
        else:
            cfg.warn("unknown action:", action["name"])
    # Any other type should generate a warning, probably--TODO
    return action_results


def act_print(action):
    if "value" in action:
        asl_print(action["value"])


def act_print_error(action):
    if "value" in action:
        asl_print(action["value"], error=True)


def act_write(action):
    if "value" in action:
        asl_print(action["value"], newline=False)


def act_write_error(action):
    if "value" in action:
        asl_print(action["value"], newline=False, error=True)


def act_ask_line(action):
    if "prompt" in action:
        asl_print(action["prompt"], newline=False)
    try:
        input_line = input()
    except EOFError:
        input_line = nil
    # Generate a receive-line! event
    return {"type": "Event",
            "name": "receive-line!",
            "line": input_line}


def act_exit(action):
    exit_code = action.get("exit-code", 0)
    # TODO: error handling if exit-code isn't an integer
    exit(exit_code)


builtin_actions = {"print!": act_print,
                   "print-error!": act_print_error,
                   "write!": act_write,
                   "write-error!": act_write_error,
                   "ask-line!": act_ask_line,
                   "exit!": act_exit,
                   }


def asl_print(value, newline=True, error=False):
    """Print an Appleseed value.

Note: this function will print infinite lists infinitely, giving output
until the program is stopped.
Keyword arguments:
- newline: print with a final newline (default True)
- error: print to stderr instead of stdout (default False)
"""
    if error:
        def write(string):
            print(string, end="", file=sys.stderr)
    else:
        def write(string):
            print(string, end="")
    value = thunk.resolve_thunks(value)
    if value == nil:
        write("()")
    elif isinstance(value, tuple):
        # List (as nested tuple)
        write("(")
        beginning = True
        for index, item in enumerate(thunk.cons_iter(value)):
            if beginning:
                beginning = False
            else:
                write(" ")
            asl_print(item, newline=newline, error=error)
        write(")")
    elif isinstance(value, bool):
        write("true" if value else "false")
    elif (isinstance(value, int) or isinstance(value, str)):
        write(value)
    elif isinstance(value, dict):
        # Object
        write("{")
        if "type" in value:
            write("(type ")
            asl_print(value["type"], newline=newline, error=error)
            write(")")
            beginning = False
        else:
            beginning = True
        for property_name, property_value in value.items():
            if property_name != "type":
                if beginning:
                    beginning = False
                else:
                    write(" ")
                write("(")
                asl_print(property_name, newline=newline, error=error)
                write(" ")
                asl_print(property_value, newline=newline, error=error)
                write(")")
        write("}")
    elif hasattr(value, "is_macro"):
        # One of the builtin functions or macros
        write("<builtin %s %s>"
                  % ("macro" if value.is_macro else "function",
                     execution.builtins[value.name]))
    else:
        # Code should never get here
        raise NotImplementedError("unknown type in asl_print")
    if newline:
        write("\n")

