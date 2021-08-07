import tkinter as tk
from goals.goal import GoalType
from goals.blueprint import BlueprintType

TKINTER_WINDOW_TITLE = "Malmo Behaviour Trees"
TKINTER_WINDOW_SIZE = "400x200"

CONDITIONS = ["HasItem", "HasItemEquipped"]
ITEMS = ["Beef", "Diamond Pickaxe"]


class MainUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.goal_sub_drop_downs = {goal_type: [] for goal_type in GoalType}
        self.setup_drop_downs()

    def setup_drop_downs(self):
        drop_down_area = tk.Frame(self)
        drop_down_area.pack(fill=tk.BOTH, side=tk.TOP)

        goal_variable = tk.StringVar(drop_down_area, GoalType(0).name)
        goal_drop_down = tk.OptionMenu(drop_down_area, goal_variable, *[goal_type.name for goal_type in GoalType])
        goal_drop_down.grid(row=0, column=0)
        goal_variable.trace(
            "w",
            lambda name, index, mode : self.update_sub_drop_downs(goal_variable)
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




def init_main_ui():
    root = tk.Tk()
    root.geometry(TKINTER_WINDOW_SIZE)
    root.title(TKINTER_WINDOW_TITLE)
    main_ui = MainUI(master=root)
    main_ui.mainloop()


if __name__ == "__main__":
    init_main_ui()
