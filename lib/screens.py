from panda3d.core import NodePath


class Screen:
    def __init__(self, base):
        self.base = base
        self.root = NodePath(self.__class__.__name__)

    def enter(self):
        self.root.reparentTo(self.base.render)

    def exit(self):
        self.root.detachNode()

    def update(self, dt):
        pass


class UIScreen(Screen):
    def enter(self):
        self.root.reparentTo(self.base.aspect2d)

    def exit(self):
        self.root.detachNode()


class ScreenManager:
    def __init__(self, base):
        self.base = base
        self.current = None

    def change(self, screen):
        if self.current:
            self.current.exit()
        self.current = screen
        self.current.enter()

    def update(self, dt):
        if self.current:
            self.current.update(dt)
