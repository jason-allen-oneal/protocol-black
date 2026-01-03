from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib, Vec4
from direct.interval.LerpInterval import LerpColorScaleInterval


class ScreenFader:
    def __init__(self, base):
        self.base = base

        self.overlay = OnscreenImage(
            image="assets/images/1x1-black.png",  # 1x1 black PNG
            parent=self.base.render2d,
            pos=(0, 0, 0),
            scale=(1, 1, 1),
        )
        self.overlay.setTransparency(TransparencyAttrib.MAlpha)
        self.overlay.setColorScale(0, 0, 0, 0)
        self.overlay.hide()

    def fade_out(self, duration=0.4):
        self.overlay.show()
        return LerpColorScaleInterval(
            self.overlay,
            duration,
            Vec4(0, 0, 0, 1),
            Vec4(0, 0, 0, 0),
        )

    def fade_in(self, duration=0.4):
        self.overlay.show()
        return LerpColorScaleInterval(
            self.overlay,
            duration,
            Vec4(0, 0, 0, 0),
            Vec4(0, 0, 0, 1),
        )
