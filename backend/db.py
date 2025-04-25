# backend/db.py
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME  = os.getenv("DB_NAME",  "2ec-database")


def get_db_collections():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db["transfer_data"], db["derivative_stats"]