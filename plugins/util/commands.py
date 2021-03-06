from exceptions import *
from commands import *


class ChatCommands:
    def __init__(self, commands):
        self.commands = commands

    def add(self, *args, **kwargs):
        self.commands[args[0]] = Command(*args, **kwargs)

    def run(self, name, *args):
        name = name.lower()
        if name in self.commands:
            self.commands[name].run(*args)
        else:
            raise CommandDoesNotExist(name)


class Command:
    def __init__(self, *args, **kwargs):
        self.name = args[0]
        self.function = args[1]
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def run(self, caller_name, arg, state):
        caller = state["players"][caller_name]
        if caller.role != "Admin" and self.requires_admin:
            raise UserDoesNotHavePermissions(self.name, caller)
        else:
            args = [state, caller_name]
            if self.has_arg == True:
                if arg == None:
                    raise ExpectedArg(self.name)
                else:
                    args.append(arg)
            self.function(*args)
