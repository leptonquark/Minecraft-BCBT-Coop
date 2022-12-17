from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

import experiment.experiments as experiments
from utils.file import get_project_root

AMOUNT_OF_AGENTS = "amountOfAgents"
EXPERIMENT_ID = "experiment"
COLLABORATIVE = "collaborative"
RESET = "reset"

AMOUNT_OF_AGENTS_DEFAULT = 2
EXPERIMENT_ID_DEFAULT = 0
COLLABORATIVE_DEFAULT = True
RESET_DEFAULT = True

CONFIG_FILE = "data/config.json"

class ConfigurationScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        file_path = get_project_root() / CONFIG_FILE
        folder_path = file_path.parent
        folder_path.mkdir(parents=True, exist_ok=True)
        self.store = JsonStore(str(file_path))

    def on_enter(self, *args):
        self.initialize_amount_of_agents()
        self.initialize_experiment()
        self.initialize_checkbox(self.ids.collaborative, COLLABORATIVE, COLLABORATIVE_DEFAULT)
        self.initialize_checkbox(self.ids.reset, RESET, RESET_DEFAULT)

    def initialize_amount_of_agents(self):
        amount_of_agents = self.get_stored_value(AMOUNT_OF_AGENTS, AMOUNT_OF_AGENTS_DEFAULT)
        self.ids.amount.text = str(amount_of_agents)
        self.ids.amount.bind(text=self.on_amount_of_agents)

    def get_stored_value(self, key, default):
        if key in self.store and key in self.store[key]:
            return self.store[key][key]
        else:
            self.store[key] = {key: default}
            return default

    def on_amount_of_agents(self, _, amount):
        if amount.isnumeric():
            self.store_value(AMOUNT_OF_AGENTS, int(amount))

    def initialize_experiment(self):
        experiment_id = self.get_stored_value(EXPERIMENT_ID, EXPERIMENT_ID_DEFAULT)
        self.ids.experiment.experiment = experiments.configurations[experiment_id]
        self.ids.experiment.bind(configuration=self.on_experiment)

    def on_experiment(self, _, experiment):
        self.store_value(EXPERIMENT_ID, experiments.configurations.index(experiment))

    def initialize_checkbox(self, widget, key, default):
        active = self.get_stored_value(key, default)
        widget.active = active
        widget.bind(active=lambda _, selected: self.store_value(key, selected))

    def store_value(self, key, value):
        self.store[key] = {key: value}

    def start_bot(self):
        self.manager.current = "DashboardScreen"


class ConfigurationScreenRowButton(Button):
    configuration = ObjectProperty(experiments.configurations[0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(configuration=self.on_configuration)
        self.text = self.configuration.name
        self.dropdown = ConfigurationScreenDropDown()
        for configuration in experiments.configurations:
            dropdown_row_button = ConfigurationScreenDropDownRowButton(text=configuration.name,
                                                                       configuration=configuration)
            dropdown_row_button.bind(on_release=lambda button: self.dropdown.select(button.experiment))
            self.dropdown.add_widget(dropdown_row_button)
        self.dropdown.bind(on_select=self.on_select)

    def on_release(self):
        self.dropdown.open(self)

    def on_select(self, _, configuration):
        self.configuration = configuration

    def on_configuration(self, _, configuration):
        self.text = configuration.name


class NumberInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if len(substring) + len(self.text) > 1:
            return

        if not substring.isdigit():
            return
        return super().insert_text(substring, from_undo=from_undo)


class ConfigurationScreenDropDown(DropDown):
    pass


class ConfigurationScreenDropDownRowButton(Button):
    configuration = ObjectProperty(None)
