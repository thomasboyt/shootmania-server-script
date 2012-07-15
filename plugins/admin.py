from util.commands import *
from util.helpers import *

commands = []


def skip(server, state, caller):
    server.ChatSendServerMessage("Notice: %s ended map" % (caller))
    server.NextMap()

commands.append(
    Command('skip', skip, requires_admin=True, has_arg=False))


def changemap(server, state, caller, name):
    try:
        new_map = find_map(name, state["maps"])
        server.ChooseNextMap(new_map.file_name)
        server.ChatSendServerMessage("Notice: %s changed map to %s" %
            (caller, new_map.map_name))
        server.NextMap()
    except MapNotFound:
        server.ChatSendServerMessageToLogin("No map found matching: "
            + name, caller)

commands.append(
    Command("changemap", changemap, requires_admin=True, has_arg=True))


def echo(server, state, caller, message):
    server.ChatSendServerMessage("[Server] " + message)

commands.append(
    Command('echo', echo, requires_admin=True, has_arg=True))


def kick(server, state, caller, target):
    if target in state['players']:
        msg = "%s (%s) was kicked by %s" % (state['players'][target].nick,
            target, caller)
        server.ChatSendServerMessage(msg)
        server.Kick(target)
    else:
        # some day will add support for kicking nicks
        server.ChatSendServerMessageToLogin("Name not found", caller)

commands.append(
    Command('kick', kick, requires_admin=True, has_arg=True))


def setservername(server, state, caller, name):
    server.SetServerName(name)
    server.ChatSendServerMessage("Notice:Server renamed to " + name)

commands.append(Command(
    'setservername', setservername, requires_admin=True, has_arg=True))


def setpassword(server, state, caller, password):
    server.SetServerPassword(password)
    server.SetServerPasswordForSpectator(password)
    server.ChatSendServerMessage("Notice: Server is now password-locked")

commands.append(Command
    ('setpassword', setpassword, requires_admin=True, has_arg=True))


def clearpassword(server, state, caller):
    server.SetServerPassword(" ")
    server.SetServerPasswordForSpectator(" ")
    server.ChatSendServerMessage("Notice: Server password was removed")

commands.append(Command(
    'clearpassword', clearpassword, requires_admin=True, has_arg=False))


def autobalance(server, state, caller):
    server.AutoTeamBalance()

commands.append(Command(
    'autobalance', autobalance, requires_admin=True, has_arg=False))
