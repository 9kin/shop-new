from multiprocessing import Pool
import argparse
import sys
from tqdm import tqdm
import time
from ext import Parser
import search
from data.__all_models import *

parser = Parser()


# sudo systemctl start elasticsearch.service
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "--sql", action="store_true", default=False, help="build db from 1c txt file"
)
arg_parser.add_argument(
    "--key",
    action="store_true",
    default=False,
    help="build path db with keywords (table.INI)",
)
arg_parser.add_argument(
    "--search", action="store_true", default=False, help="index db with elasticsearch"
)

args = arg_parser.parse_args()


def sql():
    parser.delete_items()
    parser.get_data()
    bar = tqdm(
        range(len(parser.data)),
        desc="parse 1c",
        unit="line",
        bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
    )
    for i in bar:
        parser.next_1c()
    parser.session.commit()


def keywords():
    parser.get_items()
    bar = tqdm(
        range(len(parser.items)),
        desc="keywords",
        unit="line",
        bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
    )
    for i in bar:
        parser.next_keyword()
    parser.session.commit()


def indexing(new_item):
    search.add_to_index("items", new_item)


def elasticsearch():
    try:
        search.elasticsearch.indices.delete("items")
    except:
        pass
    new_items = parser.session.query(items.Item).all()
    if __name__ == "__main__":
        with Pool(processes=100) as p:
            bar = tqdm(
                range(len(new_items)),
                desc="elasticsearch add",
                unit="line",
                bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            )
            for i, _ in enumerate(p.imap_unordered(indexing, new_items)):
                bar.update()


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
