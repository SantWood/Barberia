from bson import ObjectId
from datetime import datetime

def parse_id(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def parse_ids(docs):
    return [parse_id(doc) for doc in docs]

def validate_object_id(id_str):
    try:
        return ObjectId(id_str)
    except Exception:
        return None

def now_colombia():
    return datetime.utcnow()
