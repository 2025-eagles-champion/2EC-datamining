from pydantic import BaseModel, Field
from typing import List

# --- Top-N 관련 ---
class TopNRequest(BaseModel):
    w1: float = Field(..., description="Weight for sent_tx_count")
    w2: float = Field(..., description="Weight for recv_tx_count")
    w3: float = Field(..., description="Weight for external_sent_tx_amount")
    w4: float = Field(..., description="Weight for external_recv_tx_amount")
    limit: int = Field(..., gt=0, description="Number of top addresses to return")

class NodeScore(BaseModel):
    address: str
    score: float
    sent_tx_count: int
    recv_tx_count: int
    external_sent_tx_amount: float
    external_recv_tx_amount: float

# --- Graph (Node-Link 다이어그램) 관련 ---
class Link(BaseModel):
    source: str
    target: str
    value: float
    denom: str
    timestamp: int

class Node(BaseModel):
    id: str

class GraphData(BaseModel):
    nodes: List[Node]
    links: List[Link]

# --- Sankey 다이어그램 관련 ---
class SankeyLink(BaseModel):
    source: str
    target: str
    value: float
    denom: str
    fromChain: str
    toChain: str
    timestamp: int

class SankeyData(BaseModel):
    links: List[SankeyLink]
