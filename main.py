from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
from datetime import datetime

app = FastAPI()

# CSV 데이터 로딩 함수
def load_and_process_data(csv_path: str):
    # CSV 데이터 읽기
    df = pd.read_csv(csv_path)

    # 필수 항목만 추출
    df = df[["Sender", "Receiver", "Token", "Amount", "Timestamp", "Network"]]

    # 컬럼명 변경
    df.columns = ["sender", "receiver", "token", "amount", "timestamp", "network"]

    # timestamp를 사람이 읽기 좋은 형태로 변환 (ISO 형식)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    return df.to_dict(orient='records')

# 루트 경로: 간단한 테스트용
@app.get("/")
async def root():
    return {"message": "FastAPI Server is running!"}

# 모든 거래내역 반환 API
@app.get("/transactions")
async def get_transactions():
    try:
        data = load_and_process_data("./data/transfers_test.csv")
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# 특정 날짜의 거래내역 조회 API (예: 2025-03-01)
@app.get("/transactions/date/{date}")
async def get_transactions_by_date(date: str):
    try:
        df = pd.read_csv("./data/transfers_test.csv")
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit='s')
        df["date"] = df["Timestamp"].dt.strftime('%Y-%m-%d')

        filtered_df = df[df["date"] == date]

        # 필수 항목만 추출하여 반환
        filtered_df = filtered_df[["Sender", "Receiver", "Token", "Amount", "Timestamp", "Network"]]
        filtered_df.columns = ["sender", "receiver", "token", "amount", "timestamp", "network"]
        filtered_df["timestamp"] = filtered_df["timestamp"].dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        return JSONResponse(content=filtered_df.to_dict(orient='records'))
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

# 특정 Sender 주소의 거래내역 조회 API
@app.get("/transactions/sender/{sender_address}")
async def get_transactions_by_sender(sender_address: str):
    try:
        df = pd.read_csv("./data/transfers_test.csv")
        df_filtered = df[df["Sender"] == sender_address]

        df_filtered = df_filtered[["Sender", "Receiver", "Token", "Amount", "Timestamp", "Network"]]
        df_filtered.columns = ["sender", "receiver", "token", "amount", "timestamp", "network"]
        df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], unit='s').dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        return JSONResponse(content=df_filtered.to_dict(orient='records'))
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

