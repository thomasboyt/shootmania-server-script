from util.helpers import *
from util.plugin import Plugin


class General(Plugin):
    def __init__(self, server, config):
        super(General, self).__init__(server, config)

        self.add_command("nextmap", self.com_nextmap, requires_admin=False, has_arg=False)
        self.add_command("findmap", self.com_findmap, requires_admin=False, has_arg=True)

        self.add_callback("ManiaPlanet.BeginMap", self.cb_map_greeting)

    def com_nextmap(self, state, caller):
        server = self.server
        nextmap = server.GetNextMapInfo()['Name']
        server.ChatSendServerMessageToLogin("Next map: " + nextmap, caller)

    def com_findmap(self, state, caller, query):
        server = self.server
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

    def cb_map_greeting(self, map_info):
        self.server.ChatSendServerMessage("Welcome to %s" % (map_info['Name']))

ExportPlugin = General