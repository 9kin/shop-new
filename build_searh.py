import datetime
import data.db_session as db
from data.__all_models import *
import search

db.global_init("db/items.sqlite")
session = db.create_session()


# query = search.search(items.Item, "тиски", 1, 5, session)


now = datetime.datetime.now()

search.elasticsearch.indices.delete("items")
print(datetime.datetime.now() - now, "elastic delete")

now = datetime.datetime.now()
for post in session.query(items.Item).all()[:50]:
    search.add_to_index("items", post)
print(datetime.datetime.now() - now, "elastic add")


now = datetime.datetime.now()
print(search.query_index("items", "д/раковины", 1, 100))
print(datetime.datetime.now() - now, "elastic search")
