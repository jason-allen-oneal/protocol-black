from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from lib.screens import UIScreen
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton


class CreditsScreen(UIScreen):
    def __init__(self, base, manager):
        super().__init__(base)
        self.manager = manager

        # Background
        aspect = self.base.getAspectRatio()
        self.bg = OnscreenImage(
            image="assets/images/game-logo-no-text.png",
            parent=self.root,
            pos=(0, 0, 0),
            scale=(aspect, 1, 1),
        )
        self.bg.setTransparency(TransparencyAttrib.MAlpha)

        self.title = OnscreenText(
            text="Credits",
            pos=(0, 0.8),
            scale=0.15,
            fg=(1, 1, 1, 1),  # white
            parent=self.root,
        )

        self.credits_text = OnscreenText(
            text="Game developed by Jason O'Neal\n\nArtwork by Jason O'Neal\n\nMusic by Jason O'Neal",
            pos=(0, -0.1),
            scale=0.07,
            fg=(0.85, 0.85, 0.85, 1),  # light gray
            parent=self.root,
        )

        self.back_btn = DirectButton(
            text="Back to Title",
            scale=0.1,
            pos=(0, 0, -0.8),
            command=self.back_to_title,
            parent=self.root,
        )

    def back_to_title(self):
        from screens.title import TitleScreen
        self.manager.change(TitleScreen(self.base, self.manager))
    
    def enter(self):
        super().enter()
        self.base.release_mouse()
    
    def exit(self):
        for attr in (
            "bg",
            "title",
            "credits_text",
            "back_btn",
        ):
            obj = getattr(self, attr, None)
            if obj:
                obj.destroy()
                setattr(self, attr, None)

        super().exit()