import codecs
import os
from pathlib import Path


def get_project_root():
    return Path(__file__).parent.parent


def create_file_and_write(file_name, function):
    file_path = get_project_root() / file_name
    folder_path = file_path.parent
    folder_path.mkdir(parents=True, exist_ok=True)
    with codecs.open(str(file_path), "w", "utf-8") as file:
        function(file)


def read_from_file(file_name, function):
    if not os.path.isfile(file_name):
        return None
    with codecs.open(str(file_name), "r", "utf-8") as file:
        return function(file)
