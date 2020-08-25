# https://www.w3schools.com/colors/colors_hex.asp
import re
import sys
from pathlib import Path
from pprint import pprint
from random import shuffle

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from .database import Config, Item
from .ext import parse_config

colors = list(
    map(lambda x: x.strip(), open("shop/color.txt", "r").readlines()[::2])
)
shuffle(colors)


class RegexEdit(QLineEdit):
    def __init__(self, qw):
        self.qw = qw
        super().__init__()

    def keyPressEvent(self, event):
        prev = self.text()
        QLineEdit.keyPressEvent(self, event)
        if prev != self.text():
            self.qw.search()


class Example(QWidget):
    def __init__(self):
        menu_file = Path(__file__).parent.joinpath("menu.txt")
        menu = list(map(str.strip, open(menu_file, "r").readlines()))
        self.menu_map = {"others": "x (no items)"}
        for el in menu:
            ind = el.find(" ")
            self.menu_map[el[:ind]] = el[ind + 1 :]
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("parser")
        main_layout = QHBoxLayout()
        config_layout = QVBoxLayout()
        regex_layout = QVBoxLayout()

        self.regex_editor = RegexEdit(self)
        self.regex_editor.setText(".*шланг.*")

        tab_widget = QTabWidget()
        self.search_tree = QTreeWidget()
        self.search_tree.setHeaderLabels(["name"])
        menu = QTextEdit()

        tab_widget.addTab(self.search_tree, "db")
        tab_widget.addTab(menu, "menu")

        self.text_edit = QTextEdit()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["name"])
        self.tree.setColumnWidth(0, 300)

        self.editor = QTextEdit()

        regex_layout.addWidget(self.regex_editor)
        regex_layout.addWidget(tab_widget)

        config_settings_layout = QHBoxLayout()

        self.config_name = QLineEdit("base")

        self.parse_button = QPushButton("parse")
        self.load_button = QPushButton("load")
        self.save_button = QPushButton("save")

        self.parse_button.clicked.connect(self.parse)
        self.load_button.clicked.connect(self.load_config)
        self.save_button.clicked.connect(self.save_config)

        config_settings_layout.addWidget(self.config_name)

        config_settings_layout.addWidget(self.parse_button)
        config_settings_layout.addWidget(self.load_button)
        config_settings_layout.addWidget(self.save_button)

        config_layout.addWidget(self.editor)
        config_layout.addLayout(config_settings_layout)
        config_layout.addWidget(self.tree)

        main_layout.addLayout(config_layout)
        main_layout.addLayout(regex_layout)
        self.setLayout(main_layout)

        self.search_tree.setStyleSheet(
            """
            QTreeWidget QHeaderView::section {
                font-size: 20px;
                background-color: #3C3F41;
                color:#BBBBBB;
            }
            QTreeWidget{
                font-size: 20px;
                font-weight:bold;
                background-color: #3C3F41;
                color:#BBBBBB;
            }"""
        )
        self.resize(1600, 1000)

        self.load_config()

        self.tree.setStyleSheet(
            """
            QTreeWidget QHeaderView::section {
                font-size: 20px;
                background-color: #3C3F41;
                color:#BBBBBB;
            }
            QTreeWidget{
                font-size: 20px;
                font-weight:bold;
                background-color: #3C3F41;
                color:#BBBBBB;
            }"""
        )

        self.parse()

    def get_color(self, my_path):
        for i, other_path in enumerate(self.keys):
            if other_path == my_path:
                return colors[i]

    def search(self):
        self.search_tree.clear()
        regex = self.regex_editor.text()
        name_group = {"others": []}  # name: 1.1.1
        for item in Item.select():
            name = item.name
            # try:
            if re.fullmatch(regex, name.lower()):
                if name not in self.name_group_map:
                    name_group["others"].append(name)
                else:
                    group = self.name_group_map[name]
                    if group not in name_group:
                        name_group[group] = []
                    name_group[group].append(name)
        keys = sorted(name_group.keys())
        keys.remove("others")
        keys.insert(0, "others")
        for i, path in enumerate(keys):
            top = QtWidgets.QTreeWidgetItem(
                self.search_tree,
                [f"{path} {self.menu_map[path]}  {len(name_group[path])}"],
            )

            if path in self.keys:
                top.setForeground(
                    0, QtGui.QBrush(QtGui.QColor(self.get_color(path)))
                )
            for name in name_group[path]:
                QtWidgets.QTreeWidgetItem(top, [name])

    def parse(self):
        self.tree.clear()
        try:
            m, warnings, self.name_group_map = parse_config(
                self.editor.toPlainText()
            )
        except:
            return 0
        self.keys = sorted(m.keys())

        cnt = 0
        for path in self.keys:
            cnt += len(m[path])
        for i, path in enumerate(self.keys):
            top = QtWidgets.QTreeWidgetItem(
                self.tree, [f"{path} {self.menu_map[path]}  {len(m[path])}"]
            )
            top.setForeground(0, QtGui.QBrush(QtGui.QColor(colors[i])))
            for name in m[path]:
                QtWidgets.QTreeWidgetItem(top, [name])
        self.search()

    def load_config(self):
        if (
            Config.select()
            .where(Config.name == self.config_name.text())
            .count()
            == 1
        ):
            self.editor.setText(
                Config.select()
                .where(Config.name == self.config_name.text())
                .get()
                .config
            )

    def save_config(self):
        if (
            Config.select()
            .where(Config.name == self.config_name.text())
            .count()
            == 0
        ):
            cfg = Config(
                name=self.config_name.text(), config=self.editor.toPlainText()
            )
        else:
            cfg = (
                Config.select()
                .where(Config.name == self.config_name.text())
                .get()
            )
            cfg.config = self.editor.toPlainText()
        cfg.save()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
