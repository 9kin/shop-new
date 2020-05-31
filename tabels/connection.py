from flask_table import Table, Col, create_table, BoolCol

tbl_options = dict(
    classes=["table table-striped table-bordered"],
    thead_classes=["thead-dark"],
)


cls = (
    create_table("TableCls", options=tbl_options)
    .add_column("name", Col("Название"))
    .add_column("cost", Col("Цена"))
    .add_column("count", Col("Количество"))
)

tabel = True
