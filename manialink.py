import xml.etree.ElementTree as et


class Window:
    def __init__(self):
        self.root = et.Element("manialink")
        self.root.set("version", "1")

    def addElement(self, parent, element, **kargs):
        elem = et.SubElement(parent, element)
        for key, val in kargs.iteritems():
            elem.set(key, val)
        return elem

    def render(self):
        declaration = '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>\n'
        return declaration + et.tostring(self.root)


if __name__ == '__main__':
    test_window = Window()
    test_window.addElement(test_window.root, "label", text="Test label text")
    test_window.render()
