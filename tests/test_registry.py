"""Sanity check every registered Groot2 node instantiates with dummy ports.

Catches signature drift between bt/actions.py / bt/conditions.py and
bt/groot/registry.py.
"""
import pytest

from bt.groot.registry import LoadContext, all_specs


_FAKE_PORTS = {
    "item": "log",
    "amount": "1",
    "tier": "1",
    "block": "log",
    "material": "log",
    "specie": "Cow",
    "direction": "North",
    "position": "0 64 0",
}


class _StubAgent:
    pass


@pytest.mark.parametrize("spec", list(all_specs()), ids=lambda s: s.name)
def test_factory_constructs(spec):
    ctx = LoadContext(agent=_StubAgent())
    ports = {name: _FAKE_PORTS[name] for name in spec.ports}
    node = spec.factory(ctx, ports)
    assert hasattr(node, "name") and node.name
