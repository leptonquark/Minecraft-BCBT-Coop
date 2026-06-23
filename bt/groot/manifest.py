"""Emit a <TreeNodesModel> manifest describing the available custom nodes.

Groot2 reads this section from a tree XML (or from the FULLTREE reply) to
populate its node palette. Keeping this generated from the registry means the
visual editor always reflects the current Python node set.
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom

from bt.groot.registry import all_specs


def build_tree_nodes_model() -> ET.Element:
    model = ET.Element("TreeNodesModel")
    for spec in all_specs():
        node = ET.SubElement(model, spec.kind)
        node.set("ID", spec.name)
        for port_name, direction in spec.ports.items():
            tag = {"input": "input_port", "output": "output_port"}.get(direction, "input_port")
            port = ET.SubElement(node, tag)
            port.set("name", port_name)
    return model


def render(pretty: bool = True) -> str:
    model = build_tree_nodes_model()
    rough = ET.tostring(model, encoding="utf-8")
    if pretty:
        return minidom.parseString(rough).toprettyxml(indent="  ")
    return rough.decode("utf-8")


def write(path) -> None:
    from pathlib import Path
    Path(path).write_text(render(pretty=True), encoding="utf-8")
