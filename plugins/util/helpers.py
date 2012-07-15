import string
import xmlrpclib

from exceptions import *


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


def log(print_string, should_print=True):
    # sanitize doesn't work against objects that can be represented as string
    # (such as map and player), but those are sanitized already so it's no big deal
    # just be careful when concating safe and unsafe strings!
    if type(print_string) == str:
        sanitize(print_string)
    # to-do: actually log to a file here
    if should_print == True:
        print print_string


def api_error(err):
    return "*** API ERROR: %i: %s" % (err.faultCode, err.faultString)


def dump_state(server, state):
    players = state["players"].values()
    maps = state["maps"]
    max_players = server.GetMaxPlayers()['CurrentValue']

    log(server.GetServerName())
    password = server.GetServerPassword()
    if password:
        log("Current password: " + password)

    log("\nPlayers (%i / %i)" % (len(players), max_players))
    log("--------------------------------------------------------------")
    if (len(players) > 0):
        for player in players:
            log(player)
    else:
        log("No players connected.")

    log("")
    log("Maps (%i total)" % (len(maps)))
    log("---------+----------------------------------------------------")
    log("Position | Map name")
    log("---------+----------------------------------------------------")
    for map_item in maps:
        log_string = "%i\t | %s" % (map_item.pos, map_item.short_name)
        if map_item.pos == state["current_map_index"]:
            log_string = "* " + log_string
        else:
            log_string = "  " + log_string
        log(log_string)
    log("")


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
        #return

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

    print mode_cfg['mode_settings']
    server.SetModeScriptSettings(mode_cfg['mode_settings'])
    #print server.GetModeScriptSettings()


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