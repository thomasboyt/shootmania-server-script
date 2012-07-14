#!/usr/bin/python

import Gbx
from command_helpers import CommandDoesNotExist
from command_helpers import UserDoesNotHavePermissions, ExpectedArg
from commands import chat_commands

from helpers import sanitize


class Manager:
    def __init__(self, config):

        # state object gets passed to chat commands, etc.
        self.state = {
            "players": {},
            "maps": [],
            "current_map_index": 0,
            "config": config
        }
        self.commands = chat_commands

        self.config = config

        self.sm = Gbx.Client(self.config['address'])
        self.sm.init()
        self.sm.SetApiVersion("2012-06-19")
        self.sm.Authenticate(self.config['username'], self.config['password'])
        self.sm.EnableCallbacks(True)

        self.sync()
        self.dump_state()

        # Callbacks
        self.sm.set_default_method(self.cb_default)
        self.sm.add_method("ManiaPlanet.PlayerChat", self.cb_player_chat)
        self.sm.add_method("ManiaPlanet.PlayerConnect", self.cb_player_connect)
        self.sm.add_method("ManiaPlanet.PlayerDisconnect",
            self.cb_player_disconnect)
        self.sm.add_method("ManiaPlanet.BeginMap", self.cb_begin_map)
        #self.sm.add_method("ManiaPlanet.ChallengeListModified",
        #    self.cb_chlist_modified)

    ### Internal ###

    def get_player_count(self):
        return len(self.sm.GetPlayerList(100, 0))

    def sync(self):
        players_list = self.sm.GetPlayerList(100, 0)
        for player_info in players_list:
            self.state["players"][player_info['Login']] = Player(player_info,
                self)

        self.state['current_map_index'] = self.sm.GetCurrentMapIndex()

        maps_list = self.sm.GetMapList(1000, 0)
        for map_info in maps_list:
            pos = len(self.state['maps'])
            self.state['maps'].append(Map(self.state, map_info, pos))

    def dump_state(self):
        players = self.state["players"].values()
        maps = self.state["maps"]
        max_players = self.sm.GetMaxPlayers()['CurrentValue']

        print sanitize(self.sm.GetServerName())
        password = self.sm.GetServerPassword()
        if password:
            print "Current password: " + password

        print "\nPlayers (%i / %i)" % (len(players), max_players)
        print "--------------------------------------------------------------"
        if (len(players) > 0):
            for player in players:
                print player
        else:
            print "No players connected."

        print ""
        print "Maps (%i total)" % (len(maps))
        print "---------+----------------------------------------------------"
        print "Position | Map name"
        print "---------+----------------------------------------------------"
        for map_item in maps:
            string = "%i\t | %s" % (map_item.pos, map_item.short_name)
            if map_item.pos == self.state["current_map_index"]:
                string = "* " + string
            else:
                string = "  " + string
            print string

        print ""

    def chat_command(self, login, command, arg):
        try:
            self.commands.run(command, login, arg, self.sm, self.state)
        except CommandDoesNotExist:
            self.sm.ChatSendServerMessageToLogin("Command " + command +
                " does not exist", login)
        except UserDoesNotHavePermissions:
            self.sm.ChatSendServerMessageToLogin("You do not have the" +
                " permission to run " + command, login)
        except ExpectedArg:
            self.sm.ChatSendServerMessageToLogin("Argument expected for " +
                command, login)

    def find_map(self, name):
        # todo: partial matches, no map found exception
        for map_item in self.state['maps']:
            if map_item.short_name == name:
                return map_item

    ### Callbacks ###

    def cb_player_connect(self, login, isspec):
        player_info = self.sm.GetPlayerInfo(login)
        self.state['players'][login] = Player(player_info, self)
        player = self.state['players'][login]
        print "%s %s connected as %s" % (player.role, player.login,
            player.safe_nick)

    def cb_player_disconnect(self, login):
        role = self.state['players'][login].role
        del self.state['players'][login]
        print "%s %s left" % (role, login)

    def cb_player_chat(self, player_uid, player_login, text, isRegisteredCmd):
        print sanitize(player_login + ": " + text)
        if player_login in self.state['players']:
            if (text.startswith("/")):
                if " " in text:
                    command, arg = text[1:].split(" ", 1)
                else:
                    command = text[1:]
                    arg = None
                self.chat_command(player_login, command, arg)

    # using this as a placeholder until ManiaPlanet.BeginMap is implimented :S
    #def cb_chlist_modified(self, new_map_index, next_map_index, some_boolean):
    #    self.state['current_map_index'] = new_map_index
    #    name = self.state['maps'][new_map_index].short_name
    #    print "*** Map rotated to %s at index %i ***" % (name, new_map_index)

    def cb_begin_map(self, map_info):
        short_name = map_info['FileName'].rsplit('/')[-1][:-8]

        new_map = self.find_map(short_name)
        self.state['current_map_index'] = new_map.pos
        print "*** changed map to %s at index %i" % (short_name,
            self.state['current_map_index'])

    def cb_default(self, *args):
        # print args
        pass


class Player:
    def __init__(self, player_info, server):
        self.login = player_info['Login']
        self.nick = player_info['NickName']
        self.safe_nick = sanitize(self.nick)
        self.id = player_info['PlayerId']

        if self.login in server.config['admin_logins']:
            self.role = "Admin"
        else:
            self.role = "Player"

    def __str__(self):
        return "%s %s is connected as %s" % (self.role, self.login,
            self.safe_nick)


class Map:
    def __init__(self, state, map_info, pos):
        self.map_name = map_info['Name']
        self.file_name = map_info['FileName']

        self.short_name = self.file_name.rsplit('/')[-1][:-8]

        self.map_type = map_info['MapType']
        self.pos = pos

    def __str__(self):
        return sanitize("Map %s in position %i" % (self.short_name, self.pos))


if __name__ == '__main__':
    import json

    config_file = open('config.json')
    config = json.loads(config_file.read())
    config_file.close()

    manager = Manager(config)
    while 1:
        manager.sm.tick(3600)
