import sys
from tqdm import tqdm
import time
from ext import Parser
import search
from data.__all_models import *

parser = Parser()

parser.delete_items()
parser.get_data()
first = tqdm(
    range(len(parser.data)),
    desc="parse 1c",
    unit="line",
    bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
)
for i in first:
    parser.next_1c()
parser.session.commit()


parser.read_cfg()
parser.get_items()
second = tqdm(
    range(len(parser.items)),
    desc="keywords",
    unit="line",
    bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
)

for i in second:
    parser.next_keyword()
parser.session.commit()

try:
    search.elasticsearch.indices.delete("items")
except:
    pass
items = parser.session.query(items.Item).all()[:50]

third = tqdm(
    range(len(items)),
    desc="elasticsearch add",
    unit="line",
    bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
)


for i in third:
    search.add_to_index("items", items[i])
