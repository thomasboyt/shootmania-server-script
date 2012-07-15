from util.commands import *
from util.helpers import *
from xmlrpclib import Fault

commands = []


def skip(server, state, caller):
    caller_nick = state['players'][caller].nick
    server.ChatSendServerMessage("Notice: %s ended map" % (caller_nick))
    server.NextMap()

commands.append(
    Command('skip', skip, requires_admin=True, has_arg=False))


def changemap(server, state, caller, name):
    try:
        matches = search_maps(name, state["maps"])

        if len(matches) == 1:
            new_map = matches[0]
            server.ChooseNextMap(new_map.file_name)
            caller_nick = state['players'][caller].nick
            server.ChatSendServerMessage("Notice: %s changed map to %s" % (caller_nick, new_map.map_name))
            server.NextMap()
        else:
            map_list = ""
            for index, match in enumerate(matches):
                # make a pretty little list
                if index == (len(matches) - 1):
                    map_list += ", or "
                elif index != 0:
                    map_list += ", "
                map_list += match.short_name

            server.ChatSendServerMessageToLogin("Did you mean: %s?" % (map_list), caller)

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
        caller_nick = state['players'][caller].nick
        msg = "%s (%s) was kicked by %s" % (state['players'][target].nick,
            target, caller_nick)
        server.ChatSendServerMessage(msg)
        server.Kick(target)
    else:
        # some day will add support for kicking nicks
        server.ChatSendServerMessageToLogin("Name not found", caller)

commands.append(
    Command('kick', kick, requires_admin=True, has_arg=True))


def setservername(server, state, caller, name):
    server.SetServerName(name)
    server.ChatSendServerMessage("Notice: Server renamed to " + name)

commands.append(Command(
    'setservername', setservername, requires_admin=True, has_arg=True))


def setpassword(server, state, caller, password):
    server.SetServerPassword(password)
    server.SetServerPasswordForSpectator(password)
    server.ChatSendServerMessage("Notice: Server is now password-locked")
    server.ChatSendServerMessageToLogin("Notice: You have set the password to %s" %
        (password), caller)

commands.append(Command
    ('setpassword', setpassword, requires_admin=True, has_arg=True))


def getpassword(server, state, caller):
    password = server.GetServerPassword()
    server.ChatSendServerMessageToLogin("The password is '%s'" % (password), caller)

commands.append(Command(
    'getpassword', getpassword, requires_admin=True, has_arg=False))


def clearpassword(server, state, caller):
    server.SetServerPassword(" ")
    server.SetServerPasswordForSpectator(" ")
    server.ChatSendServerMessage("Notice: Server password was removed")

commands.append(Command(
    'clearpassword', clearpassword, requires_admin=True, has_arg=False))


def autobalance(server, state, caller):
    server.ChatSendServerMessage("Notice: %s balanced teams" % (caller))
    server.AutoTeamBalance()

commands.append(Command(
    'autobalance', autobalance, requires_admin=True, has_arg=False))


def dumpmodesettings(server, state, caller):
    settings = server.GetModeScriptSettings()
    print settings

commands.append(Command(
    'dumpmodesettings', dumpmodesettings, requires_admin=True, has_arg=False))


# When ManiaLink support is implimented, this will be replaced with a nice
# little popup. Until then...
def getmodesettings(server, state, caller):
    settings = server.GetModeScriptSettings()
    for setting, value in settings.items():
        server.ChatSendServerMessageToLogin("%s: %s" % (setting, value), caller)

commands.append(Command(
    'getmodesettings', getmodesettings, requires_admin=True, has_arg=False))


def setmodesetting(server, state, caller, args):
    try:
        key, value = args.split(" ", 1)
    except ValueError:
        key = args
        try:
            value = server.GetModeScriptSettings()[key]
            server.ChatSendServerMessageToLogin("%s is set to %s" % (key, value), caller)
        except KeyError:
            server.ChatSendServerMessageToLogin("Setting '%s' not found in current script" % (key), caller)
        return

    try:
        server.SetModeScriptSettings({key: convert_to_api_type(value)})
        caller_nick = state['players'][caller].nick
        server.ChatSendServerMessage("Notice: %s set '%s' to %s." % (caller_nick, key, value))
    except Fault as e:
        if e.faultCode == -1000:
            print e.faultString
            server.ChatSendServerMessageToLogin("Setting '%s' not found in current script" % (key), caller)

commands.append(Command(
    'setmodesetting', setmodesetting, requires_admin=True, has_arg=True))