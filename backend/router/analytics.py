# 파생변수 기반 Top N 개 노드 반환
from fastapi import APIRouter, HTTPException
from typing import List
from models import TopNRequest, NodeScore
from db import get_db_collections
from bson.json_util import loads, dumps

router = APIRouter(tags=["Analytics"])

transfer_col, deriv_col = get_db_collections()

@router.post("/top-n", response_model=List[NodeScore])
def compute_top_n(request: TopNRequest):
    w1, w2, w3, w4 = request.w1, request.w2, request.w3, request.w4
    limit = request.limit

    pipeline = [
        {"$lookup": {"from": "derivative_stats", "localField": "fromAddress", "foreignField": "_id", "as": "from_stats"}},
        {"$unwind": "$from_stats"},
        {"$lookup": {"from": "derivative_stats", "localField": "toAddress", "foreignField": "_id", "as": "to_stats"}},
        {"$unwind": "$to_stats"},
        {"$addFields": {"score": {"$add": [
            {"$multiply": ["$from_stats.sent_tx_count", w1]},
            {"$multiply": ["$to_stats.recv_tx_count", w2]},
            {"$multiply": ["$from_stats.external_sent_tx_amount", w3]},
            {"$multiply": ["$to_stats.external_recv_tx_amount", w4]}
        ]}}},
        {"$sort": {"score": -1}},
        {"$limit": limit},
        {"$project": {
            "_id": 0,
            "address": "$toAddress",
            "score": 1,
            "sent_tx_count": "$from_stats.sent_tx_count",
            "recv_tx_count": "$to_stats.recv_tx_count",
            "external_sent_tx_amount": "$from_stats.external_sent_tx_amount",
            "external_recv_tx_amount": "$to_stats.external_recv_tx_amount"
        }}
    ]

    try:
        docs = list(transfer_col.aggregate(pipeline))
        result = [NodeScore(**loads(dumps(doc))) for doc in docs]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
