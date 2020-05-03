# https://gist.github.com/hmldd/44d12d3a61a8d8077a3091c4ff7b9307
from elasticsearch import Elasticsearch
from sqlalchemy import case

elasticsearch = Elasticsearch([{"host": "localhost", "port": 9200}])


def search(cls, expression, session):
    ids, _ = query_index(cls.__tablename__, expression)
    if len(ids) == 0:
        return None
    when = []
    for i in range(len(ids)):
        when.append((ids[i], i))
    return (
        session.query(cls)
        .filter(cls.id.in_(ids))
        .order_by(case(when, value=cls.id))
    )


def get_all(cls, session):
    ids = query_all(cls.__tablename__)
    if len(ids) == 0:
        return None
    when = []
    for i in range(len(ids)):
        when.append((ids[i], i))
    return (
        session.query(cls)
        .filter(cls.id.in_(ids))
        .order_by(case(when, value=cls.id))
    )


def add_to_index(index, model):
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload)


def remove_from_index(index, model):
    elasticsearch.delete(index=index, doc_type=index, id=model.id)


def process_hits(hits):
    return [int(item["_id"]) for item in hits]


def query_all(index):
    size = 10000
    data = elasticsearch.search(
        index=index,
        doc_type=index,
        scroll="2m",
        size=size,
        body={"query": {"match_all": {}}},
    )
    ids = []
    sid = data["_scroll_id"]
    scroll_size = len(data["hits"]["hits"])
    while scroll_size > 0:
        ids += process_hits(data["hits"]["hits"])
        data = elasticsearch.scroll(scroll_id=sid, scroll="2m")
        sid = data["_scroll_id"]
        scroll_size = len(data["hits"]["hits"])
    return ids


def query_index(index, query):
    search = elasticsearch.search(
        index=index,
        doc_type=index,
        body={
            "query": {
                "query_string": {
                    "query": query,
                    "default_operator": "AND",
                    "fields": [
                        "name"
                    ],
                    "fuzziness" : 2,
                }
            },
            "from": 0, 
            "size": 1000,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]
