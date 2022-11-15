from goals.blueprint.blueprint import Blueprint, BlueprintType
from multiagents.multiagentprocess import PLAYER_POSITION, BLUEPRINT_RESULTS
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess, AGENT_DATA, BLACKBOARD
from ui.kivy.colors import get_color
from utils.names import get_names

TITLE = "Minecraft Coop AI Experiment"

if __name__ == '__main__':
    # The imports need to be done here for Kivy to support Multiprocessing without automatically opening new windows.
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.text import Label
    from kivy.core.window import Window
    from kivy.graphics import Color, Ellipse, Rectangle
    from kivy.lang import Builder
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
            Builder.load_file('start.kv')
            self.title = "Minecraft Coop AI Experiment"
            screen_manager = ScreenManager(transition=FadeTransition())
            screen_manager.add_widget(StartScreen())
            screen_manager.add_widget(DashboardScreen())
            return screen_manager


    class StartScreen(Screen):
        def start_bot(self):
            self.manager.current = "DashboardScreen"


    TRACKING_ICON_SIZE = 10
    X_RANGE = (100, 150)
    Z_RANGE = (-25, 25)


    class DashboardScreen(Screen):
        def on_enter(self):
            Window.size = (900, 600)
            self.start_bot()

        def start_bot(self):
            amount = int(self.manager.get_screen("StartScreen").ids['amount'].text)
            agent_names = get_names(amount)
            print(f"Starting Minecraft with {amount} clients...")

            goals = Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 9])
            self.ids.map.set_goals(goals)
            self.ids.map.set_agent_names(agent_names)
            runner_process = MultiAgentRunnerProcess(agent_names, goals)
            runner_process.start()
            Clock.schedule_interval(lambda _: self.listen_to_pipe(runner_process.pipe), 1 / 60)

        def listen_to_pipe(self, pipe):
            if pipe[0].poll():
                value = pipe[0].recv()
                self.on_agent_data(value[AGENT_DATA])
                self.on_blackboard(value[BLACKBOARD])

        def on_agent_data(self, agent_data):
            player_position = agent_data[1][PLAYER_POSITION]
            unit = agent_data[0]
            pos_x = player_position[0]
            pos_z = player_position[2]
            positions = (pos_x, pos_z)
            blueprint_results = agent_data[1].get(BLUEPRINT_RESULTS)
            self.ids.map.set_data(unit, positions, blueprint_results)

        def on_blackboard(self, blackboard):
            self.ids.blackboard.text = ", \n".join(f"{key}: {value}" for key, value in blackboard.items())


    NAME_MARGIN_BOTTOM = 20
    NAME_FONT_SIZE = 16


    class Map(Widget):
        def __init__(self, **kwargs):
            super(Map, self).__init__(**kwargs)

            self.agent_names = []
            self.blueprint_positions = []
            self.blueprint_results = []
            self.positions = {}

            self.bind(pos=self.update_canvas)
            self.bind(size=self.update_canvas)

            self.update_canvas()

        def set_agent_names(self, agent_names):
            self.agent_names = agent_names

        def set_goals(self, goals):
            if type(goals) is Blueprint:
                self.blueprint_positions = goals.positions

        def set_data(self, unit, positions, blueprint_results=None):
            self.positions[unit] = positions
            if blueprint_results:
                self.blueprint_results = blueprint_results
            self.update_canvas()

        def update_canvas(self, *args):
            self.canvas.clear()
            with self.canvas:
                for i, position in self.positions.items():
                    Color(*get_color(i))
                    if position is not None:
                        frame_x, frame_z = self.get_frame_position(position[0], position[1])
                        Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)
                        self.add_name([frame_x, frame_z], self.agent_names[i])
                for i, blueprint_position in enumerate(self.blueprint_positions):
                    if self.blueprint_results and self.blueprint_results[i]:
                        Color(0, 1, 0, 1)
                    else:
                        Color(0, 0, 1, 1)
                    frame_x, frame_z = self.get_frame_position(blueprint_position[0], blueprint_position[2])
                    Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)
                    self.add_name([frame_x, frame_z], str(blueprint_position), 8)

        def add_name(self, position, name, font_size=NAME_FONT_SIZE):
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

            scaled_x = (pos_x - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0])
            scaled_z = (pos_z - Z_RANGE[0]) / (Z_RANGE[1] - Z_RANGE[0])
            frame_x = self.center_x - width / 2 + scaled_x * width
            frame_z = self.center_y - height / 2 + scaled_z * height
            return frame_x, frame_z


    StartApp().run()
