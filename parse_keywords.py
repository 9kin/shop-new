from keywords import Keyword, KeywordTable, aslist_cronly
import configparser
import re
import data.db_session as db
from data.__all_models import *




def main(db_path='db/items.sqlite'):
    db.global_init(db_path)
    session = db.create_session()
    db_items = session.query(items.Item).all()

    config = configparser.ConfigParser()
    config.read('table.INI')
    TABLE = KeywordTable([Keyword(keyword, key) for key in config['table']
                      for keyword in aslist_cronly(config['table'][key])])


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
