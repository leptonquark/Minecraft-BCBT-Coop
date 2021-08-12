from bt.actions import Action, JumpIfStuck
from bt.conditions import Condition
from bt.ppa import PPA, condition_to_ppa_tree, back_chain_recursive
from bt.sequence import Sequence
from goals.blueprint import Blueprint


class BackChainTree:
    def __init__(self, agent, goals):
        self.agent = agent
        self.root = self.get_base_back_chain_tree(goals)

    def get_base_back_chain_tree(self, goals):
        children = [JumpIfStuck(self.agent)]
        if isinstance(goals, Blueprint):
            goals = goals.as_conditions(self.agent)

        for goal in goals:
            if isinstance(goal, Action):
                children.append(goal)
            elif isinstance(goal, Condition):
                goal_ppa_tree = back_chain_recursive(self.agent, goal)
                if goal_ppa_tree is not None:
                    goal_ppa_tree.setup_with_descendants()
                    children.append(goal_ppa_tree)
        return Sequence("BaseTree", children=children)
