from pymongo import ReturnDocument
from datetime import datetime
from core.mongo import get_db

db = get_db()

def generate_proposal_no(client_code):
    year = datetime.now().year

    counter = db.proposal_counters.find_one_and_update(
        {"_id": client_code},
        {"$inc": {"last_sequence": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    seq = str(counter["last_sequence"]).zfill(3)
    return f"{client_code}-PROP-{year}-{seq}"
