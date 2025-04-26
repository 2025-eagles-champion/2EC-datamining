import pandas as pd
import numpy as np
import json
import os

# 입력 설정
INPUT_TYPE = 'json'  # 'csv' 또는 'json'
INPUT_FILE_PATH = '../data/a.json'
OUTPUT_JSON_PATH = '../data/output.json'

# 입력 읽기
if INPUT_TYPE == 'csv':
    df = pd.read_csv(INPUT_FILE_PATH, encoding='utf-8', on_bad_lines='skip')
elif INPUT_TYPE == 'json':
    with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
else:
    raise ValueError('INPUT_TYPE은 csv 또는 json 중 하나여야 합니다.')

# IBCReceive 제거
df = df[df['type'] != 'IBCReceive']

# 외부 체인 거래 여부
df['is_external'] = df['fromChain'] != df['toChain']

# 작업에 사용할 데이터프레임
node_df = df
external_df = node_df[node_df['is_external']]

# 보낸 트랜잭션 집계
sent_stats = (
    node_df.groupby('fromAddress')
    .agg(sent_tx_count=('amount', 'count'), sent_tx_amount=('amount', 'sum'))
    .rename_axis('address')
)

# 받은 트랜잭션 집계
recv_stats = (
    node_df.groupby('toAddress')
    .agg(recv_tx_count=('amount', 'count'), recv_tx_amount=('amount', 'sum'))
    .rename_axis('address')
)

# 외부체인 보낸 트랜잭션 집계
external_sent_stats = (
    external_df.groupby('fromAddress')
    .agg(external_sent_tx_count=('amount', 'count'), external_sent_tx_amount=('amount', 'sum'))
    .rename_axis('address')
)

# 외부체인 받은 트랜잭션 집계
external_recv_stats = (
    external_df.groupby('toAddress')
    .agg(external_recv_tx_count=('amount', 'count'), external_recv_tx_amount=('amount', 'sum'))
    .rename_axis('address')
)

# 모든 통계 합치기
total_stats = (
    sent_stats
    .join(recv_stats, how='outer')
    .join(external_sent_stats, how='outer')
    .join(external_recv_stats, how='outer')
)

# 시간대별 Shannon entropy 계산
temp_df = node_df.copy()
temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
temp_df['hour'] = temp_df['timestamp'].dt.hour

sent = temp_df[['fromAddress', 'hour']].rename(columns={'fromAddress': 'address'})
hourly = (
    sent.groupby(['address', 'hour'])
    .size()
    .rename('hour_count')
    .reset_index()
)

def shannon_entropy(counts):
    p = counts / counts.sum()
    return -(p * np.log2(p)).sum()

ent = (
    hourly.groupby('address')['hour_count']
    .apply(shannon_entropy)
    .rename('hour_entropy')
    .reset_index()
)

total_stats = (
    total_stats.reset_index()
    .merge(ent, on='address', how='left')
    .fillna(0)
    .set_index('address')
)

# 활동 일수 기반 지표 추가
date_stats = (
    temp_df.groupby('fromAddress')['timestamp']
    .agg(first_date='min', last_date='max', active_days_count=lambda x: x.nunique())
    .rename_axis('address')
    .reset_index()
)

total_stats = (
    total_stats.reset_index()
    .merge(date_stats, on='address', how='left')
    .set_index('address')
)
total_stats['active_days_count'] = total_stats['active_days_count'].fillna(0)

# 거래 상대방 다양성 추가
cp_count_sent = (
    node_df.groupby('fromAddress')['toAddress']
    .nunique()
    .rename('counterparty_count_sent')
    .reset_index()
    .rename(columns={'fromAddress': 'address'})
)

cp_count_recv = (
    node_df.groupby('toAddress')['fromAddress']
    .nunique()
    .rename('counterparty_count_recv')
    .reset_index()
    .rename(columns={'toAddress': 'address'})
)

total_stats = (
    total_stats.reset_index()
    .merge(cp_count_sent, on='address', how='left')
    .merge(cp_count_recv, on='address', how='left')
    .set_index('address')
)

total_stats['counterparty_count_sent'] = total_stats['counterparty_count_sent'].fillna(0)
total_stats['counterparty_count_recv'] = total_stats['counterparty_count_recv'].fillna(0)

# 거래금액 특성 추가
total_stats['sent_tx_amount_mean'] = total_stats['sent_tx_amount'] / total_stats['sent_tx_count']
total_stats['recv_tx_amount_mean'] = total_stats['recv_tx_amount'] / total_stats['recv_tx_count']
total_stats['external_sent_tx_amount_mean'] = total_stats['external_sent_tx_amount'] / total_stats['external_sent_tx_count']
total_stats['external_recv_tx_amount_mean'] = total_stats['external_recv_tx_amount'] / total_stats['external_recv_tx_count']

if 'first_date' in total_stats.columns:
    total_stats['first_date'] = total_stats['first_date'].astype(str)
if 'last_date' in total_stats.columns:
    total_stats['last_date'] = total_stats['last_date'].astype(str)

# NaN 제거
total_stats.fillna(0, inplace=True)

# 결과를 JSON으로 저장
output_data = total_stats.reset_index().to_dict(orient='records')
os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✅ 변환 및 저장 완료: {OUTPUT_JSON_PATH}")