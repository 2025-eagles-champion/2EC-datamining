import pandas as pd
import tkinter as tk
from tkinter import filedialog

def convert_nodes(csv_path, js_path):
    df = pd.read_csv(csv_path)

    necessary_columns = [
        "address", "sent_tx_count", "sent_tx_amount",
        "recv_tx_count", "recv_tx_amount",
        "external_sent_tx_count", "external_sent_tx_amount",
        "external_recv_tx_count", "external_recv_tx_amount",
        "hour_entropy", "first_date", "last_date", "active_days_count",
        "counterparty_count_sent", "counterparty_count_recv",
        "sent_tx_amount_mean", "recv_tx_amount_mean",
        "external_sent_tx_amount_mean", "external_recv_tx_amount_mean"
    ]

    df = df[necessary_columns]
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('export const dummyNodes = [\n')
        for _, row in df.iterrows():
            f.write('  {\n')
            for col in necessary_columns:
                value = row[col]
                if isinstance(value, str):
                    f.write(f'    {col}: "{value}",\n')
                else:
                    f.write(f'    {col}: {value},\n')
            f.write('  },\n')
        f.write('];\n')

def convert_transactions(csv_path, js_path):
    df = pd.read_csv(csv_path)

    necessary_columns = [
        "type", "txhash", "timestamp", "amount",
        "denom", "dpDenom",
        "fromAddress", "toAddress",
        "fromChain", "fromChainId",
        "toChain", "toChainId"
    ]

    df = df[necessary_columns]

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('export const dummyTransactions = [\n')
        for _, row in df.iterrows():
            f.write('  {\n')
            for col in necessary_columns:
                value = row[col]
                if isinstance(value, str):
                    f.write(f'    {col}: "{value}",\n')
                else:
                    f.write(f'    {col}: {value},\n')
            f.write('  },\n')
        f.write('];\n')

def select_and_convert(mode):
    csv_path = filedialog.askopenfilename(
        title="CSV 파일을 선택하세요",
        filetypes=[("CSV files", "*.csv")]
    )
    if not csv_path:
        return

    js_path = filedialog.asksaveasfilename(
        title="저장할 JS 파일 이름을 지정하세요",
        defaultextension=".js",
        filetypes=[("JavaScript files", "*.js")]
    )
    if not js_path:
        return

    if mode == 'nodes':
        convert_nodes(csv_path, js_path)
    else:
        convert_transactions(csv_path, js_path)

    print(f"변환 완료! 저장 위치: {js_path}")

def main():
    root = tk.Tk()
    root.title("CSV to JS 변환기")

    tk.Label(root, text="변환할 타입을 선택하세요").pack(pady=10)

    tk.Button(root, text="노드 정보 변환(dummyNodes.js)", command=lambda: select_and_convert('nodes')).pack(pady=5)
    tk.Button(root, text="트랜잭션 정보 변환(dummyTransactions.js)", command=lambda: select_and_convert('transactions')).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
