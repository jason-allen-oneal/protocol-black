# screens/game.py
from lib.World import add_lighting, build_wing
from lib.screens import Screen
from lib.Player import Player
from lib.maps import MAP_DATA


class GameScreen(Screen):
    def __init__(self, base, manager, save_data=None):
        super().__init__(base)
        self.manager = manager
        self.save_data = save_data
        self.player = None

    def enter(self):
        super().enter()

        self.base.capture_mouse()

        # --- LIGHTING ---
        add_lighting(self.base)

        # --- BUILD WORLD FIRST ---
        wing = (
            self.save_data.get("wing", "main_floor")
            if self.save_data
            else "main_floor"
        )

        build_wing(self.base, MAP_DATA[wing], wing)

        assert self.base.player_start is not None, "No player start (X) in map!"

        # --- CREATE PLAYER ---
        self.player = Player(self.base, save_data=self.save_data)

        # IMPORTANT: player node is at FLOOR level, camera handles eye height
        self.player.node.setPos(
            self.base.player_start.x,
            self.base.player_start.y,
            0,
        )

        # --- CAMERA SAFETY ---
        self.base.camLens.setNearFar(0.1, 1000)

        # DEBUG (can remove later)
        print("PLAYER START:", self.base.player_start)
        print("PLAYER NODE POS:", self.player.node.getPos(self.base.render))
        print("CAMERA WORLD POS:", self.base.camera.getPos(self.base.render))
        self.base.render.ls()

    def update(self, dt):
        print("GAME UPDATE", self.base.mouse_captured)
        if self.player:
            self.player.update(dt)

