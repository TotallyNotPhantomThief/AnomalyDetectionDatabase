import pandas as pd
import psycopg2
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score,recall_score,f1_score


db_config = {
    "host": "localhost",
    "port": 5432,
    "database": "anomaly_database",
    "user": "postgres",
    "password": "mypassword"
}

def run_detection_anomaly():
    conn = psycopg2.connect(db_config)

    print("Taking data from database.")
    query = "" "SELECT transaction_id, users_id, transfered_amout, flagged_as_anomaly FROM recorded_transactions_of_money;"""
    df = pd.read_sql(query,conn)

    x = df[["transfered_amount"]]

    model = IsolationForest( n_estimators=100, contamination=0.032,random_state=42)
    model.fit(x)


    raw_score  = model.decision_function(x)
    df["anomaly_probabilty_score"] = (
        raw_score.max() - raw_score) / (raw_score.max()- raw_score.min())


    predict = model.predict(x)
    df["is_a_anomaly"] = predict == -1


    is_true = df["flagged_as_anomaly"]
    the_truth = df["is_a_anomaly"].astype(int)

    precision = precision_score(is_true,the_truth,zero_division=0)
    recall = recall_score(is_true,the_truth,zero_division=0)
    f1 = f1_score(is_true,the_truth,zero_division=0)

    print(f"Performance of the algorithm;  Presicion: {precision:.2f} ,  Recall: {recall:.2f}  ")
    cursor = conn.cursor()

    records_in_detection = [
    (int(row["transaction_id"]),
     int(row["anomaly_probability_score"]),
     int(row["is_a_anomaly"])
    ) for _ , row in df.iterrows()
    ]
    insert_metrics = """
    INSERT INTO learning_algorithm (algorithm_name, presicion_score, score_of_error)
    VALUES (%s, %s, %s);
    """
    error_score = 1.0 - f1
    cursor.execute(insert_metrics,("Isolation Forset", precision,error_score)
    )




    conn.commit()
    cursor.close()
    conn.close()





if __name__ == "__main__":
 run_detection_anomaly()
    



    
    


