from util.helpers import *
from util.commands import *

commands = []


def nextmap(server, state, caller):
    nextmap = server.GetNextMapInfo()['Name']
    server.ChatSendServerMessageToLogin("Next map: " + nextmap, caller)

commands.append(
    Command("nextmap", nextmap, requires_admin=False, has_arg=False)
)


def findmap(server, state, caller, query):
    try:
        matches = search_maps(query, state["maps"])
        map_list = ""
        for match in matches:
            if map_list == "":
                map_list = match.short_name
            else:
                map_list += ", " + match.short_name
        server.ChatSendServerMessageToLogin("Maps matching '%s': %s" %
            (query, map_list), caller)
    except MapNotFound:
        server.ChatSendServerMessageToLogin("No maps found matching query: "
            + query, caller)

commands.append(Command(
    "findmap", findmap, requires_admin=False, has_arg=True))
