import configparser

import data.db_session as db
from data.__all_models import *
from itertools import takewhile

import re


class Keyword:

    def __init__(self, keyword, routing):
        self.keyword = keyword
        self.routing = routing

    def __eq__(self, other):
        return re.fullmatch(self.keyword, other)


class KeywordTable:

    def __init__(self, keywords):
        self.keywords = keywords

    def __contains__(self, item):
        for i in self.keywords:
            if i == item:
                return True
        return False


def aslist_cronly(value):
    if isinstance(value, str):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return list(value)


config = configparser.ConfigParser()
config.read('table.INI')


TABLE = []
for key in config['table']:
    for keyword in aslist_cronly(config['table'][key]):
        TABLE.append(Keyword(keyword, key))
TABLE = KeywordTable(TABLE)

f = open('Остатки.txt', 'r', encoding='windows-1251').readlines()
f = list(map(lambda x: x.strip().split('\t'), f))

ban = []
ind = 9
p = 0
while ind < len(f):
    l = list(filter(lambda x: x.count(' ') != len(x), f[ind]))
    item = items.Item()
    item.name = str(l[0]).lower()
    if item.name in TABLE:
        p += 1
    ind += 1
# print(ban) # плохие их мало там \n
print(p)
