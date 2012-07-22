import random
from util.plugin import Plugin
from util.helpers import *


class Scrambler(Plugin):
    def __init__(self, server, config):
        super(Scrambler, self).__init__(server, config)
        self.add_callback("ManiaPlanet.BeginMap", self.cb_scramble)
        self.add_command("scramble", self.com_scramble, requires_admin=True, has_arg=False)

    def _scrambler(self):
        #todo: only use if mode is team-based... of course, right now it just does nothing if it isn't
        server = self.server
        all_player_list = server.GetPlayerList(50, 0)
        player_list = []
        # remove spectators
        for player in all_player_list:
            if player['TeamId'] != -1:
                log("Player %s is on team %i" % (player['Login'], player['TeamId']), log_type="debug")
                player_list.append(player)

        log("---scrambling this bramble---", log_type="debug")
        random.shuffle(player_list)
        for index, player in enumerate(player_list):
            login = player['Login']
            if index % 2 == 0:
                log("Moved %s to team %i" % (login, 0), log_type="debug")
                server.ForcePlayerTeam(login, 0)
            else:
                log("Moved %s to team %i" % (login, 1), log_type="debug")
                server.ForcePlayerTeam(login, 1)

    def cb_scramble(self, map):
        if self.config['auto_scramble_enabled'] == True:
            self._scrambler()

    def com_scramble(self, state, caller):
        server = self.server
        server.ChatSendServerMessage("Notice: Scrambling teams")
        self._scrambler()

ExportPlugin = Scrambler