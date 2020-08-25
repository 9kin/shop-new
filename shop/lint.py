from os import system
from pathlib import Path

import isort


def main():
    APP_DIR = Path(__file__).resolve().parent
    files = list(APP_DIR.parent.glob("*.py")) + list(APP_DIR.glob("*.py"))
    for file in files:
        isort.file(file)
    system("black . --line-length 79")
