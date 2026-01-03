# lib/props.py
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Literal

from panda3d.core import (
    NodePath,
    CollisionNode,
    CollisionBox,
    CollisionSphere,
    CollisionCapsule,
    BitMask32,
    LPoint3f,
    LVector3f,
)


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

DEFAULT_PROPS_ROOT = "assets/props"

# Collision masks: adapt these to your project if you already have masks defined.
MASK_PROP_SOLID = BitMask32.bit(1)     # solid blocking props
MASK_PROP_SENSOR = BitMask32.bit(2)    # non-blocking sensors/triggers (optional)


# ---------------------------------------------------------------------------
# META MODELS
# ---------------------------------------------------------------------------

CollisionShape = Literal["box", "sphere", "capsule"]

@dataclass(frozen=True)
class CollisionMeta:
    shape: CollisionShape
    dims: Tuple[float, float, float]          # box: (w,d,h), sphere: (r,0,0), capsule: (r, h, 0)
    offset: Tuple[float, float, float]        # center offset
    blocking: bool

@dataclass(frozen=True)
class RenderMeta:
    casts_shadow: bool
    two_sided: bool

@dataclass(frozen=True)
class PropMeta:
    prop_id: str
    model_path: str
    scale: float
    y_offset: float
    hpr: Tuple[float, float, float]
    collision: CollisionMeta
    render: RenderMeta


# ---------------------------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------------------------

class PropMetaError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise PropMetaError(msg)


def load_prop_meta(prop_dir: str, prop_id: str) -> PropMeta:
    """
    Loads and validates assets/props/<prop_id>/meta.json and expects model.glb.
    """
    meta_path = os.path.join(prop_dir, "meta.json")
    model_path = os.path.join(prop_dir, "model.glb")

    _require(os.path.isfile(meta_path), f"[{prop_id}] Missing meta.json at {meta_path}")
    _require(os.path.isfile(model_path), f"[{prop_id}] Missing model.glb at {model_path}")

    with open(meta_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    _require(isinstance(raw, dict), f"[{prop_id}] meta.json must be a JSON object")

    _require(raw.get("type") == "mesh", f"[{prop_id}] meta.json.type must be 'mesh'")

    scale = raw.get("scale", 1.0)
    y_offset = raw.get("y_offset", 0.0)
    hpr = raw.get("hpr", [0, 0, 0])

    _require(isinstance(scale, (int, float)) and scale > 0, f"[{prop_id}] scale must be > 0")
    _require(isinstance(y_offset, (int, float)), f"[{prop_id}] y_offset must be number")
    _require(isinstance(hpr, list) and len(hpr) == 3, f"[{prop_id}] hpr must be [h,p,r]")

    # collision
    col = raw.get("collision")
    _require(isinstance(col, dict), f"[{prop_id}] collision must be an object")

    shape = col.get("shape")
    _require(shape in ("box", "sphere", "capsule"), f"[{prop_id}] collision.shape must be box|sphere|capsule")

    dims = col.get("dims")
    _require(isinstance(dims, list) and len(dims) == 3, f"[{prop_id}] collision.dims must be [a,b,c] numbers")
    _require(all(isinstance(x, (int, float)) for x in dims), f"[{prop_id}] collision.dims entries must be numbers")

    offset = col.get("offset", [0, 0, 0])
    _require(isinstance(offset, list) and len(offset) == 3, f"[{prop_id}] collision.offset must be [x,y,z]")
    _require(all(isinstance(x, (int, float)) for x in offset), f"[{prop_id}] collision.offset entries must be numbers")

    blocking = col.get("blocking", True)
    _require(isinstance(blocking, bool), f"[{prop_id}] collision.blocking must be boolean")

    # render
    r = raw.get("render", {})
    _require(isinstance(r, dict), f"[{prop_id}] render must be an object if present")
    casts_shadow = bool(r.get("casts_shadow", False))
    two_sided = bool(r.get("two_sided", False))

    cm = CollisionMeta(
        shape=shape,  # type: ignore
        dims=(float(dims[0]), float(dims[1]), float(dims[2])),
        offset=(float(offset[0]), float(offset[1]), float(offset[2])),
        blocking=blocking,
    )

    rm = RenderMeta(casts_shadow=casts_shadow, two_sided=two_sided)

    return PropMeta(
        prop_id=prop_id,
        model_path=model_path,
        scale=float(scale),
        y_offset=float(y_offset),
        hpr=(float(hpr[0]), float(hpr[1]), float(hpr[2])),
        collision=cm,
        render=rm,
    )


# ---------------------------------------------------------------------------
# PROP REGISTRY (MODEL CACHING)
# ---------------------------------------------------------------------------

class PropRegistry:
    """
    Caches loaded models so multiple instances reuse the same source model.
    """
    def __init__(self, loader, props_root: str = DEFAULT_PROPS_ROOT):
        self.loader = loader
        self.props_root = props_root
        self._meta_cache: Dict[str, PropMeta] = {}
        self._model_cache: Dict[str, NodePath] = {}

    def get_meta(self, prop_id: str) -> PropMeta:
        if prop_id in self._meta_cache:
            return self._meta_cache[prop_id]
        prop_dir = os.path.join(self.props_root, prop_id)
        _require(os.path.isdir(prop_dir), f"[{prop_id}] Missing prop directory: {prop_dir}")
        meta = load_prop_meta(prop_dir, prop_id)
        self._meta_cache[prop_id] = meta
        return meta

    def get_source_model(self, prop_id: str) -> NodePath:
        """
        Returns a hidden source model NodePath (not parented). Instances should copyTo().
        """
        if prop_id in self._model_cache:
            return self._model_cache[prop_id]

        meta = self.get_meta(prop_id)

        # Requires panda3d-gltf for .glb in many Panda3D installs.
        model = self.loader.loadModel(meta.model_path)
        _require(not model.isEmpty(), f"[{prop_id}] loadModel returned empty for {meta.model_path}")

        model.clearModelNodes()
        model.flattenStrong()

        # Keep as hidden source
        model.detachNode()
        self._model_cache[prop_id] = model
        return model


# ---------------------------------------------------------------------------
# COLLISION PRIMITIVES
# ---------------------------------------------------------------------------

def build_collision_node(meta: PropMeta) -> CollisionNode:
    cmeta = meta.collision
    cnode = CollisionNode(f"col_{meta.prop_id}")
    cnode.setFromCollideMask(BitMask32.allOff())
    cnode.setIntoCollideMask(MASK_PROP_SOLID if cmeta.blocking else MASK_PROP_SENSOR)

    ox, oy, oz = cmeta.offset

    if cmeta.shape == "box":
        w, d, h = cmeta.dims
        _require(w > 0 and d > 0 and h > 0, f"[{meta.prop_id}] box dims must be > 0")
        # Panda3D CollisionBox uses center + half-extents
        solid = CollisionBox(
            LPoint3f(ox, oy, oz),
            w * 0.5,
            d * 0.5,
            h * 0.5,
        )
        cnode.addSolid(solid)

    elif cmeta.shape == "sphere":
        r, _, _ = cmeta.dims
        _require(r > 0, f"[{meta.prop_id}] sphere radius must be > 0")
        from panda3d.core import CollisionSphere
        solid = CollisionSphere(ox, oy, oz, r)
        cnode.addSolid(solid)

    elif cmeta.shape == "capsule":
        r, h, _ = cmeta.dims
        _require(r > 0 and h > 0, f"[{meta.prop_id}] capsule (r,h) must be > 0")
        # Capsule along Z; define endpoints
        z0 = oz - (h * 0.5)
        z1 = oz + (h * 0.5)
        solid = CollisionCapsule(ox, oy, z0, ox, oy, z1, r)
        cnode.addSolid(solid)

    else:
        raise PropMetaError(f"[{meta.prop_id}] Unknown collision shape: {cmeta.shape}")

    return cnode


# ---------------------------------------------------------------------------
# SPAWNING
# ---------------------------------------------------------------------------

def spawn_prop(
    registry: PropRegistry,
    parent: NodePath,
    prop_id: str,
    pos: Tuple[float, float, float],
    hpr: Optional[Tuple[float, float, float]] = None,
    name: Optional[str] = None,
) -> NodePath:
    """
    Spawns a prop instance under `parent`.
    Returns the top NodePath (prop root), which contains model + collision child.
    """
    meta = registry.get_meta(prop_id)
    source = registry.get_source_model(prop_id)

    root = parent.attachNewNode(name or f"prop_{prop_id}")
    x, y, z = pos
    root.setPos(x, y, z + meta.y_offset)

    # Rotation from meta plus optional override
    mh, mp, mr = meta.hpr
    if hpr is None:
        root.setHpr(mh, mp, mr)
    else:
        root.setHpr(hpr[0], hpr[1], hpr[2])

    root.setScale(meta.scale)

    # Model instance
    inst = source.copyTo(root)
    inst.setName(f"model_{prop_id}")

    # Render flags
    if meta.render.two_sided:
        inst.setTwoSided(True)

    # Collision
    cnode = build_collision_node(meta)
    cnp = root.attachNewNode(cnode)
    cnp.setName(f"coll_{prop_id}")

    return root
