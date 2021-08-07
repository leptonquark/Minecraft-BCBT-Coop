import os
import tkinter as tk
import threading

from goals.blueprint import BlueprintType, Blueprint
from goals.goal import GoalType
from malmoutils import malmoutils
from malmoutils.agent import MinerAgent
from malmoutils.minecraft import run_minecraft
from runner import Runner
from world.world import World

TKINTER_WINDOW_TITLE = "Malmo Behaviour Trees"
TKINTER_WINDOW_SIZE = "400x100"

CONDITIONS = ["HasItem", "HasItemEquipped"]
ITEMS = ["Beef", "Diamond Pickaxe"]

START_MINECRAFT_BUTTON_TEXT = "Start Minecraft"
START_BOT_BUTTON_TEXT = "Start Bot"


class MainUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.goal_sub_drop_downs = {goal_type: [] for goal_type in GoalType}
        self.setup_drop_downs()
        self.setup_buttons()

    def setup_drop_downs(self):
        drop_down_area = tk.Frame(self)
        drop_down_area.pack(side=tk.TOP)

        goal_variable = tk.StringVar(drop_down_area, GoalType(0).name)
        goal_drop_down = tk.OptionMenu(drop_down_area, goal_variable, *[goal_type.name for goal_type in GoalType])
        goal_drop_down.grid(row=0, column=0)
        goal_variable.trace(
            "w",
            lambda name, index, mode: self.update_sub_drop_downs(goal_variable)
        )

        condition_variable = tk.StringVar(drop_down_area, CONDITIONS[0])
        condition_drop_down = tk.OptionMenu(drop_down_area, condition_variable, *CONDITIONS)
        condition_drop_down.grid(row=0, column=1)
        self.goal_sub_drop_downs[GoalType.Condition].append(condition_drop_down)

        item_variable = tk.StringVar(drop_down_area, ITEMS[0])
        item_drop_down = tk.OptionMenu(drop_down_area, item_variable, *ITEMS)
        item_drop_down.grid(row=0, column=2)
        self.goal_sub_drop_downs[GoalType.Condition].append(item_drop_down)

        blueprint_variable = tk.StringVar(drop_down_area, BlueprintType(0).name)
        blueprint_drop_down = tk.OptionMenu(
            drop_down_area,
            blueprint_variable,
            *[goal_type.name for goal_type in BlueprintType]
        )
        blueprint_drop_down.grid(row=0, column=1)
        self.goal_sub_drop_downs[GoalType.Blueprint].append(blueprint_drop_down)

        self.update_sub_drop_downs(goal_variable)

    def update_sub_drop_downs(self, goal_variable):
        for goal_type in GoalType:
            if goal_type.name == goal_variable.get():
                for i, drop_down in enumerate(self.goal_sub_drop_downs[goal_type]):
                    drop_down.grid()
            else:
                for i, drop_down in enumerate(self.goal_sub_drop_downs[goal_type]):
                    drop_down.grid_remove()

    def setup_buttons(self):
        button_area = tk.Frame(self)
        button_area.pack(fill=tk.X, side=tk.BOTTOM)

        start_minecraft_button = tk.Button(
            button_area,
            text=START_MINECRAFT_BUTTON_TEXT,
            command= lambda : self.master.after(0, run_minecraft_async)
        )
        start_minecraft_button.pack(side=tk.LEFT)

        start_bot_button = tk.Button(button_area, text=START_BOT_BUTTON_TEXT, command=start_bot_async)
        start_bot_button.pack(side=tk.RIGHT)


def run_minecraft_async():

    threading.Thread(target=run_minecraft, daemon=True).start()


def start_bot_async():
    threading.Thread(target=start_bot).start()


def start_bot():
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent = MinerAgent()
    # goals = [conditions.HasItemEquipped(agent, items.DIAMOND_PICKAXE)]

    # goals = [conditions.HasItem(agent, items.BEEF)]

    goals = Blueprint.get_blueprint(BlueprintType.StraightFence)

    world = World(agent, goals)

    player = Runner(world, agent, goals)
    player.run_mission()


def init_main_ui():
    root = tk.Tk()
    root.geometry(TKINTER_WINDOW_SIZE)
    root.title(TKINTER_WINDOW_TITLE)
    main_ui = MainUI(master=root)
    main_ui.mainloop()


if __name__ == "__main__":
    init_main_ui()
