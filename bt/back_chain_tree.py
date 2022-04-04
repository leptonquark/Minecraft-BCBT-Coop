from bt.actions import Action, JumpIfStuck
from bt.conditions import Condition
from bt.ppa import back_chain_recursive
from bt.sequence import Sequence
from goals.agentless_condition import AgentlessCondition
from goals.blueprint import Blueprint
from utils.pickle import tree_to_state, state_to_tree
from utils.string import tree_to_string


class BackChainTree:
    def __init__(self, agent, goals):
        self.agent = agent
        self.root = self.get_base_back_chain_tree(goals)

    def __getstate__(self):
        state = {'agent': self.agent, 'root': tree_to_state(self.root)}
        return state

    def __setstate__(self, state):
        self.agent = state['agent']
        self.root = state_to_tree(state['root'])

    def get_base_back_chain_tree(self, goals):
        children = [JumpIfStuck(self.agent)]
        if isinstance(goals, Blueprint):
            goals = goals.as_conditions(self.agent)
        for goal in goals:
            if isinstance(goal, Action):
                children.append(goal)
            else:
                if isinstance(goal, AgentlessCondition):
                    goal = goal.as_condition(self.agent)
                if isinstance(goal, Condition):
                    goal_ppa_tree = back_chain_recursive(self.agent, goal)
                    if goal_ppa_tree is not None:
                        goal_ppa_tree.setup_with_descendants()
                        children.append(goal_ppa_tree)
        return Sequence("BaseTree", children=children)

    def print_tip(self):
        tip = self.root.tip()
        print(tip.name if tip is not None else "")

    def print_tree(self):
        print(tree_to_string(self.root))
