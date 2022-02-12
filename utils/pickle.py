from py_trees.composites import Selector

from bt.sequence import Sequence

BEHAVIOUR_BASE_ATTRIBUTES = ["id", "name", "blackboards", "qualified_name", "parent", "children", "logger",
                             "feedback_message", "blackbox_level", "status", "iterator"]

CLASS = "class"
NAME = "name"
CHILDREN = "children"
ATTRIBUTES = "attributes"


def tree_to_state(node):
    if type(node) is Selector or type(node) is Sequence:
        children = [tree_to_state(child) for child in node.children]
        return {CLASS: node.__class__, NAME: node.name, CHILDREN: children}
    else:
        attributes = {k: v for k, v in node.__dict__.items() if k not in BEHAVIOUR_BASE_ATTRIBUTES}
        return {CLASS: node.__class__, ATTRIBUTES: attributes}


def state_to_tree(state):
    behaviour_class = state[CLASS]

    if CHILDREN in state:
        children = [state_to_tree(child) for child in state[CHILDREN]]
        node = behaviour_class(state[NAME], children=children)
    else:
        node = behaviour_class(**state[ATTRIBUTES])
    return node
