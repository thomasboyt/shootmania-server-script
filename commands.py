from command_helpers import ChatCommands

chat_commands = ChatCommands()


def nextmap(server, caller):
    nextmap = server.GetNextMapInfo()['name']
    server.ChatSendServerMessageToLogin("Next map " + nextmap, caller)

chat_commands.add("nextmap", nextmap, requires_admin=False, has_arg=False)


def skip(server, state, caller):
    server.NextMap()

chat_commands.add('skip', skip, requires_admin=True, has_arg=False)


def kick(server, state, caller, target):
    if target in state['players']:
        msg = "%s (%s) was kicked by %s" % (state['players'][target].nick,
            target, caller)
        server.ChatSendServerMessage(msg)
        server.Kick(target)
    else:
        # some day will add support for kicking nicks
        server.ChatSendServerMessageToLogin("Name not found", caller)

chat_commands.add('kick', kick, requires_admin=True, has_arg=True)


def echo(server, state, caller, message):
    server.ChatSendServerMessage(message)

chat_commands.add('echo', echo, requires_admin=True, has_arg=True)


def setservername(server, state, caller, name):
    server.SetServerName(name)
    server.ChatSendServerMessage("Server renamed to " + name)

chat_commands.add('setservername', setservername, requires_admin=True,
    has_arg=True)


def setpassword(server, state, caller, password):
    server.SetServerPassword(password)
    server.SetServerPasswordForSpectator(password)
    server.ChatSendServerMessage("Set password")

chat_commands.add('setpassword', setpassword, requires_admin=True, has_arg=True)


def clearpassword(server, state, caller):
    server.SetServerPassword(" ")
    server.SetServerPasswordForSpectator(" ")
    server.ChatSendServerMessage("Cleared password")

chat_commands.add('clearpassword', clearpassword, requires_admin=True,
    has_arg=False)
