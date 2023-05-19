import multiprocessing as mp

from kivy.clock import Clock
from kivy.core.text import Label
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from goals.blueprint.blueprint import Blueprint
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from ui.colors import get_agent_color, get_cuboid_color, get_blueprint_color
from world.missiondata import MissionData
from world.worldgenerator import FlatWorldGenerator, CustomWorldGenerator


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
        cooperativity = start_screen.ids['cooperativity'].cooperativity
        reset = start_screen.ids['reset'].active

        configuration = start_screen.ids['experiment'].experiment
        mission_data = MissionData(configuration, cooperativity, reset, amount)

        print(f"Starting Minecraft with {cooperativity} {amount} clients with configuration {configuration.name}...")

        self.ids.map.set_mission_data(mission_data)

        self.running_event = mp.Event()
        self.running_event.set()
        self.process = MultiAgentRunnerProcess(mission_data, self.running_event)
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


def get_cuboid_dict(cuboid):
    return {
        "x0": min(cuboid.range[0][0], cuboid.range[1][0]),
        "x1": max(cuboid.range[0][0], cuboid.range[1][0]),
        "z0": min(cuboid.range[0][2], cuboid.range[1][2]),
        "z1": max(cuboid.range[0][2], cuboid.range[1][2]),
        "color": get_cuboid_color(cuboid.type)
    }


class Map(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.agent_names = []
        self.agent_positions = []

        self.blueprint_positions = []
        self.blueprint_results = []

        self.cuboids = []

        self.x_range = X_RANGE_DEFAULT
        self.z_range = Z_RANGE_DEFAULT

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)

        self.update_canvas()

    def set_mission_data(self, mission_data):
        self.agent_names = mission_data.agent_names
        self.blueprint_positions = [goal.positions for goal in mission_data.goals if isinstance(goal, Blueprint)]
        self.blueprint_results = [[False for _ in positions] for positions in self.blueprint_positions]
        if isinstance(mission_data.world_generator, CustomWorldGenerator):
            self.cuboids = [get_cuboid_dict(cuboid) for cuboid in mission_data.world_generator.cuboids]
            self.x_range = (-30, 30)
            self.z_range = (-30, 30)
        elif isinstance(mission_data.world_generator, FlatWorldGenerator):
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
        self.add_cuboids()

    def add_agent_positions(self):
        for role, agent_position in enumerate(self.agent_positions):
            if agent_position is not None:
                self.add_agent_position(role, agent_position)

    def add_agent_position(self, role, agent_position):
        with self.canvas:
            Color(*get_agent_color(role))
            frame_x, frame_z = self.get_frame_position(agent_position[0], agent_position[2])
            Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)
            self.add_name([frame_x, frame_z], self.agent_names[role])

    def add_blueprint_positions(self):
        for i, blueprint in enumerate(self.blueprint_positions):
            for j, blueprint_position in enumerate(blueprint):
                placed = self.blueprint_results and self.blueprint_results[i] and self.blueprint_results[i][j]
                color = get_blueprint_color(placed)
                self.add_named_dot(blueprint_position, color, str(blueprint_position), 8)

    def add_named_dot(self, position, color, name, name_size=NAME_FONT_SIZE):
        frame_x, frame_z = self.get_frame_position(position[0], position[2])
        self.add_dot(color, [frame_x, frame_z])
        self.add_name([frame_x, frame_z], name, name_size)
        return frame_x, frame_z

    def add_dot(self, color, frame_position):
        with self.canvas:
            Color(*color)
            Ellipse(pos=frame_position, size=[TRACKING_ICON_SIZE] * 2)

    def add_cuboids(self):
        with self.canvas:
            for cuboid in self.cuboids:
                Color(*cuboid["color"])
                frame_x0, frame_z0 = self.get_frame_position(cuboid["x0"], cuboid["z0"])
                frame_x1, frame_z1 = self.get_frame_position(cuboid["x1"], cuboid["z1"])
                Rectangle(pos=[frame_x0, frame_z0], size=[frame_x1 - frame_x0, frame_z1 - frame_z0])

    def add_name(self, frame_position, name, font_size=NAME_FONT_SIZE):
        with self.canvas:
            label = Label(text=name, font_size=font_size)
            label.refresh()
            text = label.texture
            name_position_x = frame_position[0] - 0.4 * text.size[0]
            name_position_z = frame_position[1] + NAME_MARGIN_BOTTOM
            name_position = [name_position_x, name_position_z]
            Color(1, 1, 1, 1)
            Rectangle(size=text.size, pos=name_position, texture=text)

    def get_frame_position(self, pos_x, pos_z):
        width = self.size[0]
        height = self.size[1]

        scaled_x = (pos_x - self.x_range[0]) / (self.x_range[1] - self.x_range[0])
        scaled_z = (pos_z - self.z_range[0]) / (self.z_range[1] - self.z_range[0])
        frame_x = self.center_x - width / 2 + scaled_x * width
        frame_z = self.center_y - height / 2 + scaled_z * height
        frame_z = height - frame_z
        return frame_x, frame_z
