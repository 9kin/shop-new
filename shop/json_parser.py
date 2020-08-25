import base64
import json
import re
from pathlib import Path
from pprint import pprint

from .database import Image, Item


def load_json(file_name):
    with open(file_name, encoding="utf-8-sig") as f:
        return json.load(f)


def json_parse(file_name, img_dir):
    items = load_json(file_name)["goods"]
    for item in items:
        name = item["name"]
        img_data = item["picture"].encode()

        cnt = Item.select().where(Item.name.startswith(name)).count()
        if cnt != 1:
            continue
        item_model = Item.select().where(Item.name.startswith(name)).get()
        name = re.sub("[!@#$/]", " ", name)

        filename = img_dir.joinpath(f"{name}.jpg")
        filename.touch()
        with open(filename, "wb") as f:
            f.write(base64.decodebytes(img_data))

        filename = Path("advard").joinpath(f"{name}.jpg")

        if Image.select().where(Image.name == item_model.name).count() == 0:
            Image.create(name=item_model.name, path=filename)
        else:
            image_model = (
                Image.select().where(Image.name == item_model.name).get()
            )
            image_model.path = filename
            image_model.save()


def main():
    APP_DIR = Path(__file__).resolve().parent.parent
    ADVARD_DIR = APP_DIR.joinpath("reports", "advard")

    ADVAR_IMG_DIR = Path("static").joinpath("img_full", "advard")

    files = [file for file in ADVARD_DIR.glob("*.json")]

    file = files[0]
    json_parse(file, ADVAR_IMG_DIR)
