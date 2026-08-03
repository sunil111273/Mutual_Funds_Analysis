import pandas as pd

tx = pd.read_csv("data/processed/08_investor_transactions_clean.csv")
print(tx.columns.tolist())