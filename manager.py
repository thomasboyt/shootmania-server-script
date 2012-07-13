# Manager.py: a lightweight ManiaPlanet server manager, focusing on ShootMania

# Credits go, of course, to Marck's Gbx.py, as well as Lavos's Panda, another
# lightweight Python ManiaPlanet server script I took many of my cues from:
# https://github.com/Lavos/panda/blob/master/panda.py
# And also the gamers.org ManiaPlanet Server API reference:
# http://www.gamers.org/tm2/docs/ListMethods.html

import Gbx
# import xmlrpclib
from inspect import getargspec


class Manager:
    def __init__(self, config):

        self.players = {}
        self.maps = {}
        self.commands = {}

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

        # Chat Commands

        self.commands['echo'] = self.chat_command_echo
        self.commands['hello'] = self.chat_command_hello

        self.commands['next'] = self.chat_command_nextmap
        self.commands['map'] = self.chat_command_change_map
        self.commands['kick'] = self.chat_command_kick

    ### Internal ###

    def get_player_count(self):
        return len(self.sm.GetPlayerList(100, 0))

    def repopulate_players(self):
        players_list = self.sm.GetPlayerList(100, 0)
        for player in players_list:
            player_info = self.sm.GetPlayerInfo(player['Login'])
            self.players[player['Login']] = Player(player_info, self)

    def chat_command(self, player, command, arg):
        if command in self.commands:
            function = self.commands[command]
            arg_expected = (len(getargspec(function).args) > 1)
            if arg_expected and arg == None:
                # send to player: hey you forgot an arg!
                self.sm.ChatSendServerMessageToLogin("Hey, you forgot an arg.",
                    player)
            elif not arg_expected:
                function(player)
            else:
                function(player, arg)

    ### Callbacks ###

    def cb_player_connect(self, login, isspec):
        player_info = self.sm.GetPlayerInfo(login)
        self.players[login] = Player(player_info, self)

    def cb_player_disconnect(self, login):
        del self.players[login]

    def cb_player_chat(self, player_uid, player_login, text, isRegisteredCmd):
        if player_login in self.players:
            if self.players[player_login].role == "Admin":
                if (text.startswith("/")):
                    if " " in text:
                        command, arg = text[1:].split(" ", 1)
                    else:
                        command = text[1:]
                        arg = None
                    self.chat_command(player_login, command, arg)
        else:
            print player_login + ": " + text
        return

    def cb_default(self, *args):
        # print args
        pass

    ### Chat Commands ###
    def chat_command_change_map(self, caller, new_map):
        self.sm.ChatSendServerMessageToLogin("Not implimented yet", caller)
        #self.sm.ChooseNextMap(new_map)
        #self.sm.NextMap()

    def chat_command_nextmap(self, caller):
        self.sm.NextMap()

    def chat_command_kick(self, caller, target):
        if target in self.players:
            self.sm.Kick(target)
        else:
            # some day will add support for kicking nicks
            self.sm.ChatSendServerMessageToLogin("Name not found", caller)

    def chat_command_hello(self, caller):
        print "Hello!"

    def chat_command_echo(self, caller, message):
        self.sm.ChatSendServerMessage(message)


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
