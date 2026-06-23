import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Tuple

import py_trees as pt
from py_trees.behaviour import Behaviour

from bt.groot.registry import LoadContext, get as get_spec
from bt.sequence import Sequence as ReactiveSequenceImpl


class TreeLoadError(Exception):
    pass


CONTROL_NODES = {
    "Sequence",
    "ReactiveSequence",
    "SequenceWithMemory",
    "Fallback",
    "ReactiveFallback",
    "Selector",
    "Parallel",
}

DECORATOR_NODES = {
    "Inverter",
    "ForceSuccess",
    "ForceFailure",
    "RetryUntilSuccessful",
    "Repeat",
    "KeepRunningUntilFailure",
}


def load_tree(xml_path, ctx: LoadContext) -> Tuple[Behaviour, Dict[int, Behaviour], str]:
    path = Path(xml_path)
    raw = path.read_text(encoding="utf-8")
    root_elem = ET.fromstring(raw)

    main = _find_main_tree(root_elem)
    if main is None:
        raise TreeLoadError(f"No <BehaviorTree> found in {path}")

    children = list(main)
    if len(children) != 1:
        raise TreeLoadError(
            f"<BehaviorTree> must contain exactly one root node (got {len(children)}) in {path}"
        )

    uid_table: Dict[int, Behaviour] = {}
    counter = _Counter()
    root = _build(children[0], ctx, uid_table, counter)
    return root, uid_table, raw


def _find_main_tree(root_elem: ET.Element):
    main_id = root_elem.get("main_tree_to_execute")
    trees = root_elem.findall("BehaviorTree")
    if not trees:
        return None
    if main_id:
        for t in trees:
            if t.get("ID") == main_id:
                return t
    return trees[0]


class _Counter:
    def __init__(self):
        self.value = 0

    def next(self) -> int:
        self.value += 1
        return self.value


def _ports(elem: ET.Element) -> Dict[str, str]:
    return {k: v for k, v in elem.attrib.items() if k not in {"name", "ID"}}


def _label(elem: ET.Element, default: str) -> str:
    return elem.attrib.get("name") or default


def _build(elem, ctx, uid_table, counter) -> Behaviour:
    tag = elem.tag
    if tag in CONTROL_NODES:
        node = _build_control(elem, ctx, uid_table, counter)
    elif tag in DECORATOR_NODES:
        node = _build_decorator(elem, ctx, uid_table, counter)
    elif tag == "SubTree":
        raise TreeLoadError("<SubTree> is not supported yet")
    else:
        node = _build_leaf(elem, ctx)

    node._groot_uid = counter.next()
    uid_table[node._groot_uid] = node
    return node


def _build_control(elem, ctx, uid_table, counter) -> Behaviour:
    tag = elem.tag
    children = [_build(child, ctx, uid_table, counter) for child in list(elem)]
    label = _label(elem, tag)

    if tag in ("Sequence", "SequenceWithMemory"):
        return pt.composites.Sequence(name=label, memory=True, children=children)
    if tag == "ReactiveSequence":
        return ReactiveSequenceImpl(name=label, children=children)
    if tag in ("Fallback", "Selector"):
        return pt.composites.Selector(name=label, memory=True, children=children)
    if tag == "ReactiveFallback":
        return pt.composites.Selector(name=label, memory=False, children=children)
    if tag == "Parallel":
        policy_name = elem.attrib.get("success_policy", "SuccessOnAll")
        if policy_name == "SuccessOnOne":
            policy = pt.common.ParallelPolicy.SuccessOnOne()
        else:
            policy = pt.common.ParallelPolicy.SuccessOnAll(synchronise=False)
        return pt.composites.Parallel(name=label, policy=policy, children=children)
    raise TreeLoadError(f"Unhandled control node {tag!r}")


def _build_decorator(elem, ctx, uid_table, counter) -> Behaviour:
    tag = elem.tag
    inner_children = list(elem)
    if len(inner_children) != 1:
        raise TreeLoadError(f"Decorator <{tag}> must wrap exactly one child")
    child = _build(inner_children[0], ctx, uid_table, counter)
    label = _label(elem, tag)

    if tag == "Inverter":
        return pt.decorators.Inverter(child=child, name=label)
    if tag == "ForceSuccess":
        return _force(child, label, pt.common.Status.SUCCESS)
    if tag == "ForceFailure":
        return _force(child, label, pt.common.Status.FAILURE)
    if tag == "RetryUntilSuccessful":
        n = int(elem.attrib.get("num_attempts", "1"))
        return _retry(child, label, n)
    if tag == "Repeat":
        n = int(elem.attrib.get("num_cycles", "1"))
        return _repeat(child, label, n)
    if tag == "KeepRunningUntilFailure":
        return _keep_running_until_failure(child, label)
    raise TreeLoadError(f"Unhandled decorator {tag!r}")


def _force(child: Behaviour, name: str, status) -> Behaviour:
    class _Force(pt.decorators.Decorator):
        def update(self):
            if self.decorated.status == pt.common.Status.RUNNING:
                return pt.common.Status.RUNNING
            return status

    return _Force(child=child, name=name)


def _keep_running_until_failure(child: Behaviour, name: str) -> Behaviour:
    class _KRUF(pt.decorators.Decorator):
        def update(self):
            if self.decorated.status == pt.common.Status.FAILURE:
                return pt.common.Status.FAILURE
            return pt.common.Status.RUNNING

    return _KRUF(child=child, name=name)


def _retry(child: Behaviour, name: str, num_attempts: int) -> Behaviour:
    class _Retry(pt.decorators.Decorator):
        def __init__(self, child, name):
            super().__init__(child=child, name=name)
            self._attempts_left = num_attempts

        def initialise(self):
            self._attempts_left = num_attempts

        def update(self):
            s = self.decorated.status
            if s == pt.common.Status.SUCCESS:
                return pt.common.Status.SUCCESS
            if s == pt.common.Status.FAILURE:
                self._attempts_left -= 1
                if self._attempts_left <= 0:
                    return pt.common.Status.FAILURE
                return pt.common.Status.RUNNING
            return pt.common.Status.RUNNING

    return _Retry(child=child, name=name)


def _repeat(child: Behaviour, name: str, num_cycles: int) -> Behaviour:
    class _Repeat(pt.decorators.Decorator):
        def __init__(self, child, name):
            super().__init__(child=child, name=name)
            self._successes = 0

        def initialise(self):
            self._successes = 0

        def update(self):
            s = self.decorated.status
            if s == pt.common.Status.FAILURE:
                return pt.common.Status.FAILURE
            if s == pt.common.Status.SUCCESS:
                self._successes += 1
                if self._successes >= num_cycles:
                    return pt.common.Status.SUCCESS
                return pt.common.Status.RUNNING
            return pt.common.Status.RUNNING

    return _Repeat(child=child, name=name)


def _build_leaf(elem, ctx) -> Behaviour:
    spec = get_spec(elem.tag)
    try:
        node = spec.factory(ctx, _ports(elem))
    except KeyError as e:
        raise TreeLoadError(f"<{elem.tag}> missing required port {e}") from e
    label = elem.attrib.get("name")
    if label:
        node.name = label
    return node
