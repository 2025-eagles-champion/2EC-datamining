# node-link, sankey 통합 버전
from fastapi import APIRouter, HTTPException
from typing import List
from models import NodeDetail
from db import get_db_collections
import pandas as pd
import os

router = APIRouter(tags=["Graph"])

# total_stats.csv 읽어오기
# (데이터 경로는 프로젝트 구조에 맞게 조정해)
TOTAL_STATS_PATH = os.path.join(os.path.dirname(__file__), "../data/total_stats.csv")
total_stats_df = pd.read_csv(TOTAL_STATS_PATH, index_col=0)

# Mongo 연결 (혹시 나중에 필요할 수도 있으니 일단 유지)
transfer_col, deriv_col = get_db_collections()

@router.get("/graph/nodes", response_model=List[NodeDetail])
def get_all_nodes():
    try:
        nodes = []
        for address, row in total_stats_df.iterrows():
            node = {
                "address": address,
                "sent_tx_count": row.get("sent_tx_count", 0),
                "sent_tx_amount": row.get("sent_tx_amount", 0),
                "recv_tx_count": row.get("recv_tx_count", 0),
                "recv_tx_amount": row.get("recv_tx_amount", 0),
                "external_sent_tx_count": row.get("external_sent_tx_count", 0),
                "external_sent_tx_amount": row.get("external_sent_tx_amount", 0),
                "external_recv_tx_count": row.get("external_recv_tx_count", 0),
                "external_recv_tx_amount": row.get("external_recv_tx_amount", 0),
                "hour_entropy": row.get("hour_entropy", 0),
                "first_date": int(row.get("first_date", 0)),
                "last_date": int(row.get("last_date", 0)),
                "active_days_count": row.get("active_days_count", 0),
                "counterparty_count_sent": row.get("counterparty_count_sent", 0),
                "counterparty_count_recv": row.get("counterparty_count_recv", 0),
                "sent_tx_amount_mean": row.get("sent_tx_amount_mean", 0),
                "recv_tx_amount_mean": row.get("recv_tx_amount_mean", 0),
                "external_sent_tx_amount_mean": row.get("external_sent_tx_amount_mean", 0),
                "external_recv_tx_amount_mean": row.get("external_recv_tx_amount_mean", 0),
                "pagerank": range([0, 1, 2, 3, 4, 5])[0],  # 더미값  
                "tier": range(["bronze","silver", "gold"])[0],  # 더미값
            }
            nodes.append(node)
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
