import random
from util.plugin import Plugin


class Scrambler(Plugin):
    def __init__(self, server, config):
        super(Scrambler, self).__init__(server, config)
        self.add_callback("ManiaPlanet.BeginMap", self.cb_scramble)
        self.add_command("scramble", self.com_scramble, requires_admin=True, has_arg=False)

    def _scrambler(self):
        #print "scrambling?"
        server = self.server
        all_player_list = server.GetPlayerList(50, 0)
        player_list = []
        # remove spectators
        for player in all_player_list:
            if player['TeamId'] != -1:
                print "Player %s is on team %i" % (player['Login'], player['TeamId'])
                player_list.append(player)

        print "---scrambling this bramble---"
        random.shuffle(player_list)
        for index, player in enumerate(player_list):
            login = player['Login']
            if index % 2 == 0:
                print "Moved %s to team %i" % (login, 0)
                server.ForcePlayerTeam(login, 0)
            else:
                print "Moved %s to team %i" % (login, 1)
                server.ForcePlayerTeam(login, 1)

    def cb_scramble(self, map):
        if self.config['auto_scramble_enabled'] == True:
            self._scrambler()

    def com_scramble(self, state, caller):
        server = self.server
        server.ChatSendServerMessage("Notice: Scrambling teams")
        self._scrambler()

ExportPlugin = Scrambler