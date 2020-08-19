# https://gist.github.com/hmldd/44d12d3a61a8d8077a3091c4ff7b9307
# sudo systemctl start elasticsearch.service
from elasticsearch import Elasticsearch

elasticsearch = Elasticsearch([{"host": "localhost", "port": 9200}])


def search(cls, expression):
    ids, _ = query_index(cls.__tablename__, expression)

    return 1
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
    elasticsearch.index(
        index=index,
        doc_type=index,
        id=model.id,
        body=payload,
        timeout="10000s",
    )


def remove_from_index(index, model):
    elasticsearch.delete(index=index, doc_type=index, id=model.id)


def process_hits(hits):
    return [int(item["_id"]) for item in hits]


def query_index(index, query):
    search = elasticsearch.search(
        index=index,
        doc_type=index,
        body={
            "query": {
                "query_string": {
                    "query": query,
                    "default_operator": "AND",
                    "fields": ["name"],
                    "fuzziness": 2,
                }
            },
            "from": 0,
            "size": 1000,
        },
    )
    return 1, 1
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]
