import graphviz
import pydot
# from graphviz2drawio import graphviz2drawio
from py_trees.composites import Selector

from bt.actions import Action
from bt.conditions import Condition
from bt.sequence import Sequence
from utils.file import create_file_and_write


def render_tree(root):
    tree_dot = tree_to_dot(root)
    src = graphviz.Source(tree_dot)
    src.render('tree.gv', format='png', view=True)


def tree_to_drawio_xml(root):
    # tree_dot = tree_to_dot(root)
    # rough_drawio = graphviz2drawio.convert(tree_dot)
    # return prettify_xml(rough_drawio)
    pass


def tree_to_dot(root):
    graph = pydot.Dot(graph_type='digraph', ordering="out", )
    graph.set_name(root.name)
    subtree_to_dot(root, graph)
    return graph.to_string()


def subtree_to_dot(tree, graph):
    label = tree.name
    shape = "box"
    fontsize = 11
    if isinstance(tree, Sequence):
        label = "→"
        fontsize = 32
    elif isinstance(tree, Selector):
        label = "?"
        fontsize = 32
    elif isinstance(tree, Condition):
        label = tree.name
        shape = "oval"
    elif isinstance(tree, Action):
        label = tree.name

    subtree_root_node = pydot.Node(str(tree.id), label=label, shape=shape, labelfontsize=fontsize, fontsize=fontsize)
    graph.add_node(subtree_root_node)
    for child in tree.children:
        child_node = subtree_to_dot(child, graph)
        child_edge = pydot.Edge(subtree_root_node.get_name(), child_node.get_name())
        graph.add_edge(child_edge)
    return subtree_root_node


# Separate implementation from the XML one
def tree_to_drawio_csv(tree):
    graph_attributes = {
        "label": "%step%",
        "style": "shape=%shape%;fontSize=%fontsize%;spacingBottom=%spacingbottom%;",
        "namespace": "csvimport-",
        "connect": '{"from":"refs", "to":"id", "invert":true, "style":"curved=0;endArrow=blockThin;endFill=1;"}',
        "padding": "15",
        "ignore": "id,shape,fill,stroke,refs"
    }
    csv = [f"# {key}: {value}" for key, value in graph_attributes.items()]
    csv.append("id,step,shape,fontsize,spacingbottom,refs")
    csv += subtree_to_csv(tree, None)

    return "\n".join(csv)


def subtree_to_csv(tree, parent_id):
    label = tree.name
    shape = "rectangle"
    fontsize = 11
    spacing_bottom = 0
    if isinstance(tree, Sequence):
        label = "→"
        fontsize = 32
        spacing_bottom = 20
    elif isinstance(tree, Selector):
        label = "?"
        fontsize = 32
        spacing_bottom = 10
    elif isinstance(tree, Condition):
        shape = "ellipse"
    ref = parent_id if parent_id is not None else ""

    base_csv = [f"{str(tree.id)},{label},{shape},{fontsize},{spacing_bottom},{ref}"]

    children_csv = []
    for child in tree.children:
        child_csv = subtree_to_csv(child, str(tree.id))
        children_csv += child_csv
    return base_csv + children_csv


def save_tree_to_log(tree, filename):
    logfile = f"log/{filename}"
    create_file_and_write(logfile, lambda file: file.write(tree_to_drawio_csv(tree)))
