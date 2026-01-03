import os
import json
from direct.gui.DirectGui import (
    DirectButton,
    DirectLabel,
    DirectScrolledList,
)
from panda3d.core import TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from lib.screens import UIScreen
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.OnscreenText import OnscreenText


SAVE_DIR = "data/saves"


class LoadScreen(UIScreen):
    def __init__(self, base, manager):
        super().__init__(base)
        self.manager = manager

        self.selected_save = None
        self.save_buttons = []

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
            text="Load Game",
            pos=(0, 0.8),
            scale=0.15,
            fg=(1, 1, 1, 1),  # white
            parent=self.root,
        )

        self._build_save_list()
        self._build_buttons()

    # ------------------------------------------------------------
    # SAVE LIST
    # ------------------------------------------------------------

    def _build_save_list(self):
        saves = self._get_save_files()

        if not saves:
            self.title = OnscreenText(
                text="No saves found.",
                pos=(0, 0, 0.2),
                scale=0.12,
                fg=(1, 1, 1, 1),  # white
                parent=self.root,
            )
            self.save_list = None
            return

        self.no_saves = None

        self.save_list = DirectScrolledList(
            parent=self.root,
            items=[],
            frameSize=(-0.6, 0.6, -0.35, 0.35),
            pos=(0, 0, 0.15),
            numItemsVisible=6,
            forceHeight=0.1,
            itemFrame_frameSize=(-0.55, 0.55, -0.05, 0.05),
            itemFrame_pos=(0, 0, 0),
        )

        for name in saves:
            btn = DirectButton(
                text=name,
                scale=0.07,
                command=self._select_save,
                extraArgs=[name],
            )
            self.save_buttons.append(btn)
            self.save_list.addItem(btn)

    def _get_save_files(self):
        if not os.path.isdir(SAVE_DIR):
            return []

        return sorted(
            f for f in os.listdir(SAVE_DIR)
            if os.path.isfile(os.path.join(SAVE_DIR, f))
        )

    def _select_save(self, filename):
        self.selected_save = filename
        self.load_btn["state"] = DGG.NORMAL

    # ------------------------------------------------------------
    # BUTTONS
    # ------------------------------------------------------------

    def _build_buttons(self):
        self.load_btn = DirectButton(
            text="LOAD",
            scale=0.08,
            pos=(-0.25, 0, -0.65),
            command=self._load_selected,
            parent=self.root,
        )
        self.load_btn["state"] = DGG.DISABLED

        self.back_btn = DirectButton(
            text="BACK",
            scale=0.08,
            pos=(0.25, 0, -0.65),
            command=self._go_back,
            parent=self.root,
        )

    def _load_selected(self):
        if not self.selected_save:
            return

        path = os.path.join(SAVE_DIR, self.selected_save)

        with open(path, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        from screens.game import GameScreen
        self.manager.change(GameScreen(self.base, self.manager, save_data=save_data))

        print(f"Loading save: {path}")

    def _go_back(self):
        from screens.title import TitleScreen
        self.manager.change(TitleScreen(self.base, self.manager))

    def enter(self):
        super().enter()
        self.base.release_mouse()

    def exit(self):
        for attr in (
            "bg",
            "title",
            "save_list",
            "no_saves",
            "load_btn",
            "back_btn",
        ):
            obj = getattr(self, attr, None)
            if obj:
                obj.destroy()
                setattr(self, attr, None)

        for btn in self.save_buttons:
            btn.destroy()
        self.save_buttons.clear()

        super().exit()
