import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler

QUERY = """
SELECT transaction_id, users_id, 
transfered_amount,flagged_as_anomaly FROM recorded_transactions_of_money;
 """
REQUIRED_COLUMNS = ["transaction_id", "transfered_amount"]
FEATURES = ["transfered_amount"]

def load_data(conn):
    return pd.read_sql(QUERY, conn)



def clean_data(df):
    df = df.copy()
    start = len(df)
    df["transfered_amount"] = pd.to_numeric(df["transfered_amount"], errors="coerce") 
    steps = {}
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    steps["missingvalues"] = before - len(df)
    before = len(df)
    df = df[df["transfered_amount"] > 0]
    steps["negativevalues"] = before - len(df)
    before = len(df)
    df = df.drop_duplicates(subset="transaction_id")
    steps["duplicates"] = before - len(df)

    for reason, count in steps.items():
        print(f"Removed {count} rows due to {reason}.")
    return df.reset_index(drop=True)

def build_transformer():
    return ColumnTransformer([("num",StandardScaler(),FEATURES)])
def preprocess(conn):
    df = load_data(conn)
    return clean_data(df)

    