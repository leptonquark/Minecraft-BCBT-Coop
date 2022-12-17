import multiprocessing as mp

from kivy.clock import Clock
from kivy.core.text import Label
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from goals.blueprint.blueprint import Blueprint
from multiagents.cooperativity import Cooperativity
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from ui.colors import get_color
from utils.names import get_names
from world.missiondata import MissionData


class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process = None
        self.listen_event = None
        self.running_event = None
        self.old_size = None

    def on_enter(self):
        self.old_size = Window.size
        Window.size = (900, 600)
        self.start_bot()

    def restart_bot(self):
        self.stop_bot()
        self.start_bot()

    def stop_bot(self):
        if self.process:
            self.running_event.clear()
        if self.listen_event:
            self.listen_event.cancel()

    def start_bot(self):
        start_screen = self.manager.get_screen("ConfigurationScreen")
        amount = int(start_screen.ids['amount'].text)
        agent_names = get_names(amount)
        cooperativity = Cooperativity.COOPERATIVE if start_screen.ids[
            'collaborative'].active else Cooperativity.INDEPENDENT
        reset = start_screen.ids['reset'].active

        configuration = start_screen.ids['experiment'].experiment
        mission_data = MissionData(configuration, cooperativity, reset, agent_names)

        print(f"Starting Minecraft with {cooperativity} {amount} clients with configuration {configuration.name}...")

        self.ids.map.set_mission_data(mission_data)

        self.running_event = mp.Event()
        self.running_event.set()

        self.process = MultiAgentRunnerProcess(self.running_event, mission_data)
        self.process.start()
        self.listen_event = Clock.schedule_interval(lambda _: self.listen_to_pipe(self.process.pipe), 1 / 60)

    def listen_to_pipe(self, pipe):
        if pipe[0].poll():
            value = pipe[0].recv()
            self.set_map_data(value.agent_positions, value.blueprint_results)
            self.set_blackboard_data(value.blackboard)

    def set_map_data(self, agent_positions, blueprint_result):
        self.ids.map.set_data(agent_positions, blueprint_result)

    def set_blackboard_data(self, blackboard):
        self.ids.blackboard.text = ", \n".join(f"{key}: {value}" for key, value in blackboard.items())

    def on_request_close(self, *args):
        self.stop_bot()
        Window.size = self.old_size
        self.manager.current = "ConfigurationScreen"
        return True


NAME_MARGIN_BOTTOM = 20
NAME_FONT_SIZE = 16
TRACKING_ICON_SIZE = 10
X_RANGE_DEFAULT = (100, 150)
Z_RANGE_DEFAULT = (-25, 25)


class Map(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.agent_names = []
        self.blueprint_positions = []
        self.blueprint_results = []
        self.agent_positions = []
        self.x_range = X_RANGE_DEFAULT
        self.z_range = Z_RANGE_DEFAULT

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

        self.update_canvas()

    def set_mission_data(self, mission_data):
        self.agent_names = mission_data.agent_names
        self.blueprint_positions = []
        for goal in mission_data.goals:
            if isinstance(goal, Blueprint):
                self.blueprint_positions.append(goal.positions)
        if mission_data.flat_world:
            self.x_range = (75, 175)
            self.z_range = (-50, 50)

    def set_data(self, agent_positions, blueprint_results):
        self.agent_positions = agent_positions
        if blueprint_results:
            self.blueprint_results = blueprint_results
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        self.add_agent_positions()
        self.add_blueprint_positions()

    def add_agent_positions(self):
        for role, agent_position in enumerate(self.agent_positions):
            if agent_position is not None:
                self.add_agent_position(role, agent_position)

    def add_agent_position(self, role, agent_position):
        with self.canvas:
            Color(*get_color(role))
            frame_x, frame_z = self.get_frame_position(agent_position[0], agent_position[2])
            Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)
            self.add_name([frame_x, frame_z], self.agent_names[role])

    def add_blueprint_positions(self):
        with self.canvas:
            for i, blueprint in enumerate(self.blueprint_positions):
                for j, blueprint_position in enumerate(blueprint):
                    if self.blueprint_results and self.blueprint_results[i] and self.blueprint_results[i][j]:
                        Color(0, 1, 0, 1)
                    else:
                        Color(0, 0, 1, 1)
                    frame_x, frame_z = self.get_frame_position(blueprint_position[0], blueprint_position[2])
                    Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)
                    self.add_name([frame_x, frame_z], str(blueprint_position), 8)

    def add_name(self, position, name, font_size=NAME_FONT_SIZE):
        with self.canvas:
            label = Label(text=name, font_size=font_size)
            label.refresh()
            text = label.texture
            pos_x = position[0] - 0.4 * text.size[0]
            pos_z = position[1] + NAME_MARGIN_BOTTOM
            pos = [pos_x, pos_z]
            Color(1, 1, 1, 1)
            Rectangle(size=text.size, pos=pos, texture=text)

    def get_frame_position(self, pos_x, pos_z):
        width = self.size[0]
        height = self.size[1]

        scaled_x = (pos_x - self.x_range[0]) / (self.x_range[1] - self.x_range[0])
        scaled_z = (pos_z - self.z_range[0]) / (self.z_range[1] - self.z_range[0])
        frame_x = self.center_x - width / 2 + scaled_x * width
        frame_z = self.center_y - height / 2 + scaled_z * height
        return frame_x, frame_z
