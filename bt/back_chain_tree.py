from bt.ppa import CraftPPA, GatherPPA, EquipPPA, condition_to_ppa_tree
from items import items


class BackChainTree:
    def __init__(self, agent):
        self.agent = agent
        self.root = self.get_base_tree_back_chain()

    def get_base_tree_back_chain(self):
        stone_pickaxe_ppa = EquipPPA(self.agent, items.DIAMOND_PICKAXE)
        return self.back_chain_recursive(stone_pickaxe_ppa)

    def back_chain_recursive(self, ppa):
        for i, pre_condition in enumerate(ppa.pre_conditions):
            ppa_condition = condition_to_ppa_tree(self.agent, pre_condition)
            if ppa_condition is not None:
                self.back_chain_recursive(ppa_condition)
                ppa.pre_conditions[i] = ppa_condition.tree
        ppa.create_ppa()
        return ppa.tree
