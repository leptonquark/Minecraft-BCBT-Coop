from goals.blueprint import Blueprint, BlueprintType
from malmoutils.minecraft import run_minecraft
from multiagents.multiagentrunner import MultiAgentRunner
from utils.names import get_names

TITLE = "Minecraft Coop AI Experiment"

if __name__ == '__main__':
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.core.window import Window
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
            self.title = "Minecraft Coop AI Experiment"

            return Builder.load_file('start.kv')

        def start_bot(self, amount):
            Window.hide()
            agent_names = get_names(amount)
            print(f"Starting Minecraft with {amount} clients...")
            run_minecraft(n_clients=len(agent_names))

            goals = Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 9])

            runner = MultiAgentRunner(agent_names, goals)
            runner.run_mission_async()


    StartApp().run()
