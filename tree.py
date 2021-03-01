import time
from py_trees.composites import Selector, Parallel
from py_trees.display import ascii_tree
from sequence import Sequence
from behaviours import Craft, Equip, JumpIfStuck, GoToMaterial, MineMaterial 


class BehaviourTree():

    def __init__(self, agent_host, goals = []):
        self.root = self.getBaseTree(agent_host, goals)


    def getBaseTree(self, agent_host, goals):
        baseGoalTree = self.getBaseGoalTree(agent_host, goals)
        tree = Parallel(
            "BaseTree", 
            children=[JumpIfStuck(agent_host), baseGoalTree]
        )
        tree.setup_with_descendants()
        return tree


    def getBaseGoalTree(self, agent_host, goals):
        goals = ["stone_pickaxe"] #REMOVE 
        children = [self.getGoalTree(agent_host, goal) for goal in goals]
        tree = Sequence(
            "BaseGoalTree",
            children=children
        )
        tree.setup_with_descendants()
        return tree


    def getGoalTree(self, agent_host, goal):
        tree = Selector(
            "Obtain " + goal,
            children=[
                self.getGatherTree(agent_host, ["iron_ore"], "stone_pickaxe"),
                Craft(agent_host, "stone_pickaxe"),
                self.getGatherTree(agent_host, ["stone"], "wooden_pickaxe"),
                self.getWoodenCraftTree(agent_host),
                self.getGatherTree(agent_host, ["log", "log2"])               
            ]
        )
        tree.setup_with_descendants()
        return tree
    
    def getWoodenCraftTree(self, agent_host):
        tree = Parallel(
            "Craft wood",
            children=[ 
                Craft(agent_host, "planks", 7),
                Craft(agent_host, "stick", 4),
                Craft(agent_host, "crafting_table", 1),
                Craft(agent_host, "wooden_pickaxe")
            ]
        )
        tree.setup_with_descendants()
        return tree


        

    def getGatherTree(self, agent_host, material, tool = None):
        children= []
        if tool is not None:
            children.append(Equip(agent_host, tool))
        children += [GoToMaterial(agent_host, material, tool), MineMaterial(agent_host, material, tool)]

        tree = Sequence(
            "Gather " + str(material), 
            children=children
        )
        tree.setup_with_descendants()
        return tree
        