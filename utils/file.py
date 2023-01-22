import codecs
import os
from pathlib import Path


def get_project_root():
    return Path(__file__).parent.parent


def save_data_safely(file_name, function):
    create_folders(file_name)
    file_path = get_free_file_path(file_name)
    print(f"Saving data as {file_path.name}")
    with codecs.open(str(file_path), "w", "utf-8") as file:
        function(file)


def get_free_file_path(file_name):
    file_path_requested = get_project_root() / file_name
    parent_path = file_path_requested.parent
    file_path = file_path_requested
    count = 1
    while file_path.is_file():
        file_name_alternative = file_path_requested.stem + f"_{count}" + file_path_requested.suffix
        file_path = parent_path / file_name_alternative
        count += 1
    return file_path


def create_file_and_write(file_name, function):
    create_folders(file_name)
    file_path = get_project_root() / file_name
    with codecs.open(str(file_path), "w", "utf-8") as file:
        function(file)


def create_folders(file_name):
    file_path = get_project_root() / file_name
    folder_path = file_path.parent
    folder_path.mkdir(parents=True, exist_ok=True)


def read_from_file(file_name, function):
    file_path = get_project_root() / file_name
    if not os.path.isfile(str(file_path)):
        return None
    with codecs.open(str(file_path), "r", "utf-8") as file:
        return function(file)
