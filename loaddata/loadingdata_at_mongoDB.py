import pandas as pd
from pymongo import MongoClient

# 1) CSV 읽기
total_stats    = pd.read_csv('data/total_stats.csv', index_col=0)
transfers_test = pd.read_csv('data/transfers_test.csv')

# 1-1) txhash 기준으로 amount만 합치고, 나머지는 첫 번째 값 사용
agg_dict = {col: 'first' for col in transfers_test.columns if col != 'amount' and col != 'txhash'}
agg_dict['amount'] = 'sum'

transfers_test = transfers_test.groupby('txhash', as_index=False).agg(agg_dict)

# 2) MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client['2ec-database']

# 3) 컬렉션 선택
col_deriv = db['derivative_stats']
col_tx    = db['transfer_data']

# 기존 문서 삭제
col_deriv.delete_many({})
col_tx.delete_many({})

# 4) DataFrame → 리스트 of dict
def df_to_docs(df, pk):
    df = df.reset_index() if df.index.name else df
    docs = df.to_dict('records')
    for d in docs:
        d['_id'] = d.pop(pk)
        for k, v in list(d.items()):
            if pd.isna(v):
                d[k] = None
    return docs

docs_deriv = df_to_docs(total_stats,    pk='address')
docs_tx    = df_to_docs(transfers_test, pk='txhash')

# 5) insert_many
col_deriv.insert_many(docs_deriv)
col_tx.insert_many(docs_tx)

print("Inserted",
      col_deriv.count_documents({}), "into derivative_stats;",
      col_tx.count_documents({}),    "into transfer_data")
