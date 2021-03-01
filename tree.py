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

        if self.agent_host.inventory.hasItem("log"):
            self.agent_host.sendCommand("craft planks")
        if not self.agent_host.inventory.hasItem("crafting_table", 1):
            if self.agent_host.inventory.hasItem("planks", 4):
                self.agent_host.sendCommand("craft crafting_table")
        else:
            if not self.agent_host.inventory.hasItem("stick", 2) and self.agent_host.inventory.hasItem("planks", 2):
                self.agent_host.sendCommand("craft stick")
            if not self.agent_host.inventory.hasItem("wooden_pickaxe") and self.agent_host.inventory.hasItem("stick", 2) and self.agent_host.inventory.hasItem("planks", 3):
                self.agent_host.sendCommand("craft wooden_pickaxe")
            if not self.agent_host.inventory.hasItem("stone_pickaxe") and self.agent_host.inventory.hasItem("stick", 2) and self.agent_host.inventory.hasItem("cobblestone", 3):
                self.agent_host.sendCommand("craft stone_pickaxe")


        if self.agent_host.inventory.hasItem("log"):
            self.agent_host.sendCommand("craft planks")
        if not self.agent_host.inventory.hasItem("crafting_table", 1):
            if self.agent_host.inventory.hasItem("planks", 4):
                self.agent_host.sendCommand("craft crafting_table")
        else:
            if not self.agent_host.inventory.hasItem("stick", 2) and self.agent_host.inventory.hasItem("planks", 2):
                self.agent_host.sendCommand("craft stick")
            if not self.agent_host.inventory.hasItem("wooden_pickaxe") and self.agent_host.inventory.hasItem("stick", 2) and self.agent_host.inventory.hasItem("planks", 3):
                self.agent_host.sendCommand("craft wooden_pickaxe")
            if not self.agent_host.inventory.hasItem("stone_pickaxe") and self.agent_host.inventory.hasItem("stick", 2) and self.agent_host.inventory.hasItem("cobblestone", 3):
                self.agent_host.sendCommand("craft stone_pickaxe")
