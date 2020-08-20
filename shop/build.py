import argparse
import os

from elasticsearch.helpers import bulk
from tqdm import tqdm

from . import search
from .database import Item
from .ext import Parser

parser = Parser()

# sudo systemctl start elasticsearch.service
def parse_price(string):
    return float(string.replace("'", ""))


def sql():
    parser.delete_items()
    for i, item in enumerate(parser.data()):
        item = parser.split_(item)
        try:
            parser.database.append(
                {
                    "name": item[0],
                    "cost": parse_price(item[2]),
                    "count": float(item[3]),
                }
            )
        except:
            parser.ban.append(i)
    parser.save_database()


def keywords():
    items = parser.items()
    for item in items:
        item.group = parser.table.contains(item.name.lower())
    Item.bulk_update(items, fields=[Item.group])


def indexing(new_item):
    search.add_to_index("items", new_item)


def gendata(items):
    for item in items:
        yield {
            "_index": "items",
            "name": item.name,
            "_type": "items",
            "_id": item.id,
        }


def elasticsearch():
    try:
        search.elasticsearch.indices.delete("items")
    except:
        pass

    items = parser.items()
    bulk(search.elasticsearch, gendata(items))


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--sql",
        action="store_true",
        default=False,
        help="build db from 1c txt file",
    )
    arg_parser.add_argument(
        "--key",
        action="store_true",
        default=False,
        help="build path db with keywords (table.INI)",
    )
    arg_parser.add_argument(
        "--search",
        action="store_true",
        default=False,
        help="index db with elasticsearch",
    )
    args = arg_parser.parse_args()
    if args.sql:
        sql()
    if args.key:
        keywords()
    if args.search:
        elasticsearch()
    if not args.sql and not args.key and not args.search:
        sql()
        keywords()
        elasticsearch()


if __name__ == "__main__":
    main()
