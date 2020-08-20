from elasticsearch import Elasticsearch

elasticsearch = Elasticsearch([{"host": "localhost", "port": 9200}])


def search(index, model, expression):
    ids, _ = query_index(index, expression)
    if len(ids) == 0:
        return []
    items = [i for i in model.select().where(model.id.in_(ids))]
    m = {}
    for item in items:
        m[item.id] = item
    return [m[id] for id in ids]


def add_to_index(index, model):
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    e = elasticsearch.index(
        index=index,
        doc_type=index,
        id=model.id,
        body=payload,
        timeout="10000s",
    )


def remove_from_index(index, model):
    elasticsearch.delete(index=index, doc_type=index, id=model.id)


def query_index(index, query):
    # https://stackoverflow.com/a/40390310/13156381
    search = elasticsearch.search(
        index=index,
        doc_type=index,
        body={
            "query": {
                "simple_query_string": {
                    "query": query,
                    "default_operator": "AND",
                    "fields": ["name"],
                }
            },
            "from": 0,
            "size": 1000,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    return ids, search["hits"]["total"]
