import os
from typing import Optional, Tuple, Any
import argparse
import yaml
import inquirer
import shutil

SHARE_PATH = "create_project"
VARIABLE_OPENING = "@@"
VARIABLE_CLOSING = "@@"


def get_existing_subdirs(path_list: list[str], subdir: str) -> list[str]:
    """Gets subdirectories from a list of paths."""

    subdirs = map(lambda d: os.path.join(d, subdir), path_list)
    existing_subdirs = filter(os.path.exists, subdirs)

    return list(existing_subdirs)


def get_data_dirs() -> list[str]:
    """Gets XDG_DATA_DIRS environment variable and package data directory as
    list."""

    data_dirs = os.environ.get("XDG_DATA_DIRS")
    program_data_dirs = get_existing_subdirs(
        data_dirs.split(":"), SHARE_PATH) if data_dirs else []

    packageDataDir = os.path.dirname(__file__)

    return [packageDataDir] + program_data_dirs


def get_data_subdirs(subdir: str) -> list[str]:
    """Gets definitions path from XDG_DATA_DIRS if it exists."""
    return get_existing_subdirs(get_data_dirs(), subdir)


def get_definition(name: str) -> Optional[dict]:
    """Gets a definition from the definitions folder."""

    for data_dir in get_data_subdirs("definitions"):
        path = os.path.join(data_dir, name + ".yaml")

        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.load(f, Loader=yaml.FullLoader)

    return None


def get_template_dir(path: str) -> str:
    """Searches for template dir in data dirs"""
    for data_dir in get_data_subdirs("templates"):
        template_dir = os.path.join(data_dir, path)
        print(template_dir)

        if os.path.exists(template_dir):
            return template_dir

    raise Exception("Template not found.")


def convert_values_to_choices(dictionary: dict) -> list[Tuple[str, str]]:
    return [(v, k) for k, v in dictionary.items()]


def convert_to_inquiry(name: str, definition: dict):
    common_args = {
        "name": name,
        "message": definition.get("name", name),
        "default": definition.get("default", None),
    }

    switch = {
        "text": lambda: inquirer.Text(**common_args),
        "select": lambda:
            inquirer.List(
                choices=convert_values_to_choices(definition.get("values", {})),
                **common_args),
    }

    return switch.get(definition.get("type", "text"), lambda: None)()


def ask_variables(variable_definitions: dict) -> Any:
    questions = [convert_to_inquiry(k, v)
                 for k, v in variable_definitions.items()]

    return inquirer.prompt(questions)


def use_definition(template: dict, variables: dict) -> Tuple[str, dict]:
    """Asks for specified variables and return a template path with variables
    to replace."""

    variable_definitions = template.get("variables", {})
    new_variables = ask_variables(variable_definitions)

    result_variables = {**variables, **new_variables}

    if "path" in template:
        return template.get("path", ""), result_variables

    if "selection_variable" in template:
        selection_variable = template.get("selection_variable", "")
        selection = result_variables.get(selection_variable, None)

        if selection is None:
            raise Exception("Selection variable not found.")

        selected_template = template.get("templates", {}).get(selection, None)

        if selected_template is None:
            raise Exception("Selected template not found.")

        return use_definition(selected_template, result_variables)

    raise Exception("Invalid template.")


def copy_template(path: str, variables: dict, destination: str):
    """Copies directory and replaces variables in files."""
    template_dir = get_template_dir(path)

    # copy tree without permissions
    _orig_copystat = shutil.copystat
    shutil.copystat = lambda x, _: x
    shutil.copytree(template_dir, destination, copy_function=shutil.copyfile)
    shutil.copystat = _orig_copystat

    # replace variables
    for root, _, files in os.walk(destination):
        for file in files:
            file_path = os.path.join(root, file)

            with open(file_path, "r") as f:
                content = f.read()

            for k, v in variables.items():
                content = content.replace(
                    VARIABLE_OPENING + k.upper() + VARIABLE_CLOSING, v)

            with open(file_path, "w") as f:
                f.write(content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new project from a template.")

    parser.add_argument("definition", help="Name of the definition to use.")
    parser.add_argument("destination", help="Destination of template.")

    return parser.parse_args()


def main():
    args = parse_args()

    print(type(args))

    definition = get_definition(args.definition)

    if definition is None:
        print("Definition not found.")
        return

    path, variables = use_definition(definition.get("templates", {}), {})

    copy_template(path, variables, args.destination)
