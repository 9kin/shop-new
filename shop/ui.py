import re
import sys

from PyQt5 import QtWidgets
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


class RegexEdit(QLineEdit):
    def __init__(self, qw):
        self.qw = qw
        super().__init__()

    def keyPressEvent(self, event):
        QLineEdit.keyPressEvent(self, event)
        self.qw.searh()


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def e(self):
        print("e")

    def initUI(self):
        self.setWindowTitle("parser")
        main_layout = QHBoxLayout()
        config_layout = QVBoxLayout()
        regex_layout = QVBoxLayout()

        self.regex_editor = RegexEdit(self)
        self.regex_editor.setText(".*стремянка.*")

        tab_widget = QTabWidget()
        self.search_edit = QTextEdit()
        menu = QTextEdit()

        tab_widget.addTab(self.search_edit, "db")
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

        # self.setStyleSheet(
        #    "QWidget {background-color: #3C3F41; color: #BBBBBB; }"
        # )
        self.resize(1000, 480)

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
        menu = list(map(str.strip, open("shop/menu.txt", "r").readlines()))

        self.menu_map = {"others": "x"}
        for el in menu:
            ind = el.find(" ")
            self.menu_map[el[:ind]] = el[ind + 1 :]
        self.parse()
        self.searh()

    def searh(self):
        s = ""
        regex = self.regex_editor.text()
        for item in Item.select():
            name = item.name
            try:
                if re.fullmatch(regex, name.lower()):
                    s += name + "\n"
            except:
                self.search_edit.setText("<b>ERROR</b>")
                return 0
        self.search_edit.setText(s)

    def load_config(self):
        cnt = (
            Config.select()
            .where(Config.name == self.config_name.text())
            .count()
        )
        if cnt == 1:
            self.editor.setText(
                Config.select()
                .where(Config.name == self.config_name.text())
                .get()
                .config
            )

    def save_config(self):
        cnt = (
            Config.select()
            .where(Config.name == self.config_name.text())
            .count()
        )
        if cnt == 0:
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

    def parse(self):
        self.tree.clear()
        try:
            m, warnings1 = parse_config(self.editor.toPlainText())
        except:
            return 0
        keys = sorted(m.keys())
        for path in keys:
            top = QtWidgets.QTreeWidgetItem(
                self.tree, [f"{path} {self.menu_map[path]}  {len(m[path])}"]
            )
            for names in m[path]:
                QtWidgets.QTreeWidgetItem(top, [names])


def main():
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
