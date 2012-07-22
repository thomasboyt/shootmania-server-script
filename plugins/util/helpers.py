import string
import xmlrpclib
import time
import logging

from exceptions import *

log_timecode = time.strftime("%Y-%m-%d_%H-%M-%S")
log_filename = "logs/log_%s.txt" % (log_timecode)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%I:%M:%S %p', filename=log_filename, level=logging.DEBUG)

log_levels = {
    "chat": 0,
    "debug": 10,
    "info": 20,
    "warning": 30,
    "error": 40,
    "critical": 50
}


# remove unicode
def sanitize(s):
    filtered_string = filter(lambda x: x in string.printable, s)
    return filtered_string


def find_map(name, maps):
    for map_item in maps:
        if map_item.short_name == name:
            return map_item
    raise MapNotFound()


def search_maps(search, maps):
    results = []
    for map_item in maps:
        if search.lower() in map_item.short_name.lower():
            results.append(map_item)
    if len(results) > 0:
        return results
    else:
        raise MapNotFound()


def log(message, has_timestamp=True, log_type="chat"):
    # sanitize doesn't work against objects that can be represented as string
    if type(message) == str:
        message = sanitize(message)

    log_type = log_type.lower()
    if log_type in log_levels:
        level_num = log_levels[log_type]
        logging.log(level_num, message)
        if has_timestamp:
            timestamp = time.strftime("[%H:%M:%S] ")
            message = str(timestamp) + message
        print message
    else:
        raise ValueError()


def api_error(err):
    return "*** API ERROR: %i: %s" % (err.faultCode, err.faultString)


def dump_state(server, state):
    players = state["players"].values()
    maps = state["maps"]
    max_players = server.GetMaxPlayers()['CurrentValue']

    log(server.GetServerName(), has_timestamp=False)
    password = server.GetServerPassword()
    if password:
        log("Current password: " + password, has_timestamp=False)

    log("\nPlayers (%i / %i)" % (len(players), max_players), has_timestamp=False)
    log("--------------------------------------------------------------", has_timestamp=False)
    if (len(players) > 0):
        for player in players:
            log("%s %s is connected as %s" % (player.role, player.login, player.safe_nick), has_timestamp=False)
    else:
        log("No players connected.", has_timestamp=False)

    log("\nMaps (%i total)" % (len(maps)), has_timestamp=False)
    log("---------+----------------------------------------------------", has_timestamp=False)
    log("Position | Map name", has_timestamp=False)
    log("---------+----------------------------------------------------", has_timestamp=False)
    for map_item in maps:
        log_string = "%i\t | %s" % (map_item.pos, map_item.short_name)
        if map_item.pos == state["current_map_index"]:
            log_string = "* " + log_string
        else:
            log_string = "  " + log_string
        log(log_string, has_timestamp=False)
    log("", has_timestamp=False)


# Sets the mode and changes map to the proper rotation
# All kinds of hella broken. See issue #1
def mode_loader(server, state, mode_name):
    modes = state['server_config']['modes']
    if not mode_name in modes:
        raise ModeNotFoundError()

    mode_cfg = modes[mode_name]
    mode_file = mode_name + ".Script.txt"

    next_mode = server.GetScriptName()["NextValue"]
    if next_mode == mode_file:
        log("*** WARN: Script was already set as the next mode!")
        return

    print server.GetModeScriptInfo()

    try:
        server.SetScriptName(mode_file)
    except xmlrpclib.Fault, err:
        log(api_error(err))
        log("*** ERROR: Could not load script '%s'. Is it on the server?" %
            (mode_file))
        server.SetScriptName(next_mode)

    # so, now we've set the next mode. Let's load in the maps for it!
    match_settings_file = mode_cfg['match_settings']
    try:
        server.LoadMatchSettings(match_settings_file)
    except xmlrpclib.Fault, err:
        log(api_error(err))
        log("*** ERROR: Could not load MatchSettings '%s'. Is it on the server?" %
            (match_settings_file))

    server.NextMap()

    server.SetModeScriptSettings(mode_cfg['mode_settings'])


def convert_to_api_type(value):
    try:
        value = int(value)
    except ValueError:
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        else:
            try:
                value = str(value)
            except ValueError:
                raise CouldNotConvertToApiType()
    return value