from py_trees.common import Status

from bt.actions import Action, JumpIfStuck
from bt.conditions import Condition
from bt.ppa import back_chain_recursive
from bt.sequence import Sequence
from goals.agentlesscondition import AgentlessCondition
from goals.blueprint.blueprint import Blueprint
from utils.pickle import tree_to_state, state_to_tree
from utils.string import tree_to_string


class BackChainTree:
    def __init__(self, agent, goals, collaborative):
        self.agent = agent
        self.root = self.back_chain(goals, collaborative)

    def __getstate__(self):
        state = {'agent': self.agent, 'root': tree_to_state(self.root)}
        return state

    def __setstate__(self, state):
        self.agent = state['agent']
        self.root = state_to_tree(state['root'])

    def back_chain(self, goals, collaborative):
        children = [JumpIfStuck(self.agent)]
        for goal in goals:
            if isinstance(goal, Action):
                children.append(goal)
            elif isinstance(goal, Blueprint):
                for condition in goal.as_conditions(self.agent):
                    condition_ppa_tree = back_chain_recursive(self.agent, condition, collaborative)
                    condition_ppa_tree.setup_with_descendants()
                    children.append(condition_ppa_tree)
            else:
                if isinstance(goal, AgentlessCondition):
                    goal = goal.as_condition(self.agent)
                if isinstance(goal, Condition):
                    goal_ppa_tree = back_chain_recursive(self.agent, goal, collaborative)
                    goal_ppa_tree.setup_with_descendants()
                    children.append(goal_ppa_tree)
        return Sequence("BaseTree", children=children)

    def tick(self):
        self.root.tick_once()

    def print_tip(self):
        tip = self.root.tip()
        print(tip.name if tip is not None else "")

    def print_tree(self):
        print(tree_to_string(self.root))

    def all_goals_achieved(self):
        return self.root.status == Status.SUCCESS
