from goals.blueprint.blueprint import Blueprint, BlueprintType
from multiagents.multiagentprocess import PLAYER_POSITION, BLUEPRINT_RESULT
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess, AGENT_DATA
from ui.kivy.colors import get_color
from utils.names import get_names

TITLE = "Minecraft Coop AI Experiment"

if __name__ == '__main__':
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.graphics import Color, Ellipse
    from kivy.lang import Builder
    from kivy.core.window import Window
    from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
    from kivy.uix.textinput import TextInput

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

        def __init__(self, **kw):
            super(DashboardScreen, self).__init__(**kw)
            self.positions = {}
            self.blueprint_positions = []
            self.blueprint_results = []
            self.n_agents = 0

        def on_enter(self):
            Window.size = (600, 600)
            self.bind(pos=self.update_canvas)
            self.bind(size=self.update_canvas)
            self.update_canvas()
            self.start_bot()

            print("oh")

        def start_bot(self):
            amount = int(self.manager.get_screen("StartScreen").ids['amount'].text)
            self.n_agents = amount
            agent_names = get_names(amount)
            print(f"Starting Minecraft with {amount} clients...")

            goals = Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 9])
            if type(goals) is Blueprint:
                self.blueprint_positions = goals.positions

            runner_process = MultiAgentRunnerProcess(agent_names, goals)
            runner_process.start()

            Clock.schedule_interval(lambda _: self.listen_to_pipe(runner_process.pipe), 1 / 60)

        def listen_to_pipe(self, pipe):
            if pipe[0].poll():
                value = pipe[0].recv()
                print(value)
                agent_data = value[AGENT_DATA]
                player_position = agent_data[1][PLAYER_POSITION]
                unit = agent_data[0]
                pos_x = player_position[0]
                pos_z = player_position[2]
                self.positions[unit] = (pos_x, pos_z)
                if BLUEPRINT_RESULT in agent_data[1]:
                    self.blueprint_results = agent_data[1][BLUEPRINT_RESULT]

                self.update_canvas()

        def update_canvas(self, *args):
            self.canvas.clear()
            with self.canvas:
                for i in range(self.n_agents):
                    Color(*get_color(i))
                    position = self.positions.get(i)
                    if position is not None:
                        frame_x, frame_z = self.get_frame_position(position[0], position[1])
                        Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)
                for i, blueprint_position in enumerate(self.blueprint_positions):
                    if self.blueprint_results and self.blueprint_results[i]:
                        Color(0, 1, 0, 1)
                    else:
                        Color(0, 0, 1, 1)
                    frame_x, frame_z = self.get_frame_position(blueprint_position[0], blueprint_position[2])
                    Ellipse(pos=[frame_x, frame_z], size=[TRACKING_ICON_SIZE] * 2)

        def get_frame_position(self, pos_x, pos_z):
            width = self.size[0]
            height = self.size[1]

            scaled_x = (pos_x - X_RANGE[0]) / (X_RANGE[1] - X_RANGE[0])
            scaled_z = (pos_z - Z_RANGE[0]) / (Z_RANGE[1] - Z_RANGE[0])
            frame_x = self.center_x - width / 2 + scaled_x * width
            frame_z = self.center_y - height / 2 + scaled_z * height
            return frame_x, frame_z


    StartApp().run()
