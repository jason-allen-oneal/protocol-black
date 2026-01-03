from panda3d.core import (
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    GeomTriangles,
    Geom,
    GeomNode,
    NodePath,
    Vec3,
    SamplerState,
    CollisionNode,
    CollisionBox,
)

from lib.constants import TILE_SIZE, WALL_HEIGHT, PLAYER_EYE_HEIGHT
from lib.textures import TEXTURES

# ------------------------------------------------------------
# MAP LEGEND
# ------------------------------------------------------------
WALL_CHARS = {"#", "*"}
DOOR_CHARS = {"$", "@", "-", "+"}
SOLID_CHARS = WALL_CHARS | DOOR_CHARS
PLAYER_START = "X"

# ------------------------------------------------------------
# DOOR TEXTURE UV TUNING
# ------------------------------------------------------------
DOOR_U_SCALE = 1.18
DOOR_U_MARGIN = 0.2
DOOR_V_SCALE = 1.0
DOOR_V_MARGIN = 0.0

# ------------------------------------------------------------
# LIGHTING
# ------------------------------------------------------------
def add_lighting(base):
    from panda3d.core import AmbientLight, DirectionalLight, Vec4

    ambient = AmbientLight("ambient")
    ambient.setColor(Vec4(0.25, 0.25, 0.25, 1))
    base.render.setLight(base.render.attachNewNode(ambient))

    sun = DirectionalLight("sun")
    sun.setColor(Vec4(0.85, 0.8, 0.75, 1))
    sun_np = base.render.attachNewNode(sun)
    sun_np.setHpr(45, -60, 0)
    base.render.setLight(sun_np)

# ------------------------------------------------------------
# WORLD BUILD
# ------------------------------------------------------------
def build_wing(base, map_data, pwing):
    wing = base.render.attachNewNode(f"wing_{pwing}")

    h = len(map_data)
    w = len(map_data[0])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def is_solid(x, y):
        if not in_bounds(x, y):
            return False
        return map_data[y][x] in SOLID_CHARS

    for y, row in enumerate(map_data):
        for x, char in enumerate(row):
            wx = x * TILE_SIZE
            wy = y * TILE_SIZE

            if char in SOLID_CHARS:
                block = build_wall_block(
                    pwing,
                    tile_char=char,
                    north=not is_solid(x, y - 1),
                    south=not is_solid(x, y + 1),
                    west=not is_solid(x - 1, y),
                    east=not is_solid(x + 1, y),
                )
                block.reparentTo(wing)
                block.setPos(wx, wy, 0)

                if char in DOOR_CHARS:
                    block.setTag("door", "1")
                    block.setTag("door_x", str(x))
                    block.setTag("door_y", str(y))
                    if char in {"@", "-"}:
                        block.setTag("door_unlocked", "1")
                    else:
                        block.setTag("door_unlocked", "0")

                # ---------------- COLLISION ----------------
                cnode = CollisionNode("solid")
                cnode.addSolid(
                    CollisionBox(
                        Vec3(
                            TILE_SIZE * 0.5,
                            TILE_SIZE * 0.5,
                            WALL_HEIGHT * 0.5,
                        ),
                        TILE_SIZE * 0.5,
                        TILE_SIZE * 0.5,
                        WALL_HEIGHT * 0.5,
                    )
                )
                cnode.setIntoCollideMask(0x1)
                block.attachNewNode(cnode)

            elif char == PLAYER_START:
                base.player_start = Vec3(
                    wx + TILE_SIZE * 0.5,
                    wy + TILE_SIZE * 0.5,
                    PLAYER_EYE_HEIGHT,
                )

    build_floor(wing, map_data, pwing)
    build_ceiling(wing, map_data, pwing)

# ------------------------------------------------------------
# WALL / DOOR BLOCK
# ------------------------------------------------------------
def build_wall_block(pwing, tile_char, north, south, west, east):
    fmt = GeomVertexFormat.getV3n3t2()
    vdata = GeomVertexData("wall", fmt, Geom.UHStatic)

    v = GeomVertexWriter(vdata, "vertex")
    n = GeomVertexWriter(vdata, "normal")
    t = GeomVertexWriter(vdata, "texcoord")

    s = TILE_SIZE
    h = WALL_HEIGHT
    tris = GeomTriangles(Geom.UHStatic)
    idx = 0

    if tile_char in DOOR_CHARS:
        u0 = (0.0 + DOOR_U_MARGIN) * DOOR_U_SCALE
        u1 = (1.0 - DOOR_U_MARGIN) * DOOR_U_SCALE
        v0 = (0.0 + DOOR_V_MARGIN) * DOOR_V_SCALE
        v1 = (1.0 - DOOR_V_MARGIN) * DOOR_V_SCALE
    else:
        u0, u1 = 0.0, 1.0
        v0, v1 = 0.0, 1.0

    def quad(verts, normal):
        nonlocal idx
        for x, y, z, u, v_ in verts:
            v.addData3(x, y, z)
            n.addData3(*normal)
            t.addData2(u, v_)
        tris.addVertices(idx, idx + 1, idx + 2)
        tris.addVertices(idx, idx + 2, idx + 3)
        idx += 4

    if north:
        quad([(0, 0, 0, u0, v0), (s, 0, 0, u1, v0), (s, 0, h, u1, v1), (0, 0, h, u0, v1)], (0, -1, 0))
    if south:
        quad([(s, s, 0, u0, v0), (0, s, 0, u1, v0), (0, s, h, u1, v1), (s, s, h, u0, v1)], (0, 1, 0))
    if west:
        quad([(0, s, 0, u0, v0), (0, 0, 0, u1, v0), (0, 0, h, u1, v1), (0, s, h, u0, v1)], (-1, 0, 0))
    if east:
        quad([(s, 0, 0, u0, v0), (s, s, 0, u1, v0), (s, s, h, u1, v1), (s, 0, h, u0, v1)], (1, 0, 0))

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode("wall_block")
    node.addGeom(geom)

    np = NodePath(node)

    if tile_char in DOOR_CHARS:
        tex = TEXTURES["door_old"]
        tex.setWrapU(SamplerState.WM_clamp)
        tex.setWrapV(SamplerState.WM_clamp)
        np.setTag("interactable", "door")
    else:
        tex = TEXTURES[f"{pwing}_wall"]

    np.setTexture(tex)
    return np

# ------------------------------------------------------------
# FLOOR / CEILING
# ------------------------------------------------------------
def build_floor(parent, map_data, pwing):
    from panda3d.core import CardMaker

    cm = CardMaker("floor")
    cm.setFrame(0, TILE_SIZE, 0, TILE_SIZE)
    tex = TEXTURES[f"{pwing}_floor"]

    for y, row in enumerate(map_data):
        for x, char in enumerate(row):
            if char in SOLID_CHARS:
                continue
            tile = parent.attachNewNode(cm.generate())
            tile.setPos(x * TILE_SIZE, y * TILE_SIZE, 0)
            tile.setP(-90)
            tile.setTexture(tex)

def build_ceiling(parent, map_data, pwing):
    from panda3d.core import CardMaker

    cm = CardMaker("ceiling")
    cm.setFrame(0, TILE_SIZE, 0, TILE_SIZE)
    tex = TEXTURES[f"{pwing}_ceiling"]

    for y, row in enumerate(map_data):
        for x, _ in enumerate(row):
            tile = parent.attachNewNode(cm.generate())
            tile.setPos(x * TILE_SIZE, y * TILE_SIZE, WALL_HEIGHT)
            tile.setP(90)
            tile.setTexture(tex)
