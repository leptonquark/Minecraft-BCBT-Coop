from py_trees.common import Status

from bt.actions import Action, JumpIfStuck
from bt.conditions import Condition
from bt.ppa import back_chain_recursive
from bt.sequence import Sequence
from goals.agentlesscondition import AgentlessCondition
from goals.blueprint.blueprint import Blueprint
from multiagents.cooperativity import Cooperativity
from utils.pickle import tree_to_state, state_to_tree
from utils.string import tree_to_string


class BackChainTree:
    def __init__(self, agent, goals, cooperativity=Cooperativity.INDEPENDENT):
        self.agent = agent
        self.root = self.initialize_tree(goals, cooperativity)

    def __getstate__(self):
        state = {'agent': self.agent, 'root': tree_to_state(self.root)}
        return state

    def __setstate__(self, state):
        self.agent = state['agent']
        self.root = state_to_tree(state['root'])

    def initialize_tree(self, goals, cooperativity):
        children = [JumpIfStuck(self.agent)]
        if cooperativity == Cooperativity.COOPERATIVE_WITH_CATCHUP or cooperativity == Cooperativity.COOPERATIVE:
            children += self.backward_chain(goals, True)
        if cooperativity == Cooperativity.COOPERATIVE_WITH_CATCHUP or cooperativity == Cooperativity.INDEPENDENT:
            children += self.backward_chain(goals, False)
        base_tree = Sequence("BaseTree", children=children)
        base_tree.setup_with_descendants()
        return base_tree

    def backward_chain(self, goals, collaborative):
        children = []
        for goal in goals:
            if isinstance(goal, Action):
                children.append(goal)
            elif isinstance(goal, Blueprint):
                conditions = goal.as_conditions(self.agent)
                children += [back_chain_recursive(self.agent, condition, collaborative) for condition in conditions]
            else:
                if isinstance(goal, AgentlessCondition):
                    goal = goal.as_condition(self.agent)
                if isinstance(goal, Condition):
                    children.append(back_chain_recursive(self.agent, goal, collaborative))
        return children

    def tick(self):
        self.root.tick_once()

    def print_tip(self):
        tip = self.root.tip()
        print(tip.name if tip is not None else "")

    def print_tree(self):
        print(tree_to_string(self.root))

    def all_goals_achieved(self):
        return self.root.status == Status.SUCCESS
