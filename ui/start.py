from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

import experiment.experiments as experiments
from multiagents.cooperativity import Cooperativity
from utils.file import create_folders

AMOUNT_OF_AGENTS = "amountOfAgents"
EXPERIMENT_ID = "experiment"
COOPERATIVITY_ID = "cooperativity"
RESET = "reset"

AMOUNT_OF_AGENTS_DEFAULT = 2
EXPERIMENT_ID_DEFAULT = 0
COOPERATIVITY_DEFAULT = 0
RESET_DEFAULT = True

CONFIG_FILE = "data/config.json"


class ConfigurationScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        create_folders(CONFIG_FILE)
        self.store = JsonStore(CONFIG_FILE)

    def on_enter(self, *args):
        self.initialize_amount_of_agents()
        self.initialize_experiment()
        self.initialize_cooperativity()
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
        self.ids.experiment.bind(experiment=self.on_experiment)

    def on_experiment(self, _, experiment):
        self.store_value(EXPERIMENT_ID, experiments.configurations.index(experiment))

    def initialize_cooperativity(self):
        cooperativity_id = self.get_stored_value(COOPERATIVITY_ID, COOPERATIVITY_DEFAULT)
        self.ids.cooperativity.cooperativity = Cooperativity(cooperativity_id)
        self.ids.cooperativity.bind(cooperativity=self.on_cooperativity)

    def on_cooperativity(self, _, cooperativity):
        self.store_value(COOPERATIVITY_ID, cooperativity.value)

    def initialize_checkbox(self, widget, key, default):
        active = self.get_stored_value(key, default)
        widget.active = active
        widget.bind(active=lambda _, selected: self.store_value(key, selected))

    def store_value(self, key, value):
        self.store[key] = {key: value}

    def start_bot(self):
        self.manager.current = "DashboardScreen"


class ExperimentRowButton(Button):
    experiment = ObjectProperty(experiments.configurations[0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(experiment=self.on_experiment)
        self.text = self.experiment.name
        self.dropdown = ConfigurationScreenDropDown()
        for experiment in experiments.configurations:
            dropdown_row_button = ConfigurationScreenDropDownRowButton(text=experiment.name, value=experiment)
            dropdown_row_button.bind(on_release=lambda button: self.dropdown.select(button.value))
            self.dropdown.add_widget(dropdown_row_button)
        self.dropdown.bind(on_select=self.on_select)

    def on_release(self):
        self.dropdown.open(self)

    def on_select(self, _, experiment):
        self.experiment = experiment

    def on_experiment(self, _, experiment):
        self.text = experiment.name


class CooperativityRowButton(Button):
    cooperativity = ObjectProperty(Cooperativity.INDEPENDENT)
    values = [Cooperativity.INDEPENDENT, Cooperativity.COOPERATIVE, Cooperativity.COOPERATIVE_WITH_CATCHUP]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(cooperativity=self.on_cooperativity)
        self.text = str(self.cooperativity)
        self.dropdown = ConfigurationScreenDropDown()
        for cooperativity in CooperativityRowButton.values:
            dropdown_row_button = ConfigurationScreenDropDownRowButton(text=str(cooperativity), value=cooperativity)
            dropdown_row_button.bind(on_release=lambda button: self.dropdown.select(button.value))
            self.dropdown.add_widget(dropdown_row_button)
        self.dropdown.bind(on_select=self.on_select)

    def on_release(self):
        self.dropdown.open(self)

    def on_select(self, _, cooperativity):
        self.cooperativity = cooperativity

    def on_cooperativity(self, _, cooperativity):
        self.text = str(cooperativity)


class NumberInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if len(substring) + len(self.text) > 1 or not substring.isdigit():
            return
        else:
            return super().insert_text(substring, from_undo=from_undo)


class ConfigurationScreenDropDown(DropDown):
    pass


class ConfigurationScreenDropDownRowButton(Button):
    value = ObjectProperty(None)
