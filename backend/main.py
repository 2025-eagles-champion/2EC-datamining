from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from router import health, graph, analytics

app = FastAPI(
    title="Cosmos Network Transaction Analytics API",
    description="Node-Link & Sankey 다이어그램을 제공하는 Cosmos 트랜잭션 시각화 ",
    version="1.0.0"
)

# 라우터 등록
app.include_router(health.router)
app.include_router(graph.router)
app.include_router(analytics.router)

# 예외처리 핸들러
@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
