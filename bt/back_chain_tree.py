from bt.behaviours import JumpIfStuck
from bt.conditions import Condition
from bt.ppa import PPA, condition_to_ppa_tree
from bt.sequence import Sequence


class BackChainTree:
    def __init__(self, agent, goals):
        self.agent = agent
        self.root = self.get_base_back_chain_tree(goals)

    def get_base_back_chain_tree(self, goals):
        children = [JumpIfStuck(self.agent)]
        for goal in goals:
            goal_ppa = None
            if isinstance(goal, Condition):
                goal_ppa = condition_to_ppa_tree(self.agent, goal)
            elif isinstance(goal, PPA):
                goal_ppa = condition_to_ppa_tree(self.agent, goal)
            if goal_ppa is not None:
                self.back_chain_recursive(goal_ppa)
                children.append(goal_ppa.tree)
        return Sequence("BaseTree", children=children)

    def back_chain_recursive(self, ppa):
        for i, pre_condition in enumerate(ppa.pre_conditions):
            ppa_condition = condition_to_ppa_tree(self.agent, pre_condition)
            if ppa_condition is not None:
                self.back_chain_recursive(ppa_condition)
                ppa.pre_conditions[i] = ppa_condition.tree
        ppa.create_ppa()
        return ppa.tree
