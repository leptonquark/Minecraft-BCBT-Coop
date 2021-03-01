from py_trees.composites import Selector
from sequence import Sequence
from behaviours import Craft, Equip, JumpIfStuck, GoToMaterial, MineMaterial 


class BehaviourTree():

    def __init__(self, agent_host):
        self.root = self.getBasicTree(agent_host)


    def getBasicTree(self, agent_host):
        gatherMaterialTree = self.getGatherMaterialTree(agent_host)
        tree = Sequence(
            "Create Stone Pickaxe", 
            children=[JumpIfStuck(agent_host), Craft(agent_host), Equip(agent_host), gatherMaterialTree]
        )
        tree.setup_with_descendants()
        return tree

    def getGatherMaterialTree(self, agent_host):
        tree = Sequence(
            "Gather Wood", 
            children=[GoToMaterial(agent_host), MineMaterial(agent_host)]
        )
        tree.setup_with_descendants()
        return tree
        