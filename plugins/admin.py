from util.helpers import *
from util.plugin import Plugin
from xmlrpclib import Fault


class Admin(Plugin):
    def __init__(self, server, config):
        super(Admin, self).__init__(server, config)

        self.add_command("changemap", self.com_change_map, requires_admin=True, has_arg=True)
        self.add_command("skip", self.com_skip_map, requires_admin=True, has_arg=False)
        self.add_command("getmodesettings", self.com_get_mode_settings, requires_admin=True, has_arg=False)
        self.add_command("setmodesetting", self.com_set_mode_setting, requires_admin=True, has_arg=True)
        self.add_command("reloadmatchsettings", self.com_reload_match_settings, requires_admin=True, has_arg=False)
        #self.add_command("restartmap", self.restart_map, requires_admin=True, has_arg=False)

        self.add_command("setservername", self.com_set_server_name, requires_admin=True, has_arg=True)
        self.add_command("setpassword", self.com_set_password, requires_admin=True, has_arg=True)
        self.add_command("getpassword", self.com_get_password, requires_admin=True, has_arg=False)
        self.add_command("clearpassword", self.com_clear_password, requires_admin=True, has_arg=False)

        #self.add_command("setmaxplayers", self_com_set_max_players, requires_admin=True, has_arg=True)

        self.add_command("autobalance", self.com_autobalance, requires_admin=True, has_arg=False)
        self.add_command("kick", self.com_kick, requires_admin=True, has_arg=True)
        self.add_command("ban", self.com_ban, requires_admin=True, has_arg=True)
        #self.add_command("unban", self.com_unban, requires_admin=True, has_arg=True)
        #self.add_command("clearbans", self.clear_bans, requires_admin=True, has_arg=False)
        #self.add_command("getbans", self_get_ban_list, requires_admin=True, has_arg=False)

        self.add_command("echo", self.com_echo, requires_admin=True, has_arg=True)

    ### Map/mode management ###

    def com_skip_map(self, state, caller):
        server = self.server
        caller_nick = state['players'][caller].nick
        server.ChatSendServerMessage("Notice: %s ended map." % (caller_nick))
        server.NextMap()

    def com_restart_map(self, state, caller):
        caller_nick = state['players'][caller].nick
        self.server.ChatSendServerMessage("Notice: %s restarted the match." % (caller_nick))
        self.server.RestartMap()

    def com_change_map(self, state, caller, name):
        server = self.server
        try:
            matches = search_maps(name, state["maps"])
            if len(matches) == 1:
                new_map = matches[0]
                server.ChooseNextMap(new_map.file_name)
                caller_nick = state['players'][caller].nick
                server.ChatSendServerMessage("Notice: %s changed map to %s" % (caller_nick, new_map.map_name))
                server.NextMap()
            else:
                map_list = ""
                for index, match in enumerate(matches):
                    # make a pretty little list
                    if index == (len(matches) - 1):
                        map_list += ", or "
                    elif index != 0:
                        map_list += ", "
                    map_list += match.short_name

                server.ChatSendServerMessageToLogin("Did you mean: %s?" % (map_list), caller)
        except MapNotFound:
            server.ChatSendServerMessageToLogin("No map found matching: " + name, caller)

    # When ManiaLink support is implimented, this will be replaced with a nice
    # little popup. Until then...
    def com_get_mode_settings(self, state, caller):
        server = self.server
        settings = server.GetModeScriptSettings()
        for setting, value in settings.items():
            server.ChatSendServerMessageToLogin("%s: %s" % (setting, value), caller)

    def com_set_mode_setting(self, state, caller, args):
        server = self.server
        try:
            key, value = args.split(" ", 1)
        except ValueError:
            key = args
            try:
                value = server.GetModeScriptSettings()[key]
                server.ChatSendServerMessageToLogin("%s is set to %s" % (key, value), caller)
            except KeyError:
                server.ChatSendServerMessageToLogin("Setting '%s' not found in current script" % (key), caller)
            return

        try:
            server.SetModeScriptSettings({key: convert_to_api_type(value)})
            caller_nick = state['players'][caller].nick
            server.ChatSendServerMessage("Notice: %s set '%s' to %s." % (caller_nick, key, value))
        except Fault as e:
            if e.faultCode == -1000:
                server.ChatSendServerMessageToLogin("Setting '%s' not found in current script" % (key), caller)

    def com_reload_match_settings(self, state, caller):
        mode = self.server.GetScriptName()['CurrentValue']
        mode = mode[:-11]  # remove ".Script.txt"
        match_settings = "MatchSettings/SMStorm" + mode + ".txt"
        print match_settings
        self.server.LoadMatchSettings(match_settings)

    ### Basic server settings ###

    def com_set_server_name(self, state, caller, name):
        server = self.server
        server.SetServerName(name)
        server.ChatSendServerMessage("Notice: Server renamed to " + name)

    def com_set_password(self, state, caller, password):
        server = self.server
        server.SetServerPassword(password)
        server.SetServerPasswordForSpectator(password)
        server.ChatSendServerMessage("Notice: Server is now password-locked.")
        server.ChatSendServerMessageToLogin("Notice: You have set the password to '%s'" %
            (password), caller)

    def com_get_password(self, state, caller):
        server = self.server
        password = server.GetServerPassword()
        server.ChatSendServerMessageToLogin("The password is '%s'" % (password), caller)

    def com_clear_password(self, state, caller):
        server = self.server
        server.SetServerPassword(" ")
        server.SetServerPasswordForSpectator(" ")
        server.ChatSendServerMessage("Notice: Server password was removed.")

    ### Player/team management ###

    def com_autobalance(self, state, caller):
        server = self.server
        caller_nick = state['players'][caller].nick
        server.ChatSendServerMessage("Notice: %s balanced teams." % (caller_nick))
        server.AutoTeamBalance()

    def com_kick(self, state, caller, target):
        server = self.server
        if target in state['players']:
            caller_nick = state['players'][caller].nick
            msg = "%s (%s) was kicked by %s" % (state['players'][target].nick, target, caller_nick)
            server.ChatSendServerMessage(msg)
            server.Kick(target)
        else:
            # some day will add support for kicking nicks
            server.ChatSendServerMessageToLogin("Name not found", caller)

    def com_ban(self, state, caller, target):
        server = self.server
        if target in state['players']:
            caller_nick = state['players'][caller].nick
            msg = "%s (%s) was banned by %s" % (state['players'][target].nick, target, caller_nick)
            server.ChatSendServerMessage(msg)
            server.Ban(target)
        else:
            server.ChatSendServerMessageToLogin("Name not found", caller)

    # needs testing:
    # - what fault code does it produce when trying to unban a player who isn't in the ban list?
    #def com_unban(self, state, caller, target)

    ### Misc. ###

    def com_echo(self, state, caller, message):
        self.server.ChatSendServerMessage("[Server] " + message)

ExportPlugin = Admin
