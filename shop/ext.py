import configparser

from peewee import chunked

from .database import Item, db
from .keywords import Keyword, KeywordTable, aslist_cronly

total = None


def parse_price(string):
    return float(string.replace("'", ""))


class Parser:
    def __init__(self):
        self.cur_1c = 0
        self.cur_key = 0
        self.database_1c = []
        self.ban = []
        self.read_cfg()

    def next_1c(self):
        if self.cur_1c < len(self.data):
            item = self.split_(self.data[self.cur_1c])
            try:
                self.database_1c += [
                    {
                        "name": item[0],
                        "cost": parse_price(item[2]),
                        "count": float(item[3]),
                    }
                ]
            except:
                self.ban.append(self.cur_1c)
            self.cur_1c += 1

    def save_1c_database(self):
        with db.atomic():
            for batch in chunked(self.database_1c, 1000):
                Item.insert_many(batch).execute()

    def delete_items(self):
        db.drop_tables([Item])
        db.create_tables([Item])

    def load_data(self):
        self.data = list(
            map(
                lambda x: x.strip().split("\t"),
                open(self.remains, "r", encoding="windows-1251").readlines(),
            )
        )[9:-1]

    def split_(self, line):
        return list(filter(lambda x: x.count(" ") != len(x), line))

    def read_cfg(self):
        # add pewee database  TODO
        config = configparser.ConfigParser()
        config.read("shop/config.INI")
        self.table = KeywordTable(
            [
                Keyword(keyword, key)
                for key in config["table"]
                for keyword in aslist_cronly(config["table"][key])
            ]
        )
        self.remains = config["app"]["remains"]
        self.port = config["app"]["port"]

    def load_items(self):
        self.items = [item for item in Item.select()]

    def next_keyword(self):
        if self.cur_key < len(self.items):
            item = self.items[self.cur_key]
            res = self.table.contains(item.name.lower())
            if res != False:
                item.group = res
            item.save()
            self.cur_key += 1
