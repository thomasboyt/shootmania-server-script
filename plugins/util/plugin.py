import importlib
from commands import *


class Plugin(object):
    def __init__(self, server, config):
        self.server = server
        self.config = config
        self.callbacks = []
        self.commands = {}

    def add_callback(self, callback_name, callback_func):
        self.callbacks.append([callback_name, callback_func])

    def add_command(self, *args, **kwargs):
        self.commands[args[0]] = Command(*args, **kwargs)


# allows plugins to define multiple callback methods for a given server callback
# basically:
# plugins define callbacks they need as ["server method", callback_method]
# plugin_loader concats these together and creates a CallbacksHandler() with them
# callbackshandler creates Callback objects that handle multiple callbacks for one
#   server method
class CallbacksHandler:
    def __init__(self, server, callbacks):
        self.callbacks = {}
        self.server = server

        for callback in callbacks:
            name = callback[0]
            method = callback[1]
            self.add(name, method)

    def add(self, name, callback):
        if name not in self.callbacks:
            self.callbacks[name] = Callback(name, self.server)
        self.callbacks[name].cbs.append(callback)


class Callback:
    def __init__(self, name, server):
        self.cbs = []
        server.add_method(name, self.run)

    def run(self, *args):
        for callback in self.cbs:
            callback(*args)


# todo: exceptions for missing plugins
def plugin_loader(server, plugins_config):
    commands = {}
    callbacks = []

    for name, config in plugins_config.iteritems():
        Plugin = importlib.import_module("plugins." + name).ExportPlugin
        plugin = Plugin(server, config)
        commands = dict(commands.items() + plugin.commands.items())
        callbacks += plugin.callbacks

    return (ChatCommands(commands), CallbacksHandler(server, callbacks))
