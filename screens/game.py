# screens/game.py
from lib.World import add_lighting, build_wing, compute_spawn_heading
from lib.constants import TILE_SIZE
from lib.screens import Screen
from lib.Player import Player
from lib.maps import MAP_DATA

from lib.ObjectManager import PropManager, PropSpawn


class GameScreen(Screen):
    def __init__(self, base, manager, save_data=None):
        super().__init__(base)
        self.manager = manager
        self.save_data = save_data
        self.player = None
        self.props = None

    def enter(self):
        super().enter()

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

        # --- PROPS ---
        self.props = PropManager(
            base=self.base,
            parent=self.base.render,
            props_root="assets/objects",
        )

        self.props.spawn_batch([
            PropSpawn("chair", (10.5, 6.0, 0.0), (90, 0, 0)),
        ])

        # --- CREATE PLAYER ---
        self.player = Player(self.base, save_data=self.save_data)
        self.player.node.setPos(
            self.base.player_start.x,
            self.base.player_start.y,
            0,
        )
        tx = int(self.base.player_start.x // TILE_SIZE)
        ty = int(self.base.player_start.y // TILE_SIZE)

        heading = compute_spawn_heading(MAP_DATA[wing], tx, ty)
        self.player.node.setH(heading)

        # --- CAMERA SAFETY ---
        self.base.camLens.setNearFar(0.1, 1000)

        # --- NOW CAPTURE MOUSE ---
        self.base.capture_mouse()

        self.player.pitch = 0.0
        self.player.node.setH(self.player.node.getH())
        self.player.camera.setP(0)

        # DEBUG
        self.base.render.ls()


    def update(self, dt):
        if self.player:
            self.player.update(dt)
