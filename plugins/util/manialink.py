# if your plugin uses a ManiaLink template, make sure you tell users to install
# jinja2 via "pip install jinja2"
from jinja2 import Template


class ManiaLink:
    def __init__(self, path):
        linkfile = open(path)
        manialink_src = linkfile.read()
        linkfile.close()

        self.manialink = Template(manialink_src)

    def __call__(self, *args, **kwargs):
        return self.manialink.render(*args, **kwargs)