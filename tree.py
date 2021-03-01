from py_trees.composites import Selector
from sequence import Sequence
from behaviours import Craft, Equip, JumpIfStuck, GoToMaterial, MineMaterial 


class BehaviourTree():

    def __init__(self, agent_host):
        self.root = self.getBasicTree(agent_host)


    def getBasicTree(self, agent_host):
        craftingTree = self.getCraftingTree(agent_host)
        equipTree = self.getEquipTree(agent_host)
        gatherMaterialTree = self.getGatherMaterialTree(agent_host)


        tree = Sequence(
            "Create Stone Pickaxe", 
            children=[JumpIfStuck(agent_host), craftingTree, equipTree, gatherMaterialTree]
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
        
    # This will be removed and will be integrated better. For testing only
    def getCraftingTree(self, agent_host):
        tree = Sequence(
            "Craft", 
            children=[
                Craft(agent_host, "planks"),
                Craft(agent_host, "crafting_table", True),
                Craft(agent_host, "wooden_pickaxe", True),
                Craft(agent_host, "stone_pickaxe", True),
                Craft(agent_host, "stick"),

            ]
        )
        tree.setup_with_descendants()
        return tree


   # This will be removed and will be integrated better. For testing only
    def getEquipTree(self, agent_host):
        tree = Sequence(
            "Equip", 
            children=[Equip(agent_host)]
        )        
        tree.setup_with_descendants()
        return tree