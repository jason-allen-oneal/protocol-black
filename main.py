from panda3d.core import loadPrcFileData, WindowProperties
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock

loadPrcFileData(
    "",
    """
    window-type onscreen
    framebuffer-srgb false
    multisamples 0
    framebuffer-multisample false
    sync-video false
    """
)

from lib.screens import ScreenManager
from screens.splash import SplashScreen
from lib.Audio import AudioManager
from lib.Presence import PresenceSystem


class HorrorGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0, 0, 0, 1)

        props = WindowProperties()
        props.setTitle("Protocol Black")
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        if self.win is not None:
            self.win.requestProperties(props)

        # Disable Panda default camera controller
        self.disableMouse()

        self.accept("escape", self.userExit)

        self.player_start = None
        self.mouse_captured = False

        self.audio = AudioManager(self)
        self.presence = PresenceSystem()

        self.screens = ScreenManager(self)
        self.screens.change(SplashScreen(self, self.screens))

        self.taskMgr.add(self.update, "update")

    def capture_mouse(self):
        if self.mouse_captured or not self.win:
            return

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)

        self.mouse_captured = True

    def release_mouse(self):
        if self.win is None:
            return

        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)

        self.mouse_captured = False


    def update(self, task):
        dt = globalClock.getDt()
        self.screens.update(dt)
        return task.cont


if __name__ == "__main__":
    HorrorGame().run()
