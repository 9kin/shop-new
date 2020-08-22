# https://github.com/mauricio-chavez/openpyxl-image-loader
from openpyxl import load_workbook
import io
import os
import string
from PIL import Image
import glob

class SheetImageLoader:
    _images = {}

    def __init__(self, sheet):
        sheet_images = sheet._images
        for image in sheet_images:
            self._images[image.anchor._from.row + 1] = image._data


    def get(self, row):
        if row in self._images:
            return io.BytesIO(self._images[row]())

def parse(sheet, start, end, name_index):
    image_loader = SheetImageLoader(sheet)
    rows = list(sheet.rows)
    l = []
    for row_i, row in enumerate(rows[start:end]):
        l.append((row[name_index].value, Image.open(image_loader.get(row_i + 1 + start))))
    return l

def main():
    APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORT_DIR = os.path.join(APP_PATH, "reports/")
    ADVARD_DIR = os.path.join(REPORT_DIR, "advard/")

    files = glob.glob(f'{ADVARD_DIR}*.xlsx')
    filename = files[0]
    wb = load_workbook(filename = filename)
    sheet = wb.active


    res = parse(sheet, 3, -1, 2)
    res[0][1].show()