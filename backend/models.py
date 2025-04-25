from pydantic import BaseModel, Field

class TopNRequest(BaseModel):
    w1: float = Field(..., description="Weight for sent_tx_count")
    w2: float = Field(..., description="Weight for recv_tx_count")
    w3: float = Field(..., description="Weight for external_sent_tx_amount")
    w4: float = Field(..., description="Weight for external_recv_tx_amount")
    limit: int   = Field(..., gt=0, description="Number of top addresses to return")

class NodeScore(BaseModel):
    address: str
    score: float
    sent_tx_count: int
    recv_tx_count: int
    external_sent_tx_amount: float
    external_recv_tx_amount: float