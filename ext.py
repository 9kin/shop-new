import data.db_session as db
from data.__all_models import *
from keywords import Keyword, KeywordTable, aslist_cronly
import configparser

total = None


def parse_price(string):
    return float(string.replace("'", ""))


class Parser:
    def __init__(self, db_path="db/items.sqlite"):
        db.global_init(db_path)
        self.session = db.create_session()
        self.cur_1c = 0
        self.cur_key = 0
        self.ban = []
        self.read_cfg()

    def next_1c(self):
        if self.cur_1c < len(self.data):
            item = self.split_(self.data[self.cur_1c])
            try:
                self.add_item(item)
            except:
                self.ban.append(self.cur_1c)
            self.cur_1c += 1

    def parse_1c(self):
        self.delete_items()
        self.get_data()
        for ind in range(len(self.data)):
            self.next_1c()
        self.session.commit()

    def delete_items(self):
        for obj in self.session.query(items.Item).all():
            self.session.delete(obj)
        self.session.commit()

    def get_data(self):
        self.data = list(
            map(
                lambda x: x.strip().split("\t"),
                open(self.remains, "r", encoding="windows-1251").readlines(),
            )
        )[9:]

    def add_item(self, item):
        self.session.add(
            items.Item(name=item[0], cost=parse_price(item[2]), count=float(item[3]))
        )

    def split_(self, line):
        return list(filter(lambda x: x.count(" ") != len(x), line))

    def read_cfg(self):
        config = configparser.ConfigParser()
        config.read("config.INI")
        self.TABLE = KeywordTable(
            [
                Keyword(keyword, key)
                for key in config["table"]
                for keyword in aslist_cronly(config["table"][key])
            ]
        )
        self.remains = config["app"]["remains"]
        self.port = config["app"]["port"]

    def get_items(self):
        self.items = self.session.query(items.Item).all()

    def next_keyword(self):
        if self.cur_key < len(self.items):
            item = self.items[self.cur_key]
            res = self.TABLE.contains(item.name.lower())
            if res != False:
                # print(item.name)
                item.group = res
            self.cur_key += 1

    def parse_keyword(self):
        self.read_cfg()
        self.get_items()
        for item in range(len(self.items)):
            self.next_keyword()
        self.session.commit()


if __name__ == "__main__":
    q = Parser()
    # q.parse_1c()
    q.parse_keyword()
