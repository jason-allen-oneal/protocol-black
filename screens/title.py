from direct.gui.DirectGui import DirectButton
from panda3d.core import TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from lib.screens import UIScreen


class TitleScreen(UIScreen):
    def __init__(self, base, manager):
        super().__init__(base)
        self.manager = manager

        # Background
        self.bg = OnscreenImage(
            image="assets/images/game-logo.png",
            parent=self.base.render2d,
            pos=(0, 0, 0),
            scale=(1, 1, 1),
        )
        self.bg.setTransparency(TransparencyAttrib.MAlpha)

        # START BUTTON
        self.start_btn = DirectButton(
            text="NEW",
            scale=0.1,
            pos=(0, 0, -0.4),
            command=self.new_game,
            parent=self.root,
        )

        self.load_btn = DirectButton(
            text="LOAD",
            scale=0.1,
            pos=(0, 0, -0.55),
            command=self.load_game,
            parent=self.root,
        )

        self.credits_btn = DirectButton(
            text="CREDITS",
            scale=0.1,
            pos=(0, 0, -0.7),
            command=self.show_credits,
            parent=self.root,
        )

        self.quit_btn = DirectButton(
            text="QUIT",
            scale=0.1,
            pos=(0, 0, -0.85),
            command=self.quit_game,
            parent=self.root,
        )

    def load_game(self):
        from screens.load import LoadScreen
        self.manager.change(LoadScreen(self.base, self.manager))

    def show_credits(self):
        from screens.credits import CreditsScreen
        self.manager.change(CreditsScreen(self.base, self.manager))

    def quit_game(self):
        self.base.userExit()

    def new_game(self):
        from screens.game import GameScreen
        self.manager.change(GameScreen(self.base, self.manager))
    
    def enter(self):
        super().enter()
        self.base.release_mouse()

    def exit(self):
        for attr in (
            "bg",
            "start_btn",
            "load_btn",
            "credits_btn",
            "quit_btn",
        ):
            obj = getattr(self, attr, None)
            if obj:
                obj.destroy()
                setattr(self, attr, None)

        super().exit()
