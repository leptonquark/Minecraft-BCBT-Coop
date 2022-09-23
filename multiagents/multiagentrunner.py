import multiprocessing as mp

from multiagents.multiagentprocess import MultiAgentProcess
from world.missiondata import MissionData


class MultiAgentRunner:

    def __init__(self, agent_names, goals=None):
        if goals is None:
            goals = []
        self.goals = goals
        self.agent_names = agent_names

    def run_mission_async(self):
        manager = mp.Manager()
        blackboard = manager.dict()

        mission_data = MissionData(self.goals, self.agent_names)
        processes = [MultiAgentProcess(mission_data, self.goals, blackboard, i) for i in range(len(self.agent_names))]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
