#!/usr/bin/python

import Gbx

from plugins.util.commands import command_loader
from plugins.util.exceptions import *
from plugins.util.helpers import *


class Manager:
    def __init__(self, config):

        # state object gets passed to chat commands, etc.
        self.state = {
            "players": {},
            "maps": [],
            "current_map_index": 0,
            "server_config": config["server_config"]
        }

        self.config = config["tiny_config"]

        self.commands = command_loader(self.config['plugins'])

        self.sm = Gbx.Client(self.config['address'])
        self.sm.init()
        self.sm.SetApiVersion("2012-06-19")
        self.sm.Authenticate(self.config['username'], self.config['password'])
        self.sm.EnableCallbacks(True)

        self.sync()
        dump_state(self.sm, self.state)

        #print self.sm.GetScriptName()
        #print self.sm.GetModeScriptSettings()

        mode_loader(self.sm, self.state, self.state['server_config']['default_mode'])

        # Callbacks
        self.sm.set_default_method(self.cb_default)
        self.sm.add_method("ManiaPlanet.PlayerChat", self.cb_player_chat)
        self.sm.add_method("ManiaPlanet.PlayerConnect", self.cb_player_connect)
        self.sm.add_method("ManiaPlanet.PlayerDisconnect",
            self.cb_player_disconnect)
        self.sm.add_method("ManiaPlanet.BeginMap", self.cb_begin_map)

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

    ### Callbacks ###

    def cb_player_connect(self, login, isspec):
        player_info = self.sm.GetPlayerInfo(login)
        self.state['players'][login] = Player(player_info, self)
        player = self.state['players'][login]
        print ">> %s %s connected as %s" % (player.role, player.login,
            player.safe_nick)

    def cb_player_disconnect(self, login):
        try:
            role = self.state['players'][login].role
            print "<< %s %s left" % (role, login)
            del self.state['players'][login]
        except KeyError:
            print "*** WARN: %s left; was not in players[]!" % (login)

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

    def cb_begin_map(self, map_info):
        short_name = map_info['FileName'].rsplit('/')[-1][:-8]

        new_map = find_map(short_name, self.state['maps'])
        self.state['current_map_index'] = new_map.pos
        print "*** changed map to %s at index %i" % (short_name,
            self.state['current_map_index'])
        self.sm.ChatSendServerMessage("Welcome to %s" % (
            new_map.map_name))

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


class Mode:
    def __init__(self, name, settings, is_current=False):
        self.name = name
        self.settings = settings


if __name__ == '__main__':
    import json

    try:
        config_file = open('config.json')
    except IOError:
        print "Couldn't find your config.json file."
        print "Have you created one yet? Check the readme for help."
        quit()

    try:
        config = json.loads(config_file.read())
    except ValueError as e:
        print "Error parsing your config file:"
        print e
        print "Check to see if you forgot a comma or a quotation or something! :]"
        quit()

    config_file.close()

    manager = Manager(config)
    while 1:
        manager.sm.tick(3600)
