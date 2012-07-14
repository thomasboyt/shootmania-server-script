# Mini ShootMania Server Script

This is a tiny little ShootMania server script that is mainly focused on adding basic commands to your server, such as switching maps, kicking or banning players, and changing your server's config. This script does not have a radio, it does not have a GUI interface, it will not alter gameplay in the slightest. All this script is is a simple, in-game chat commands interface.

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

**Map management:**

* `/skip` - Ends the current map and skips to the next one in the rotation

**Player management:**

* `/kick <player>` - Kick a player. Uses the login name of the player.

**Server management:**

* `/setservername <name>`
* `/setpassword <password>` and `/clearpassword`

**Misc:**

* `/echo <message>` - Echo a message to the server (white text)
* `/help` - Would list at least the player-facing commands - maybe have separate `/adminhelp`

### To-do

(in no particular order, will be done as I feel like it)

* `/changemap <map>`
* `/mapslist` (dump full maplist to console)
* `/findmap` (search map names for a specific file)
* `/ban <player>` and `/unban <player>`
* `/playerslist` (dump full playerslist to console)
* `/whois` (show login name for a nick)


## In the wild

Currently used on the Goons server (US-Texas).

## Credits

* [Panda](https://github.com/Lavos/panda/) - Similar project for TrackMania servers. Took many design cues from it
* Gbx.py by Marck
* Gamers.org API docs: [methods](http://www.gamers.org/tm2/docs/ListMethods.html) and [callbacks](http://www.gamers.org/tm2/docs/ListCallbacks.html)