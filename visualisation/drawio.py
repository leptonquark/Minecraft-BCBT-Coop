import graphviz
import pydot
from graphviz2drawio import graphviz2drawio
from py_trees.composites import Selector

from bt.actions import Action
from bt.conditions import Condition
from bt.sequence import Sequence
from utils.string import prettify_xml


def tree_to_drawio_xml(root):
    tree_dot = tree_to_dot(root)
    print(tree_dot)
    src = graphviz.Source(tree_dot)
    src.render()
    rough_drawio = graphviz2drawio.convert(tree_dot)
    return prettify_xml(rough_drawio)


def tree_to_dot(root):
    graph = pydot.Dot(graph_type='digraph', ordering="out",)
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


def dot_to_draw_io(dot):
    src = graphviz.Source(dot)
    src.render()

