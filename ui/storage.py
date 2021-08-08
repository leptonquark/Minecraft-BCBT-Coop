import codecs
import json
import os

from utils.file import create_file_and_write, read_from_file

CONFIG_STORAGE_FILE_NAME = "data/config.json"

GOAL_TYPE_DATA_NAME = "GoalType"
CONDITION_TYPE_DATA_NAME = "ConditionType"
ITEM_TYPE_DATA_NAME = "ItemType"
BLUEPRINT_TYPE_DATA_NAME = "BlueprintType"


def save_data(data):
    create_file_and_write(CONFIG_STORAGE_FILE_NAME, lambda file: json.dump(data, file))


def load_data():
    data = read_from_file(CONFIG_STORAGE_FILE_NAME, json.load)
    return data if data is not None else {}
