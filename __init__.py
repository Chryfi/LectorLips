import sys
import traceback
from commands import InvalidCommandArguments, InvalidCommand, CommandException, commands

__author__ = "Christian F. (known as Chryfi)"
__copyright__ = "Copyright 2022, LectorLips"
__credits__ = ["Christian F. (known as Chryfi)", "Florian Torgau"]
__maintainer__ = "Christian F. (known as Chryfi)"
__status__ = "Release"
__version__ = "1.1"

if __name__ == "__main__":
    if len(sys.argv) > 0:
        commandClass = None

        try:
            sys.argv.pop(0)

            if len(sys.argv) == 0 or (len(sys.argv) > 0 and commands.get(sys.argv[0]) is None):
                raise InvalidCommand("No existing command was provided. Type in -help for a list of commands")

            commandClass = commands.get(sys.argv[0])

            sys.argv.pop(0)

            command = commandClass(sys.argv)

            command.execute()
        except Exception as e:
            if "-debug" in sys.argv:
                print(traceback.format_exc())

            print(e)

            if isinstance(e, InvalidCommandArguments) and commandClass is not None:
                print("\n")
                print(commandClass.get_documentation())
            elif not isinstance(e, InvalidCommand) and not isinstance(e, CommandException) and not "-debug" in sys.argv:
                print("\nType in -debug for the stacktrace.")

            quit(1)

        quit(0)