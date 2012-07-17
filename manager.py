#!/usr/bin/python

import Gbx

from plugins.util.plugin import plugin_loader
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
        
        self.sm = Gbx.Client(self.config['address'])
        self.sm.init()
        self.sm.SetApiVersion("2012-06-19")
        self.sm.Authenticate(self.config['username'], self.config['password'])
        self.sm.EnableCallbacks(True)

        self.command_handler, self.cb_handler = plugin_loader(self.sm, config['plugins'])

        #mode_loader(self.sm, self.state, self.state['server_config']['default_mode'])

        # Placeholder configuration (see issue #1)
        server_cfg = self.state['server_config']

        name = server_cfg['name']
        default_mode = server_cfg['default_mode']
        if server_cfg['append_mode'] == True:
            name = "%s (%s)" % (name, default_mode)

        self.sm.SetServerName(name)
        self.sm.SetServerPassword(server_cfg['password'])
        self.sm.SetServerPasswordForSpectator(server_cfg['password'])

        try:
            mode_cfg = server_cfg['modes'][default_mode]['mode_settings']
            self.sm.SetModeScriptSettings(mode_cfg)
        except KeyError:
            pass

        self.sync()
        dump_state(self.sm, self.state)

        # Callbacks
        self.sm.set_default_method(self.cb_default)
        self.cb_handler.add("ManiaPlanet.PlayerChat", self.cb_player_chat)
        self.cb_handler.add("ManiaPlanet.PlayerConnect", self.cb_player_connect)
        self.cb_handler.add("ManiaPlanet.PlayerDisconnect", self.cb_player_disconnect)
        self.cb_handler.add("ManiaPlanet.BeginMap", self.cb_begin_map)

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
            self.command_handler.run(command, login, arg, self.state)
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

        # this seems to be happening when I scramble sometimes?
        if type(player_info) == bool:
            log("*** WARN: For some reason got a bool for player_info.")
            log("player_info = " + str(player_info) + "")
            log("isspec = " + str(isspec))
            return

        self.state['players'][login] = Player(player_info, self)
        player = self.state['players'][login]
        log(">> %s %s connected as %s" % (player.role, player.login,
            player.safe_nick))

    def cb_player_disconnect(self, login):
        try:
            role = self.state['players'][login].role
            log("<< %s %s left" % (role, login))
            del self.state['players'][login]
        except KeyError:
            log("*** WARN: %s left; was not in players[]!" % (login))

    def cb_player_chat(self, player_uid, player_login, text, isRegisteredCmd):
        log(player_login + ": " + text)
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
        log("*** changed map to %s at index %i" % (short_name, self.state['current_map_index']))
        self.sm.ChatSendServerMessage("Welcome to %s" % (new_map.map_name))

    def cb_default(self, *args):
        # useful debug tool if you want to see all callbacks:
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


class Map:
    def __init__(self, state, map_info, pos):
        self.map_name = map_info['Name']
        self.file_name = map_info['FileName']

        self.short_name = self.file_name.rsplit('/')[-1][:-8]

        self.map_type = map_info['MapType']
        self.pos = pos


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
        print "Check to see if you forgot a comma or a quotation or something!"
        quit()

    config_file.close()

    manager = Manager(config)
    while 1:
        manager.sm.tick(3600)
