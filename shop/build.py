import argparse
import os
from multiprocessing import Pool

from dotenv import load_dotenv, set_key
from tqdm import tqdm

from . import search
from .database import Item
from .ext import Parser

load_dotenv()
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


def elasticsearch(c, processes):
    try:
        search.elasticsearch.indices.delete("items")
    except:
        pass
    items = [item for item in Item.select()]

    c = 3

    if c != -1:
        items = items[:c]
    for i in items:
        print(i.name)
    with Pool(processes=processes) as p:
        bar = tqdm(
            range(len(items)),
            desc="elasticsearch add",
            unit="line",
            bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        )
        for i, _ in enumerate(p.imap_unordered(indexing, items)):
            bar.update()
    print("=====")
    search.search(items[0], "21276MH G/2 FGD")


if __name__ == "__main__":
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

    arg_parser.add_argument(
        "--bench",
        action="store_true",
        default=False,
        help="benchmark elasticsearch",
    )

    arg_parser.add_argument(
        "--pool",
        type=int,
        default=int(os.getenv("POLL_PROCESSES")),
        required=False,
    )
    args = arg_parser.parse_args()
    if args.pool != int(os.getenv("POLL_PROCESSES")):
        # TODO type
        set_key(".env", "POLL_PROCESSES", str(args.pool))
        exit(0)
    if args.bench:
        elasticsearch(
            int(os.getenv("COUNT_SEARCH")), int(os.getenv("POLL_PROCESSES"))
        )
        exit(0)

    if args.sql:
        sql()
    if args.key:
        keywords()
    if args.search:
        elasticsearch(-1, args.pool)
    if not args.sql and not args.key and not args.search:
        sql()
        keywords()
        elasticsearch(-1, args.pool)
