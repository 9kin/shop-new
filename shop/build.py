import argparse
import os

from elasticsearch.helpers import bulk
from tqdm import tqdm

from . import search
from .database import Item
from .ext import Parser

parser = Parser()

# sudo systemctl start elasticsearch.service


def sql():
    parser.delete_items()

    parser.load_data()

    bar = tqdm(
        range(len(parser.data)),
        desc="parse 1c",
        unit="line",
        bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
    )
    for i in bar:
        parser.next_1c()
    parser.save_1c_database()


def keywords():
    parser.load_items()
    bar = tqdm(
        range(len(parser.items)),
        desc="keywords",
        unit="line",
        bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
    )
    for i in bar:
        parser.next_keyword()


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

    items = [item for item in Item.select()]
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
