from fastapi import APIRouter

router = APIRouter(tags=["Utility"])

@router.get("/health")
def health_check():
    return {"status": "ok", "network": "cosmos"}
