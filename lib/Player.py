from panda3d.core import (
    Vec3,
    CollisionNode,
    CollisionCapsule,
    CollisionTraverser,
    CollisionHandlerPusher,
    CollisionRay,
    CollisionHandlerQueue,
    TextNode,
)
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.InputStateGlobal import inputState
from lib.constants import PLAYER_EYE_HEIGHT, TILE_SIZE


class Player:
    def __init__(self, base, save_data=None):
        self.base = base

        # ------------------------------------------------------------
        # PLAYER NODE
        # ------------------------------------------------------------
        self.node = base.render.attachNewNode("player")
        self.node.setPos(0, 0, 0)

        # ------------------------------------------------------------
        # CAMERA
        # ------------------------------------------------------------
        self.camera = base.camera
        self.camera.reparentTo(self.node)
        self.camera.setPos(0, 0, PLAYER_EYE_HEIGHT)
        self.camera.setHpr(0, 0, 0)

        # ------------------------------------------------------------
        # MOVEMENT
        # ------------------------------------------------------------
        self.speed = 8.0
        self.pitch = 0.0

        # ------------------------------------------------------------
        # COLLISION
        # ------------------------------------------------------------
        self._setup_collision()

        # ------------------------------------------------------------
        # DOOR RAY
        # ------------------------------------------------------------
        self._setup_door_ray()

        # ------------------------------------------------------------
        # UI MESSAGE (STATUS FEEDBACK)
        # ------------------------------------------------------------
        self.message = OnscreenText(
            text="",
            pos=(0, -0.85),
            scale=0.055,
            fg=(1, 0.2, 0.2, 1),  # red = denied
            align=TextNode.ACenter,
            mayChange=True,
        )

        self._bind_inputs()

    # ------------------------------------------------------------
    # COLLISION
    # ------------------------------------------------------------
    def _setup_collision(self):
        cnode = CollisionNode("playerCollider")
        cnode.addSolid(
            CollisionCapsule(
                Vec3(0, 0, 0.5),
                Vec3(0, 0, PLAYER_EYE_HEIGHT),
                0.35,
            )
        )
        cnode.setFromCollideMask(0x1)
        cnode.setIntoCollideMask(0)

        self.collider_np = self.node.attachNewNode(cnode)

        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.collider_np, self.node)

        self.traverser = CollisionTraverser("playerTraverser")
        self.traverser.addCollider(self.collider_np, self.pusher)

    # ------------------------------------------------------------
    # DOOR RAY
    # ------------------------------------------------------------
    def _setup_door_ray(self):
        self.door_ray = CollisionRay()
        self.door_ray.setOrigin(0, 0, PLAYER_EYE_HEIGHT * 0.9)
        self.door_ray.setDirection(0, 1, 0)

        ray_node = CollisionNode("doorRay")
        ray_node.addSolid(self.door_ray)
        ray_node.setFromCollideMask(0x1)
        ray_node.setIntoCollideMask(0)

        self.door_ray_np = self.camera.attachNewNode(ray_node)

        self.door_queue = CollisionHandlerQueue()
        self.door_traverser = CollisionTraverser("doorTraverser")
        self.door_traverser.addCollider(self.door_ray_np, self.door_queue)

    # ------------------------------------------------------------
    # INPUT
    # ------------------------------------------------------------
    def _bind_inputs(self):
        inputState.watchWithModifiers("forward", "w")
        inputState.watchWithModifiers("back", "s")
        inputState.watchWithModifiers("left", "a")
        inputState.watchWithModifiers("right", "d")

        inputState.watchWithModifiers("forward2", "arrow_up")
        inputState.watchWithModifiers("back2", "arrow_down")
        inputState.watchWithModifiers("left2", "arrow_left")
        inputState.watchWithModifiers("right2", "arrow_right")

        # SPACE = interact
        self.base.accept("space", self._try_use_door)

        self.base.accept("mouse1", self.base.capture_mouse)
        self.base.accept("m", self.base.release_mouse)

    # ------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------
    def update(self, dt):
        if self.base.mouse_captured:
            self._mouse_look()

        self._movement(dt)
        self.traverser.traverse(self.base.render)

    # ------------------------------------------------------------
    # MESSAGE HANDLING
    # ------------------------------------------------------------
    def _show_message(self, text, duration=2.0):
        self.message.setText(text)
        self.base.taskMgr.remove("clearMessage")
        self.base.taskMgr.doMethodLater(
            duration,
            lambda t: self.message.setText(""),
            "clearMessage",
        )

    # ------------------------------------------------------------
    # DOOR INTERACTION
    # ------------------------------------------------------------
    def _try_use_door(self):
        self.door_traverser.traverse(self.base.render)
        if self.door_queue.getNumEntries() == 0:
            return

        self.door_queue.sortEntries()
        entry = self.door_queue.getEntry(0)
        np = entry.getIntoNodePath()

        # Walk up to the wall tile node that owns the door tags
        while np and not np.hasTag("door"):
            np = np.getParent()

        if not np:
            return

        # Locked door feedback
        if np.getTag("door_unlocked") != "1":
            self._show_message("LOCKED — ACCESS DENIED")
            return

        # --------------------------------------------------------
        # TELEPORT THROUGH UNLOCKED DOOR
        # --------------------------------------------------------
        door_pos = np.getPos(self.base.render)
        cx = door_pos.x + TILE_SIZE * 0.5
        cy = door_pos.y + TILE_SIZE * 0.5

        player_pos = self.node.getPos(self.base.render)
        dx = player_pos.x - cx
        dy = player_pos.y - cy

        hop = TILE_SIZE * 0.65

        if abs(dx) > abs(dy):
            new_pos = Vec3(cx - hop if dx > 0 else cx + hop, cy, player_pos.z)
        else:
            new_pos = Vec3(cx, cy - hop if dy > 0 else cy + hop, player_pos.z)

        self.node.setPos(self.base.render, new_pos)
        self.traverser.traverse(self.base.render)

    # ------------------------------------------------------------
    # MOUSE LOOK
    # ------------------------------------------------------------
    def _mouse_look(self):
        if not self.base.mouseWatcherNode.hasMouse():
            return

        win = self.base.win
        if not win:
            return

        cx = win.getXSize() // 2
        cy = win.getYSize() // 2

        md = win.getPointer(0)
        dx = md.getX() - cx
        dy = md.getY() - cy

        # Recenter immediately
        win.movePointer(0, cx, cy)

        sensitivity = 0.15
        max_pitch = 75.0

        # Yaw
        self.node.setH(self.node.getH() - dx * sensitivity)

        # Pitch
        self.pitch -= dy * sensitivity
        self.pitch = max(-max_pitch, min(max_pitch, self.pitch))
        self.node.setP(self.pitch)


    # ------------------------------------------------------------
    # MOVEMENT
    # ------------------------------------------------------------
    def _movement(self, dt):
        direction = Vec3(0, 0, 0)

        if inputState.isSet("forward") or inputState.isSet("forward2"):
            direction.y += 1
        if inputState.isSet("back") or inputState.isSet("back2"):
            direction.y -= 1
        if inputState.isSet("left") or inputState.isSet("left2"):
            direction.x -= 1
        if inputState.isSet("right") or inputState.isSet("right2"):
            direction.x += 1

        if direction.lengthSquared() > 0:
            direction.normalize()
            self.node.setPos(self.node, direction * self.speed * dt)

