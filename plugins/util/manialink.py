from jinja2 import Template


class ManiaLink:
    def __init__(self, path):
        linkfile = open(path)
        manialink_src = linkfile.read()
        linkfile.close()

        self.manialink = Template(manialink_src)

    def render(self, *args, **kwargs):
        return self.manialink.render(*args, **kwargs)

if __name__ == '__main__':
    test_link = ManiaLink("../manialinks/render_test.xml")
    print test_link.render(url="test")
