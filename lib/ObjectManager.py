# lib/prop_manager.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from panda3d.core import NodePath

from lib.objects import PropRegistry, spawn_prop


@dataclass(frozen=True)
class PropSpawn:
    prop_id: str
    pos: Tuple[float, float, float]
    hpr: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    name: Optional[str] = None


class PropManager:
    def __init__(self, base, parent: NodePath, props_root: str = "assets/objects"):
        """
        base: ShowBase
        parent: NodePath under which props will be attached (typically render or a wing/room node)
        """
        self.base = base
        self.parent = parent
        self.registry = PropRegistry(base.loader, props_root=props_root)

    def spawn(self, prop_id: str, pos: Tuple[float, float, float], hpr=(0.0, 0.0, 0.0), name: Optional[str] = None) -> NodePath:
        return spawn_prop(
            registry=self.registry,
            parent=self.parent,
            prop_id=prop_id,
            pos=pos,
            hpr=hpr,
            name=name,
        )

    def spawn_batch(self, spawns: List[PropSpawn]) -> List[NodePath]:
        out: List[NodePath] = []
        for s in spawns:
            out.append(self.spawn(s.prop_id, s.pos, s.hpr, s.name))
        return out
