# screens/splash.py

from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from lib.screens import UIScreen


class SplashScreen(UIScreen):
    def __init__(self, base, manager):
        super().__init__(base)
        self.manager = manager
        self.timer = 0.0

        self.image = OnscreenImage(
            image="assets/images/bluedot-logo.png",
            parent=self.root,          # UIScreen => root will be under aspect2d
            pos=(0, 0, 0),
            scale=1.0,                 # 1.0 roughly fills screen width on aspect2d
        )
        self.image.setTransparency(TransparencyAttrib.MAlpha)

        text = TextNode("splash")
        text.setText("Bluedot IT - Jason O'Neal - All rights reserved")
        text.setAlign(TextNode.ACenter)
        text.setTextScale(0.05)

        self.text_np = self.root.attachNewNode(text)
        self.text_np.setPos(0, 0, -0.85)

    def update(self, dt):
        self.timer += dt
        if self.timer > 4:
            from screens.title import TitleScreen
            self.manager.change(TitleScreen(self.base, self.manager))

    def exit(self):
        if self.image:
            self.image.destroy()
            self.image = None
        super().exit()