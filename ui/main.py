import os
import threading
import tkinter as tk

from items import items
from bt import conditions
from goals.blueprint import BlueprintType, Blueprint
from goals.goal import GoalType
from malmo import malmoutils
from malmoutils.agent import MinerAgent
from malmoutils.minecraft import run_minecraft
from runner import Runner
from ui import storage

TKINTER_WINDOW_TITLE = "Malmo Behaviour Trees"
TKINTER_WINDOW_SIZE = "400x100"

CONDITIONS = ["HasItem", "HasItemEquipped"]
ITEMS = [items.BEEF, items.WOODEN_PICKAXE, items.STONE_PICKAXE, items.IRON_PICKAXE, items.DIAMOND_PICKAXE]

START_MINECRAFT_BUTTON_TEXT = "Start Minecraft"
START_BOT_BUTTON_TEXT = "Start Bot"


class MainUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.close_ui())
        self.pack()

        data = storage.load_data()
        self.goal_variable = tk.StringVar(self, data.get(storage.GOAL_TYPE_DATA_NAME, GoalType(0).name))
        self.condition_variable = tk.StringVar(self, data.get(storage.CONDITION_TYPE_DATA_NAME, CONDITIONS[0]))
        self.item_variable = tk.StringVar(self, data.get(storage.ITEM_TYPE_DATA_NAME, ITEMS[0]))
        self.blueprint_variable = tk.StringVar(self, data.get(storage.BLUEPRINT_TYPE_DATA_NAME, BlueprintType(0).name))

        self.goal_sub_drop_downs = {goal_type: [] for goal_type in GoalType}

        self.setup_drop_downs()
        self.setup_buttons()

    def setup_drop_downs(self):
        drop_down_area = tk.Frame(self)
        drop_down_area.pack(side=tk.TOP)

        goal_drop_down = tk.OptionMenu(drop_down_area, self.goal_variable, *[goal_type.name for goal_type in GoalType])
        goal_drop_down.grid(row=0, column=0)
        self.goal_variable.trace("w", lambda name, index, mode: self.update_sub_drop_downs(self.goal_variable))

        condition_drop_down = tk.OptionMenu(drop_down_area, self.condition_variable, *CONDITIONS)
        condition_drop_down.grid(row=0, column=1)
        self.goal_sub_drop_downs[GoalType.Condition].append(condition_drop_down)

        item_drop_down = tk.OptionMenu(drop_down_area, self.item_variable, *ITEMS)
        item_drop_down.grid(row=0, column=2)
        self.goal_sub_drop_downs[GoalType.Condition].append(item_drop_down)

        blueprint_drop_down = tk.OptionMenu(
            drop_down_area,
            self.blueprint_variable,
            *[blueprint_type.name for blueprint_type in BlueprintType]
        )
        blueprint_drop_down.grid(row=0, column=1)
        self.goal_sub_drop_downs[GoalType.Blueprint].append(blueprint_drop_down)

        self.update_sub_drop_downs(self.goal_variable)

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

        start_minecraft_button = tk.Button(button_area, text=START_MINECRAFT_BUTTON_TEXT, command=run_minecraft_async)
        start_minecraft_button.pack(side=tk.LEFT)

        start_bot_button = tk.Button(button_area, text=START_BOT_BUTTON_TEXT, command=lambda: self.start_bot())
        start_bot_button.pack(side=tk.RIGHT)

    def start_bot(self):
        if "MALMO_XSD_PATH" not in os.environ:
            print("Please set the MALMO_XSD_PATH environment variable.")
            return
        self.close_ui()

        malmoutils.fix_print()

        agent = MinerAgent()
        goals = self.get_goals(agent)

        player = Runner(agent, goals)
        player.run_mission()

    def get_goals(self, agent):
        if self.goal_variable.get() == GoalType.Blueprint.name:
            return Blueprint.get_blueprint(BlueprintType[self.blueprint_variable.get()])
        else:
            if self.condition_variable.get() == "HasItem":
                return [conditions.HasItem(agent, self.item_variable.get())]
            else:
                return [conditions.HasItemEquipped(agent, self.item_variable.get())]

    def close_ui(self):
        self.save_configuration()
        self.master.destroy()

    def save_configuration(self):
        data = {
            storage.GOAL_TYPE_DATA_NAME: self.goal_variable.get(),
            storage.CONDITION_TYPE_DATA_NAME : self.condition_variable.get(),
            storage.ITEM_TYPE_DATA_NAME: self.item_variable.get(),
            storage.BLUEPRINT_TYPE_DATA_NAME: self.blueprint_variable.get()
        }
        storage.save_data(data)

def run_minecraft_async():
    threading.Thread(target=run_minecraft, daemon=True).start()


def init_main_ui():
    root = tk.Tk()
    root.geometry(TKINTER_WINDOW_SIZE)
    root.title(TKINTER_WINDOW_TITLE)
    main_ui = MainUI(master=root)
    main_ui.mainloop()


if __name__ == "__main__":
    init_main_ui()
