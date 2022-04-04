import inspect
import sys


def list_children_in_module(module, parent):
    module = sys.modules[module.__name__]
    return [name for name, obj in inspect.getmembers(module) if is_child(obj, parent)]


def is_child(child, parent):
    return inspect.isclass(child) and (child is not parent and issubclass(child, parent))
