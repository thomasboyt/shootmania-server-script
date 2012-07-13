class CommandDoesNotExist(Exception):
    def __init__(self, command):
        self.command = command


class UserDoesNotHavePermissions(Exception):
    def __init__(self, command, user):
        self.command = command
        self.user = user


class ExpectedArg(Exception):
    def __init(self, command):
        self.command = command


class ChatCommands:
    def __init__(self):
        self.commands = {}

    def add(self, *args, **kwargs):
        self.commands[args[0]] = Command(*args, **kwargs)

    def run(self, name, caller_name, arg, server, state):
        if name in self.commands:
            self.commands[name].run(caller_name, arg, server, state)
        else:
            raise CommandDoesNotExist(name)


class Command:
    def __init__(self, *args, **kwargs):
        self.name = args[0]
        self.function = args[1]
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def run(self, caller_name, arg, server, state):
        caller = state["players"][caller_name]
        if caller.role != "Admin" and self.requires_admin:
            raise UserDoesNotHavePermissions(self.name, caller)
        else:
            args = [server, state, caller_name]
            if self.has_arg == True:
                if arg == None:
                    raise ExpectedArg(self.name)
                else:
                    args.append(arg)
            self.function(*args)
