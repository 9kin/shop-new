from database import Item, db, Config
import configparser
from keywords import Keyword, KeywordTable, aslist_cronly
from tqdm import tqdm
from rich.console import Console
from pprint import pprint
import os

db.create_tables([Config])
configs = [config for config in Config.select()]


def parse_choose(s, choose):
    s = s.lower()
    if s in choose:
        return True
    else:
        return False


def parse_number(s, mx, not_valid):
    if s == "":
        return mx - 1
    elif s.isdecimal() and 0 <= int(s) < mx and int(s) not in not_valid:
        return int(s)
    else:
        return -1


YN = "[[[green bold]y[/]/[red bold]n[/]]]"

console = Console(force_terminal=True)


def cprint(string):
    console.print(string, end="")


def input_yn():
    return parse_choose(input(), ["", "yes", "y"])


def input_config(configs, not_valid=[]):
    i = 0
    for config in configs:
        if i in not_valid:
            color = "red"
        else:
            color = "green"
        cprint(f"{i} [{color} bold]{config.name}[/]\n\n")
        i += 1
    n = -1
    while n == -1:
        cprint(f"type number or (enter for last) ")
        n = parse_number(input(), len(configs), not_valid=not_valid)
    cprint(f"you choose [green bold]{configs[n].name}[/]\n\n")
    return n, configs[n]


cprint(f"use config from database {YN} ")
yn = input_yn()
if not yn:
    cprint(
        "[green bold]edit[/] or [red bold]create[/] new config [[[green bold]1[/]/[red bold]2[/]]] "
    )
    yn = parse_choose(input(), ["", "1"])
    if yn:
        cprint("choose config from db\n\n")
        _, cfg = input_config(configs)
    else:
        cprint("choose config name ")
        name = input()
        cfg = Config(name=name, config="")
    file = ""
    while not (os.path.isfile(file) and os.path.exists(file)):
        cprint("input file ")
        file = input()
    data = open(file).read()
    cfg.config = data
    cfg.save()
    exit(0)


first, config1 = input_config(configs)
cprint(f"compare with [red bold]base[/] configuration {YN} ")
yn = input_yn()
if not yn:
    second, config2 = input_config(configs, not_valid=[first])
else:
    second, config2 = 0, configs[0]


def parse_config(config):
    parser = configparser.ConfigParser()
    parser.read_string(config.config)

    table = KeywordTable(
        [
            Keyword(keyword, key)
            for key in parser["table"]
            for keyword in aslist_cronly(parser["table"][key])
        ]
    )

    items = [item for item in Item.select()]

    bar = tqdm(
        items,
        desc="keywords",
        unit="line",
        bar_format="{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
    )

    m = {}
    warnings = []
    for item in bar:
        res = table.test_contains(item.name.lower())
        if len(res) != 0:
            if len(res) != 1:
                warnings.append([item, res])
            group = list(res)[0]
            if group not in m:
                m[group] = set()
            m[group].add(item.name)
    return m, warnings


m1, warnings1 = parse_config(config1)
m2, warnings2 = parse_config(config2)
cnt_1, cnt_2 = 0, 0

keys = sorted(list(set(m1.keys()) | set(m2.keys())))
for group in keys:
    f = set()
    if group in m1:
        f = m1[group]
        cnt_1 += len(f)
    s = set()
    if group in m2:
        s = m2[group]
        cnt_2 += len(s)
    plus = f - s
    minus = s - f
    cprint(
        f"[white bold]{group}[/] [green bold]+{len(plus)}[/] [red bold]-{len(minus)}[/]\n\n"
    )
    for item in sorted(list(plus)):
        cprint(f"[green bold]{item}[/]\n\n")
    for item in sorted(list(minus)):
        cprint(f"[red bold]{item}[/]\n\n")
print(cnt_1, cnt_2)
