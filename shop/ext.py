import configparser

from peewee import chunked

from .database import Config, Image, Item, db
from .keywords import Keyword, KeywordTable, aslist_cronly
from .search import search
from .tables import Base, Ladder

table_map = {}
for table in [Base, Ladder]:
    table_map[table.__name__] = table


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
            if path == "DEFAULT":
                continue
            for key in config[path]:
                if key == "regex":
                    for regex in aslist_cronly(config[path][key]):
                        keywords.append(Keyword(regex, path))
        self.table = KeywordTable(keywords)
        self.remains = config["app"]["remains"]

    def items(self):
        return [item for item in Item.select()]


def cfg2json():
    base = Config.select().where(Config.id == 1).get()
    config = configparser.ConfigParser()
    config.read_string(base.config)
    items = {}
    for section in config:
        if section == "DEFAULT":
            continue
        items[section] = {}
        for key in config[section]:
            if key != "regex":
                items[section][key] = config[section][key]
    return items


class Route:
    def __init__(self):
        self.items = cfg2json()

    def routing(self, key):
        if key in self.items:
            return self.items[key]
        return None


def get_table(name):
    return table_map[name]


def items_path(path):
    path_list = []
    prev = ""
    try:
        for i in enumerate(path.split(".")):
            if i[0] != 0:
                prev += "."
            prev += str(i[1])
            path_list.append(menu_map[prev])
    except:
        path_list = []
    return path_list


# ext TODO
def validate_path(path: str):
    # SQL INJECTION
    for char in path:
        if not (char.isdigit() or char == "."):
            return False
    return True


#  TODO ext
def items2json(items):
    m = {item.id: item for item in items}
    imgs = Image.select().where(Image.name.in_(items))
    for i in imgs:
        m[i.name_id].img = i.path
    l = []
    for key in m:
        item = m[key]
        l.append(
            {
                "name": item.name,
                "count": item.count,
                "cost": item.cost,
                "img": item.img,
                "id": item.id,
            }
        )
    l.sort(key=lambda x: x["cost"])
    return l


def extract_items(path: str):
    items = Item.select().where(Item.group == path)
    if items:
        return items2json([i for i in items])
    return []


def search_items(query):
    if query is not None:
        items = search("items", Item, query.lower())
        return items2json(items)
    return []


def parse_config(config_text):
    config = configparser.ConfigParser()
    config.read_string(config_text)
    keywords = []
    for path in config:
        if path == "DEFAULT":
            continue
        for key in config[path]:
            if key == "regex":
                for regex in aslist_cronly(config[path][key]):
                    keywords.append(Keyword(regex, path))
    table = KeywordTable(keywords)

    m = {}
    warnings = []
    for item in Item.select():
        res = table.test_contains(item.name.lower())
        if len(res) != 0:
            if len(res) != 1:
                warnings.append([item, res])
            group = list(res)[0]
            if group not in m:
                m[group] = set()
            m[group].add(item.name)
    return m, warnings
