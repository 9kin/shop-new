from PyInquirer import prompt as pypromt

from .build import main as build
from .image_compression import main as compress
from .json_parser import main as json_parser
from .lint import main as lint_project
from .parser_bs4 import main as parse_menu
from .ui import main as gui

# from .validate import main
# from .parser import main


def prompt(question):
    result = pypromt(question)
    if result == {}:
        exit(0)
    else:
        return result[question["name"]]


if __name__ == "__main__":
    answer = prompt(
        {
            "type": "rawlist",
            "name": "list",
            "message": "What do you want to do?",
            "choices": [
                "run gui",
                "compress images",
                "rebuild database (keywords)",
                "lint project",
                "json parse",  #  todo choose company
                "parse menu",
            ],
        }
    )
    if answer == "run gui":
        gui()
    elif answer == "compress images":
        compress()
    elif answer == "rebuild database (keywords)":
        build()
    elif answer == "lint project":
        lint_project()
    elif answer == "json parse":
        json_parser()
    elif answer == "parse menu":
        parse_menu()
