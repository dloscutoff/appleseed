
import cfg
import version
import builtin_events
from execution import Program


def run_file(filename, environment=None):
    if environment is None:
        environment = Program(repl=False)
    try:
        with open(filename) as f:
            code = f.read()
    except FileNotFoundError:
        cfg.error("could not find", filename)
        return
    except PermissionError:
        cfg.error("insufficient permissions to read", filename)
        return
    except IOError:
        cfg.error("could not read", filename)
        return
    # If file read was successful, execute the code
    run_program(code, environment)


def run_program(code, environment=None):
    if environment is None:
        environment = Program(repl=False)
    try:
        environment.execute(code)
    except cfg.UserQuit:
        # Encountered (quit) in one of the files
        return
    except KeyboardInterrupt:
        cfg.error("calculation interrupted by user.")
        return
    except RecursionError:
        cfg.error("recursion depth exceeded.",
                  "How could you forget to use tail calls?!")
        return
    except Exception as err:
        # Miscellaneous exception, probably indicates a bug in
        # the interpreter
        cfg.error(err)
        return
    # If code execution was successful, begin event loop
    builtin_events.event_loop(environment)


def repl(environment=None):
    print("Appleseed", version.VERSION)
    print("Type (help) for information")
    if environment is None:
        environment = Program(repl=True, max_list_items=20)
    instruction = input_instruction()
    while True:
        try:
            last_value = environment.execute(instruction)
            environment.global_names["_"] = last_value
        except KeyboardInterrupt:
            cfg.error("calculation interrupted by user.")
        except RecursionError:
            cfg.error("recursion depth exceeded.",
                      "How could you forget to use tail calls?!")
        except cfg.UserQuit:
            break
        except Exception as err:
            # Miscellaneous exception, probably indicates a bug in
            # the interpreter
            cfg.error(err)
            break
        instruction = input_instruction()
    print("Bye!")


def input_instruction():
    try:
        instruction = input(cfg.PROMPT)
    except (EOFError, KeyboardInterrupt):
        instruction = "(quit)"
    return instruction

