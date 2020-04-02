from elasticsearch import Elasticsearch
from sqlalchemy import case

elasticsearch = Elasticsearch([{"host": "localhost", "port": 9200}])


def search(cls, expression, page, per_page, session):
    ids, _ = query_index(cls.__tablename__, expression, page, per_page)
    if len(ids) == 0:
        return None
    when = []
    for i in range(len(ids)):
        when.append((ids[i], i))
    return session.query(cls).filter(cls.id.in_(ids)).order_by(case(when, value=cls.id))


def add_to_index(index, model):
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    elasticsearch.index(index=index, doc_type=index, id=model.id, body=payload)


def remove_from_index(index, model):
    elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query, page, per_page):
    search = elasticsearch.search(
        index=index,
        doc_type=index,
        body={
            "query": {"multi_match": {"query": query, "fields": ["*"]}},
            "from": (page - 1) * per_page,
            "size": per_page,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]
