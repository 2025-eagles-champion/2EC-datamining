from fastapi import FastAPI, Query, HTTPException
from typing import List
from pydantic import BaseModel
from pymongo import MongoClient
from bson.json_util import dumps
import os


# FastAPI app
app = FastAPI(
    title="Cosmos Network Transaction Analytics API",
    description="Real-time Top-N Cosmos addresses by weighted transaction metrics.",
    version="1.0.0"
)