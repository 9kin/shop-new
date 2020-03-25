import re


def aslist_cronly(value):
    if isinstance(value, str):
        value = filter(None, [x.strip() for x in value.splitlines()])
    return list(value)


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
