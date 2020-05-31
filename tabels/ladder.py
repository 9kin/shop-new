from flask_table import Table, Col, create_table, BoolCol

tbl_options = dict(classes=["table"], thead_classes=["thead-dark"])

ladder_cls = (
    create_table("TableCls", options=tbl_options)
    .add_column("name", Col("Арт."))
    .add_column("steps", Col("Кол-во ступеней"))
    .add_column("weight", Col("Вес, кг"))
    .add_column("platform_height", Col("высота до платформы, мм"))
    .add_column("working_height", Col("рабочая высота, мм"))
    .add_column(
        "belt", BoolCol("Страховочная лента", yes_display="+", no_display="-"),
    )
    .add_column("max_load", Col("Max нагрузка, кг"))
    .add_column("cost", Col("Цена"))
)

ladder = [
    dict(
        name="СМ3",
        steps="3",
        weight=5,
        platform_height=625,
        working_height=2825,
        belt=False,
        max_load=150,
        cost="Стремянка широкие 3 ступени (металл). СМ3",
    ),
    dict(
        name="СМ4",
        steps="4",
        weight=5.5,
        platform_height=845,
        working_height=3045,
        belt=False,
        max_load=150,
        cost="Стремянка широкие 4 ступени (металл). СМ4",
    ),
    dict(
        name="СМ5",
        steps="5",
        weight=6.7,
        platform_height=1070,
        working_height=3270,
        belt=True,
        max_load=150,
        cost=0,
    ),
    dict(
        name="СМ6",
        steps="6",
        weight=8.3,
        platform_height=1290,
        working_height=3490,
        belt=True,
        max_load=120,
        cost=0,
    ),
    dict(
        name="СМ7",
        steps="7",
        weight=10.1,
        platform_height=1510,
        working_height=3710,
        belt=True,
        max_load=120,
        cost=0,
    ),
    dict(
        name="СМ8",
        steps="8",
        weight=11,
        platform_height=1720,
        working_height=3920,
        belt=True,
        max_load=120,
        cost=0,
    ),
]
