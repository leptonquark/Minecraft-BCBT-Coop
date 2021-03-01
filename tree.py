from sequence import Sequence
from behaviours import Craft, Equip, GatherMaterial, JumpIfStuck 


class BehaviourTree():

    def __init__(self, agent_host):
        self.root = self.getBasicTree(agent_host)


    def getBasicTree(self, agent_host):
        tree = Sequence(
            "Create Stone Pickaxe", 
            children=[JumpIfStuck(agent_host), Craft(agent_host), Equip(agent_host), GatherMaterial(agent_host)]
        )
        tree.setup_with_descendants()
        return tree
