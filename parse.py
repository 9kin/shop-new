import data.db_session as db
from data.__all_models import *

db.global_init('db/items.sqlite')
session = db.create_session()


f = open('ostatki.txt', 'r', encoding='windows-1251').readlines()
f = list(map(lambda x: x.strip().split('\t'), f))


def parse_price(string):
    return float(string.replace("'", ''))


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
print(ban) # плохие их мало там \n
