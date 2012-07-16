# Mini ShootMania Server Script

This is a tiny little ShootMania server script that is mainly focused on adding basic commands to your server, such as switching maps, kicking or banning players, and changing your server's config. This script does not have a radio, it does not have a GUI interface, it will not alter gameplay in the slightest. All this script is is a simple, in-game chat commands interface.

This script is basically not safe for human consumption right now. Don't worry, when it is, I'll post about it on the ManiaPlanet forums and write better docs. And probably a better name.

## Config

Create a config.json file:

```
{
    "address": "YOUR_ADDRESS:5000",
    "username": "SuperAdmin",
    "password": "PASSWORD",
    "admin_logins": [
      "YOUR_USERNAME", "YOUR_BROS_USERNAME"
    ]
}
```

Currently, there are two levels of commands: Admins and Players. To add an admin, add their login name (not their in-game nickname, of course!) to the "admin_logins" list.

## Running

Just `git clone` the repo to your ManiaPlanet directory, `chmod 777 manager.py`, and run `./manager.py` after starting your ShootMania server.

## Commands

### Player commands

* `/nextmap` - See the next map in the rotation

### Admin commands

**Map/game management:**

* `/skip` - Ends the current map and skips to the next one in the rotation
* `/findmap <search>` - Find a map from a partial string match
* `/changemap <map>` - Ends the current map and changes to the one you choose. Requires the full name of the map - use `/findmap` to find it.
* `/getmodesettings` - Dumps all of the settings for the current game mode to your chat box. Press "C" to maximize the chat if you can't see all of them at once.
* `/setmodesettings <key> <value>` - Set a setting for the game mode. Usually doesn't take affect until the next round, or sometimes match/map.

**Player management:**

* `/kick <player>` - Kick a player. Uses the login name of the player.
* `/autobalance` - Auto balances teams. Be warned, tho: auto balance is dumb as all hell, and if you have a two-slot different between teams (like 6v8), it's not going to do the sane thing of just taking one guy from the larger team and moving it over, it's going to respawn like four dudes for no reason.
* `/scramble` - Randomly shuffles around the players on each team.

**Server management:**

* `/setservername <name>`
* `/setpassword <password>` and `/clearpassword`

**Misc:**

* `/echo <message>` - Echo a message to the server as "[Server] Words!". Useful when you wanna look all authoritative.

### To-do

(in no particular order, will be done as I feel like it)

* `/ban <player>` and `/unban <player>`
* `/help` - Would list at least the player-facing commands - maybe have separate `/adminhelp`

## In the wild

Currently used on the Goons server (US-Texas).

## What's next?

* More commands
* Autoscramble/balance on map change
* Way for plugins to hook into callbacks
* Logging to a file(s)
* Script for running as a background task
* Allow admin commands to be run from console
* Gametype management

## Credits

* [Panda](https://github.com/Lavos/panda/) - Similar project for TrackMania servers. Took many design cues from it
* Gbx.py by Marck
* Gamers.org API docs: [methods](http://www.gamers.org/tm2/docs/ListMethods.html) and [callbacks](http://www.gamers.org/tm2/docs/ListCallbacks.html)