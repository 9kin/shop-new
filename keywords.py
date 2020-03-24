import configparser
import re
import data.db_session as db
from data.__all_models import *


class Keyword:

    def __init__(self, keyword, routing):
        self.keyword = keyword
        self.routing = routing

    def __eq__(self, other):
        return re.fullmatch(self.keyword, other)


class KeywordTable:

    def __init__(self, keywords):
        self.keywords = keywords

    def contains(self, item):
        for key in self.keywords:
            if key == item:
                return key.routing
        return False


def aslist_cronly(value):
    if isinstance(value, str):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return list(value)



def main(db_path='db/items.sqlite'):
    db.global_init(db_path)
    session = db.create_session()
    db_items = session.query(items.Item).all()

    config = configparser.ConfigParser()
    config.read('table.INI')
    TABLE = []
    for key in config['table']:
        for keyword in aslist_cronly(config['table'][key]):
            TABLE.append(Keyword(keyword, key))
    TABLE = KeywordTable(TABLE)

    p = 0
    for item in db_items:
        res = TABLE.contains(item.name.lower())
        if res != False:
            print(item.name)
            item.group = res
            p += 1
    print(p)

    session.commit()


if __name__ == '__main__':
    main()
