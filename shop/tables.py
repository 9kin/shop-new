from flask_table import BoolCol, Col, Table, create_table

table_option = dict(
    classes=[
        "table table-striped table-bordered table-sm text-center table-hover"
    ],
    thead_classes=["thead-dark thead-f"],
)


class Base:
    table = (
        create_table("TableCls", options=table_option)
        .add_column("name", Col("Название"))
        .add_column("cost", Col("Цена"))
        .add_column("count", Col("Количество"))
    )
    data = None


class Ladder:
    table = (
        create_table("TableCls", options=table_option)
        .add_column("name", Col("Арт."))
        .add_column("cost", Col("Цена"))
        .add_column("steps", Col("Кол-во ступеней"))
        .add_column("weight", Col("Вес"))
        .add_column("platform_height", Col("высота до платформы"))
        .add_column("working_height", Col("высота"))
        .add_column(
            "belt",
            BoolCol("Страховочная лента", yes_display="+", no_display="-"),
        )
    )

    data = [
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
            cost="Стремянка широкие 5 ступеней (металл). СМ5",
        ),
        dict(
            name="СМ6",
            steps="6",
            weight=8.3,
            platform_height=1290,
            working_height=3490,
            belt=True,
            max_load=120,
            cost="Стремянка широкие 6 ступеней (металл). СМ6",
        ),
        dict(
            name="СМ7",
            steps="7",
            weight=10.1,
            platform_height=1510,
            working_height=3710,
            belt=True,
            max_load=120,
            cost="Стремянка широкие 7 ступеней (металл). СМ7",
        ),
        dict(
            name="СМ8",
            steps="8",
            weight=11,
            platform_height=1720,
            working_height=3920,
            belt=True,
            max_load=120,
            cost="Стремянка широкие 8 ступеней (металл). СМ8",
        ),
    ]
