#!/usr/bin/python

import Gbx
from command_helpers import CommandDoesNotExist
from command_helpers import UserDoesNotHavePermissions, ExpectedArg
from commands import chat_commands


class Manager:
    def __init__(self, config):

        self.state = {"players": {}, "maps": {}}
        self.commands = chat_commands

        self.config = config

        self.sm = Gbx.Client(self.config['address'])
        self.sm.init()
        self.sm.Authenticate(self.config['username'], self.config['password'])
        self.sm.EnableCallbacks(True)

        print "Connected to " + self.sm.GetServerName()

        max_players = self.sm.GetMaxPlayers()['CurrentValue']
        print "%i / %i players connected." % (self.get_player_count(),
            max_players)

        self.repopulate_players()

        # Callbacks
        self.sm.set_default_method(self.cb_default)
        self.sm.add_method("TrackMania.PlayerChat", self.cb_player_chat)
        self.sm.add_method("TrackMania.PlayerConnect", self.cb_player_connect)
        self.sm.add_method("TrackMania.PlayerDisconnect",
            self.cb_player_disconnect)

    ### Internal ###

    def get_player_count(self):
        return len(self.sm.GetPlayerList(100, 0))

    def repopulate_players(self):
        players_list = self.sm.GetPlayerList(100, 0)
        for player in players_list:
            player_info = self.sm.GetPlayerInfo(player['Login'])
            self.state["players"][player['Login']] = Player(player_info, self)

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

    def cb_player_disconnect(self, login):
        del self.state['players'][login]

    def cb_player_chat(self, player_uid, player_login, text, isRegisteredCmd):
        print player_login + ": " + text
        if player_login in self.state['players']:
            if (text.startswith("/")):
                if " " in text:
                    command, arg = text[1:].split(" ", 1)
                else:
                    command = text[1:]
                    arg = None
                self.chat_command(player_login, command, arg)

    def cb_default(self, *args):
        # print args
        pass


class Player:
    def __init__(self, player_info, server):
        self.login = player_info['Login']
        self.nick = player_info['NickName']
        self.id = player_info['PlayerId']

        if self.login in server.config['admin_logins']:
            self.role = "Admin"
        else:
            self.role = "Player"

        print "%s %s connected as %s" % (self.role, self.login, self.nick)

    def __del__(self):
        print "%s %s left" % (self.role, self.login)


if __name__ == '__main__':
    import json

    config_file = open('config.json')
    config = json.loads(config_file.read())
    config_file.close()

    manager = Manager(config)
    while 1:
        manager.sm.tick(3600)
