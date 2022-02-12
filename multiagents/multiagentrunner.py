from multiagents.multiagentprocess import MultiAgentProcess
from world.missiondata import MissionData


class MultiAgentRunner:

    def __init__(self, agent_names, goals=None):
        if goals is None:
            goals = []
        self.goals = goals
        self.agent_names = agent_names

    def run_mission_async(self):
        mission_data = MissionData(self.goals, self.agent_names)
        processes = [MultiAgentProcess(mission_data, i, self.goals) for i in range(len(self.agent_names))]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
