from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable

import numpy as np

from bt import actions, conditions
from utils.vectors import Direction


@dataclass
class LoadContext:
    agent: object


@dataclass
class NodeSpec:
    name: str
    kind: str
    factory: Callable[[LoadContext, Dict[str, str]], object]
    ports: Dict[str, str] = field(default_factory=dict)


_REGISTRY: Dict[str, NodeSpec] = {}


def register(name: str, kind: str, factory, ports=None) -> None:
    if name in _REGISTRY:
        raise ValueError(f"Node {name!r} already registered")
    _REGISTRY[name] = NodeSpec(name, kind, factory, ports or {})


def get(name: str) -> NodeSpec:
    if name not in _REGISTRY:
        raise KeyError(f"Unknown Groot2 node {name!r}. Registered: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


def all_specs() -> Iterable[NodeSpec]:
    return _REGISTRY.values()


def _int(value: str) -> int:
    return int(value)


def _direction(value: str) -> Direction:
    return Direction[value]


def _position(value: str) -> np.ndarray:
    parts = [p for p in value.replace(",", " ").split() if p]
    if len(parts) != 3:
        raise ValueError(f"Position port expects 'x y z' (got {value!r})")
    return np.array([float(p) for p in parts])


# --- Actions ---

register(
    "Craft", "Action",
    lambda ctx, p: actions.Craft(ctx.agent, p["item"], _int(p.get("amount", "1"))),
    ports={"item": "input", "amount": "input"},
)
register(
    "Melt", "Action",
    lambda ctx, p: actions.Melt(ctx.agent, p["item"], _int(p.get("amount", "1"))),
    ports={"item": "input", "amount": "input"},
)
register(
    "Equip", "Action",
    lambda ctx, p: actions.Equip(ctx.agent, p["item"]),
    ports={"item": "input"},
)
register(
    "EquipBestPickAxe", "Action",
    lambda ctx, p: actions.EquipBestPickAxe(ctx.agent, _int(p["tier"])),
    ports={"tier": "input"},
)
register(
    "JumpIfStuck", "Action",
    lambda ctx, p: actions.JumpIfStuck(ctx.agent),
)
register(
    "PickupItem", "Action",
    lambda ctx, p: actions.PickupItem(ctx.agent, p["item"]),
    ports={"item": "input"},
)
register(
    "GoToAnimal", "Action",
    lambda ctx, p: actions.GoToAnimal(ctx.agent, p.get("specie") or None),
    ports={"specie": "input"},
)
register(
    "GoToEnemy", "Action",
    lambda ctx, p: actions.GoToEnemy(ctx.agent),
)
register(
    "GoToBlock", "Action",
    lambda ctx, p: actions.GoToBlock(ctx.agent, p["block"]),
    ports={"block": "input"},
)
register(
    "GoToPosition", "Action",
    lambda ctx, p: actions.GoToPosition(ctx.agent, _position(p["position"])),
    ports={"position": "input"},
)
register(
    "MineMaterial", "Action",
    lambda ctx, p: actions.MineMaterial(ctx.agent, p["material"]),
    ports={"material": "input"},
)
register(
    "AttackAnimal", "Action",
    lambda ctx, p: actions.AttackAnimal(ctx.agent, p.get("specie") or None),
    ports={"specie": "input"},
)
register(
    "DefeatEnemy", "Action",
    lambda ctx, p: actions.DefeatEnemy(ctx.agent),
)
register(
    "PlaceBlockAtPosition", "Action",
    lambda ctx, p: actions.PlaceBlockAtPosition(ctx.agent, p["block"], _position(p["position"])),
    ports={"block": "input", "position": "input"},
)
register(
    "DigDownwardsToMaterial", "Action",
    lambda ctx, p: actions.DigDownwardsToMaterial(ctx.agent, p["material"]),
    ports={"material": "input"},
)
register(
    "ExploreInDirection", "Action",
    lambda ctx, p: actions.ExploreInDirection(ctx.agent, _direction(p.get("direction", "North"))),
    ports={"direction": "input"},
)

# --- Conditions ---

register(
    "HasItem", "Condition",
    lambda ctx, p: conditions.HasItem(ctx.agent, p["item"], _int(p.get("amount", "1"))),
    ports={"item": "input", "amount": "input"},
)
register(
    "HasItemEquipped", "Condition",
    lambda ctx, p: conditions.HasItemEquipped(ctx.agent, p["item"]),
    ports={"item": "input"},
)
register(
    "HasPickaxeByMinimumTier", "Condition",
    lambda ctx, p: conditions.HasPickaxeByMinimumTier(ctx.agent, _int(p["tier"])),
    ports={"tier": "input"},
)
register(
    "HasBestPickaxeByMinimumTierEquipped", "Condition",
    lambda ctx, p: conditions.HasBestPickaxeByMinimumTierEquipped(ctx.agent, _int(p["tier"])),
    ports={"tier": "input"},
)
register(
    "HasPickupNearby", "Condition",
    lambda ctx, p: conditions.HasPickupNearby(ctx.agent, p["item"]),
    ports={"item": "input"},
)
register(
    "HasNoEnemyNearby", "Condition",
    lambda ctx, p: conditions.HasNoEnemyNearby(ctx.agent),
)
register(
    "IsBlockWithinReach", "Condition",
    lambda ctx, p: conditions.IsBlockWithinReach(ctx.agent, p["block"]),
    ports={"block": "input"},
)
register(
    "IsBlockObservable", "Condition",
    lambda ctx, p: conditions.IsBlockObservable(ctx.agent, p["block"]),
    ports={"block": "input"},
)
register(
    "IsPositionWithinReach", "Condition",
    lambda ctx, p: conditions.IsPositionWithinReach(ctx.agent, _position(p["position"])),
    ports={"position": "input"},
)
register(
    "IsAnimalWithinReach", "Condition",
    lambda ctx, p: conditions.IsAnimalWithinReach(ctx.agent, p["specie"]),
    ports={"specie": "input"},
)
register(
    "IsEnemyWithinReach", "Condition",
    lambda ctx, p: conditions.IsEnemyWithinReach(ctx.agent),
)
register(
    "IsAnimalObservable", "Condition",
    lambda ctx, p: conditions.IsAnimalObservable(ctx.agent, p["specie"]),
    ports={"specie": "input"},
)
register(
    "IsBlockAtPosition", "Condition",
    lambda ctx, p: conditions.IsBlockAtPosition(ctx.agent, p["block"], _position(p["position"])),
    ports={"block": "input", "position": "input"},
)
