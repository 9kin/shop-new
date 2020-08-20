import configparser

from peewee import chunked

from .database import Item, Config, db
from .keywords import Keyword, KeywordTable, aslist_cronly

total = None


def parse_price(string):
    return float(string.replace("'", ""))


class Parser:
    def __init__(self):
        self.database = []
        self.ban = []
        self.read_cfg()

    def save_database(self):
        with db.atomic():
            for batch in chunked(self.database, 1000):
                Item.insert_many(batch).execute()

    def delete_items(self):
        db.drop_tables([Item])
        db.create_tables([Item])

    def data(self):
        return list(
            map(
                lambda x: x.strip().split("\t"),
                open(self.remains, "r", encoding="windows-1251").readlines(),
            )
        )[9:-1]

    def split_(self, line):
        return list(filter(lambda x: x.count(" ") != len(x), line))

    def read_cfg(self):
        base = Config.select().where(Config.id == 1).get()
        config = configparser.ConfigParser()
        config.read_string(base.config)
        keywords = []
        for path in config:
            if path == 'DEFAULT':
                continue
            for key in config[path]:
                if key == "regex":
                    for regex in aslist_cronly(config[path][key]):
                        keywords.append(Keyword(regex, path))
        self.table = KeywordTable(keywords)
        self.remains = config['app']['remains']
        
    def items(self):
        return [item for item in Item.select()]