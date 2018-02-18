
from cfg import nil
import cfg
import thunk
import sys

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
        action_name = action["name"]
        # TODO: change these from an if statement to a list of
        # actions that can be augmented by extension code
        if action_name == "write!":
            if "value" in action:
                asl_write(action["value"])
        elif action_name == "error-write!":
            if "value" in action:
                asl_write(action["value"], err=True)
        elif action_name == "print!":
            if "value" in action:
                asl_write(action["value"])
                print()
        elif action_name == "ask-line!":
            if "prompt" in action:
                asl_write(action["prompt"])
            action_results.append({"type": "Event",
                                   "name": "receive-line!",
                                   "line": input()})
        elif action_name == "exit!":
            exit_code = 0 if "exit-code" not in action else action["exit-code"]
            exit(exit_code)

    # Any other type should generate a warning, probably--TODO
    return action_results


def asl_write(value, err=False):
    write = cfg.write if not err else sys.stderr.write
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
            asl_write(item)
        write(")")
    elif isinstance(value, int):
        # Integer
        write(value)
    elif isinstance(value, str):
        # String
        write(value)
    elif isinstance(value, dict):
        # Object
        write("{")
        if "type" in value:
            write("(type ")
            asl_write(value["type"])
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
                asl_write(property_name)
                write(" ")
                asl_write(property_value)
                write(")")
        write("}")
    elif hasattr(value, "is_macro"):
        # One of the builtin functions or macros
        write("<builtin %s %s>"
                  % ("macro" if value.is_macro else "function",
                     builtins[value.name]))
    else:
        # Code should never get here
        raise NotImplementedError("unknown type in asl_write")
