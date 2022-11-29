import multiprocessing as mp

import experiment.configurations as config
from goals.blueprint.blueprint import Blueprint
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from ui.colors import get_color
from utils.names import get_names
from world.missiondata import MissionData

TITLE = "Minecraft Coop AI Experiment"

if __name__ == '__main__':
    # The imports need to be done here for Kivy to support Multiprocessing without automatically opening new windows.
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.text import Label
    from kivy.core.window import Window
    from kivy.graphics import Color, Ellipse, Rectangle
    from kivy.storage.jsonstore import JsonStore
    from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
    from kivy.uix.textinput import TextInput
    from kivy.uix.widget import Widget

    Window.borderless = False
    Window.size = (300, 300)


    class NumberInput(TextInput):
        def insert_text(self, substring, from_undo=False):
            if len(substring) + len(self.text) > 1:
                return

            if not substring.isdigit():
                return
            return super().insert_text(substring, from_undo=from_undo)


    class StartApp(App):

        def build(self):
            self.title = TITLE
            screen_manager = ScreenManager(transition=FadeTransition())
            screen_manager.add_widget(StartScreen())
            screen_manager.add_widget(DashboardScreen())
            return screen_manager


    AMOUNT_OF_AGENTS = "amountOfAgents"
    COLLABORATIVE = "collaborative"
    RESET = "reset"
    FLAT_WORLD = "flat_world"

    AMOUNT_OF_AGENTS_DEFAULT = 2
    COLLABORATIVE_DEFAULT = True
    RESET_DEFAULT = True
    FLAT_WORLD_DEFAULT = False


    class StartScreen(Screen):

        def __init__(self, **kwargs):
            super(StartScreen, self).__init__(**kwargs)
            self.store = JsonStore("config.json")

        def on_enter(self, *args):
            self.initialize_amount_of_agents()
            self.initialize_checkbox(self.ids.collaborative, COLLABORATIVE, COLLABORATIVE_DEFAULT)
            self.initialize_checkbox(self.ids.reset, RESET, RESET_DEFAULT)
            self.initialize_checkbox(self.ids.flat_world, FLAT_WORLD, FLAT_WORLD_DEFAULT)

        def initialize_amount_of_agents(self):
            if AMOUNT_OF_AGENTS in self.store and AMOUNT_OF_AGENTS in self.store[AMOUNT_OF_AGENTS]:
                amount_of_agents = self.store[AMOUNT_OF_AGENTS][AMOUNT_OF_AGENTS]
            else:
                amount_of_agents = AMOUNT_OF_AGENTS_DEFAULT
                self.store[AMOUNT_OF_AGENTS] = {AMOUNT_OF_AGENTS: AMOUNT_OF_AGENTS_DEFAULT}

            self.ids.amount.text = str(amount_of_agents)
            self.ids.amount.bind(text=self.on_amount_of_agents)

        def on_amount_of_agents(self, _, amount):
            if amount.isnumeric():
                self.store[AMOUNT_OF_AGENTS] = {AMOUNT_OF_AGENTS: int(amount)}

        def initialize_checkbox(self, widget, key, default):
            if key in self.store and key in self.store[key]:
                collaborative = self.store[key][key]
            else:
                collaborative = default
                self.store[key] = {key: default}

            widget.active = collaborative
            widget.bind(active=lambda _, selected: self.store_value(key, selected))

        def store_value(self, key, value):
            self.store[key] = {key: value}

        def start_bot(self):
            self.manager.current = "DashboardScreen"


    class DashboardScreen(Screen):

        def __init__(self, **kwargs):
            super(DashboardScreen, self).__init__(**kwargs)
            self.process = None
            self.listen_event = None
            self.running_event = None


        def on_enter(self):
            Window.size = (900, 600)
            self.start_bot()

        def start_bot(self):

            start_screen = self.manager.get_screen("StartScreen")
            amount = int(start_screen.ids['amount'].text)
            agent_names = get_names(amount)
            collaborative = start_screen.ids['collaborative'].active
            reset = start_screen.ids['reset'].active
            flat_world = start_screen.ids['flat_world'].active

            configuration = config.config_flat_world_generator if flat_world else config.config_default_world_generator
            mission_data = MissionData(configuration, collaborative, reset, agent_names)

            descriptor = "collaborative" if collaborative else "independent"
            generator = "FWG" if flat_world else "DWG"
            print(f"Starting Minecraft with {descriptor} {amount} clients using {generator}...")

            self.ids.map.set_mission_data(mission_data)

            self.running_event = mp.Event()
            self.running_event.set()

            self.process = MultiAgentRunnerProcess(self.running_event, mission_data)
            self.process.start()
            self.listen_event = Clock.schedule_interval(lambda _: self.listen_to_pipe(self.process.pipe), 1 / 60)

        def restart_bot(self):
            if self.process:
                self.running_event.clear()
            if self.listen_event:
                self.listen_event.cancel()
            self.start_bot()

        def listen_to_pipe(self, pipe):
            if pipe[0].poll():
                value = pipe[0].recv()
                self.set_map_data(value.agent_positions, value.blueprint_result)
                self.set_blackboard_data(value.blackboard)

        def set_map_data(self, agent_positions, blueprint_result):
            self.ids.map.set_data(agent_positions, blueprint_result)

        def set_blackboard_data(self, blackboard):
            self.ids.blackboard.text = ", \n".join(f"{key}: {value}" for key, value in blackboard.items())


    NAME_MARGIN_BOTTOM = 20
    NAME_FONT_SIZE = 16
    TRACKING_ICON_SIZE = 10
    X_RANGE_DEFAULT = (100, 150)
    Z_RANGE_DEFAULT = (-25, 25)


    class Map(Widget):
        def __init__(self, **kwargs):
            super(Map, self).__init__(**kwargs)

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
            if type(mission_data.goals) is Blueprint:
                self.blueprint_positions = mission_data.goals.positions
            if mission_data.flat_world:
                self.x_range = (75, 175)
                self.z_range = (-50, 50)

        def set_data(self, agent_positions, blueprint_result):
            self.agent_positions = agent_positions
            if blueprint_result:
                self.blueprint_results = blueprint_result
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
                for i, blueprint_position in enumerate(self.blueprint_positions):
                    if self.blueprint_results and self.blueprint_results[i]:
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


    StartApp().run()
