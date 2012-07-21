# Allows users to /like and /dislike maps and logs their opinions to a file

from util.helpers import *
from util.plugin import Plugin
import json
import os


class AlreadyVoted(Exception):
    pass


class NoRatings(Exception):
    pass


class MapRating(Plugin):
    def __init__(self, server, config):
        super(MapRating, self).__init__(server, config)

        self.add_command("like", self.com_like_map, requires_admin=False, has_arg=False)
        self.add_command("dislike", self.com_dislike_map, requires_admin=False, has_arg=False)
        self.add_command("getrating", self.com_get_rating, requires_admin=False, has_arg=False)

        self.add_command("savevotes", self.com_save_votes, requires_admin=True, has_arg=False)

        self.add_callback("ManiaPlanet.BeginMap", self.cb_advertise)
        self.add_callback("ManiaPlanet.BeginMap", self.cb_save)

        if os.path.exists("db/map_votes.json"):
            self.map_file = open("db/map_votes.json", 'r+')
        else:
            self.map_file = open("db/map_votes.json", 'w+')

        try:
            self.map_votes = json.loads(self.map_file.read())
        except ValueError:
            log("*** WARN: Could not parse map_votes JSON. File may be empty or corrupted.")
            self.map_votes = {}

    def _rate_map(self, caller, vote, map_name):
        if map_name in self.map_votes:
            votes = self.map_votes[map_name]['player_votes']
            if caller in votes and votes[caller] == vote:
                raise AlreadyVoted()
                return
            else:
                votes[caller] = vote
                self.server.ChatSendServerMessageToLogin("Thank you for voting on this map.", caller)
        else:
            self.map_votes[map_name] = {"player_votes": {}, "avg": 0}
            self._rate_map(caller, vote, map_name)

    def _calc_rating(self, map_name):
        if map_name in self.map_votes:
            votes = self.map_votes[map_name]['player_votes'].values()
            avg = sum(votes) / len(votes)
            return avg
        else:
            raise NoRatings()

    def com_like_map(self, state, caller):
        map_name = self.server.GetCurrentMapInfo()['FileName']
        try:
            self._rate_map(caller, 1, map_name)
        except AlreadyVoted:
            self.server.ChatSendServerMessageToLogin("You have already liked this map.", caller)

    def com_dislike_map(self, state, caller):
        try:
            map_info = self.server.GetCurrentMapInfo()
            map_name = map_info['FileName']
        # debug, remove when done
        except KeyError:
            print "*** ERR: KeyError when trying to dislike map"
            print "map_info = "
            print map_info
            quit()
        try:
            self._rate_map(caller, 0, map_name)
        except AlreadyVoted:
            self.server.ChatSendServerMessageToLogin("You have already disliked this map.", caller)

    def com_get_rating(self, state, caller):
        try:
            rating = self._calc_rating(self.server.GetCurrentMapInfo()['FileName'])
            self.server.ChatSendServerMessageToLogin("This map is rated {0:.0f}%.".format(rating * 100), caller)
        except NoRatings:
            self.server.ChatSendServerMessageToLogin("There are no ratings yet for this map.", caller)

    #debug
    def com_save_votes(self, state, caller):
        self.map_file.truncate()
        json.dump(self.map_votes, self.map_file)

    def cb_advertise(self, *args):
        self.server.ChatSendServerMessage("Make sure to /like or /dislike this map to decide whether it stays in rotation!")

    def cb_save(self, *args):
        #todo: efficiency. but this is once per map change, not like once per vote, so it's not that bad (and we don't need to worry about concurrent saves or anything crazy)
        self.map_file.seek(0)
        self.map_file.truncate()
        json.dump(self.map_votes, self.map_file)


ExportPlugin = MapRating
