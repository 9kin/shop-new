import configparser
import os
from pprint import pprint

from prompt_toolkit.validation import ValidationError, Validator
from PyInquirer import Separator, print_json
from PyInquirer import prompt as pypromt
from rich import print

from .database import Config, Item, db
from .ext import parse_config
from .keywords import Keyword, KeywordTable, aslist_cronly


def cprint(string):
    print(string, end="")


class FileValidator(Validator):
    def validate(self, document):
        exp = ValidationError(
            message="Please enter a correct file",
            cursor_position=len(document.text),
        )
        file = document.text
        if not (os.path.isfile(file) and os.path.exists(file)):
            raise exp


def prompt(question):
    result = pypromt(question)
    if result == {}:
        exit(0)
    else:
        return result[question["name"]]


def get(answer, key):
    if answer == {}:
        exit(0)
    else:
        return answer[key]


def get_configs(not_valid=[]):
    choices = []
    for i, config in enumerate(Config.select()):
        if i in not_valid:
            choices.append(Separator(config.name))
        else:
            choices.append(config.name)
    return choices


def choose_config(not_valid=[]):
    config_name = prompt(
        {
            "type": "rawlist",
            "message": "Select config?",
            "name": "config",
            "choices": get_configs(not_valid=not_valid),
        }
    )
    return Config.select().where(Config.name == config_name).get()


def input_file():
    return prompt(
        {
            "type": "input",
            "name": "config_name",
            "message": "Type file name (INI)?",
            "validate": FileValidator,
        }
    )


def main():
    db.create_tables([Config])

    confirm = prompt(
        {
            "type": "confirm",
            "message": "Use config from database?",
            "name": "confirm",
            "default": True,
        }
    )

    if not confirm:
        question = {
            "type": "rawlist",
            "name": "list",
            "message": "What do you want to do?",
            "choices": ["Edit config", "Create new config",],
        }
        choose = prompt(question)
        if choose == "Edit config":
            config = choose_config()
        else:
            name = prompt(
                {
                    "type": "input",
                    "name": "config_name",
                    "message": "Type config name?",
                }
            )
            config = Config(name=name, config="")
        config.config = open(input_file()).read()
        config.save()
        exit(0)
    first = choose_config()
    second = choose_config(not_valid=[first.id - 1])

    m1, warnings1 = parse_config(first.config)
    m2, warnings2 = parse_config(second.config)
    cnt_1, cnt_2 = 0, 0

    keys = sorted(list(set(m1.keys()) | set(m2.keys())))
    for group in keys:
        f = set()
        if group in m1:
            f = m1[group]
            cnt_1 += len(f)
        s = set()
        if group in m2:
            s = m2[group]
            cnt_2 += len(s)
        plus = s - f
        minus = f - s
        cprint(
            f"[white bold]{group}[/] [green bold]+{len(plus)}[/] [red bold]-{len(minus)}[/]\n"
        )
        for item in sorted(list(plus)):
            cprint(f"[green bold]{item}[/]\n")
        for item in sorted(list(minus)):
            cprint(f"[red bold]{item}[/]\n")
    print(cnt_1, cnt_2)
