import data.db_session as db
from data.__all_models import *


def parse_price(string):
    return float(string.replace("'", ''))


def main(db_path='db/items.sqlite'):

    db.global_init(db_path)
    session = db.create_session()

    for obj in session.query(items.Item).all():
        session.delete(obj)

    f = open('Остатки.txt', 'r', encoding='windows-1251').readlines()
    f = list(map(lambda x: x.strip().split('\t'), f))

    ban = []
    ind = 9
    while ind < len(f):
        l = list(filter(lambda x: x.count(' ') != len(x), f[ind]))
        try:
            item = items.Item()
            item.name = l[0]
            item.cost = parse_price(l[2])
            item.count = float(l[3])
            session.add(item)
        except:
            ban.append(ind)
        ind += 1
    session.commit()
    print(ban)  # плохие их мало там \n


if __name__ == '__main__':
    main()
