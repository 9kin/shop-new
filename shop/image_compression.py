# https://www.youtube.com/watch?v=OFtqNy6PEeE
# https://www.mankier.com/1/jpegoptim
# https://www.mankier.com/1/pngquant
import json
import subprocess
from pathlib import Path
from shutil import copyfile, rmtree

from PIL import Image


def jpegoptim(file_name):
    dest = Path(str(file_name).replace("img_full", "img")).parent
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "jpegoptim",
            file_name,
            "--strip-all",
            "--all-progressive",
            "--max=80",
            f"--dest={dest}",
        ],
        stdout=subprocess.PIPE,
    )


def pngquant(file_name):
    dest = Path(str(file_name).replace("img_full", "img"))
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        f"pngquant --skip-if-larger --quality=50-90 --speed 1 --strip -o {str(dest)} {str(file_name)}",
        shell=True,
    )


def main():
    JSON_PATH = (
        Path(__file__).resolve().parent.joinpath("image_compression.json")
    )
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_DIR = BASE_DIR.joinpath("static")
    IMG_DIR = STATIC_DIR.joinpath("img")
    IMG_FULL_DIR = STATIC_DIR.joinpath("img_full")

    jpg_files = list(IMG_FULL_DIR.rglob("*.jpg"))
    JSON_DATA = json.load(open(JSON_PATH, "r"))

    rmtree(str(IMG_DIR), ignore_errors=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    for file_name in jpg_files:
        jpegoptim(file_name)

    for file_name in JSON_DATA:
        for size in JSON_DATA[file_name]:
            path = IMG_DIR.joinpath(file_name)
            im = Image.open(str(path))
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(f'{path.with_suffix("")}_{size[0]}x{size[1]}.jpg')

    png_files = list(IMG_FULL_DIR.rglob("*.png"))
    for file_name in png_files:
        pngquant(file_name)

    copy_files = list(IMG_FULL_DIR.rglob("*.webp")) + list(
        IMG_FULL_DIR.rglob("*.ico")
    )
    for file_name in copy_files:
        file_name.parent.mkdir(parents=True, exist_ok=True)
        copyfile(str(file_name), str(file_name).replace("img_full", "img"))
