import pandas as pd
import psycopg2
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score,recall_score,f1_score
from preprocessing import preprocess, build_transformer

db_config = {
    "host": "localhost",
    "port": 5433,
    "database": "anomaly_database",
    "user": "postgres",
    "password": "mypassword"
}

def run_detection_anomaly():
    conn = psycopg2.connect(**db_config)

    print("Taking data from database.")
    df = preprocess(conn)
    transformer = build_transformer()
    x = transformer.fit_transform(df[["transfered_amount"]])

    model = IsolationForest( n_estimators=100, contamination=0.032,random_state=42)
    model.fit(x)


    raw_score  = model.decision_function(x)
    df["anomaly_probability_score"] = (
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
     float(row["anomaly_probability_score"]),
     bool(row["is_a_anomaly"])
    ) for _ , row in df.iterrows()
    ]
    insert_detection_query = """
    INSERT INTO anomaly_detections (transaction_id, anomaly_probability_score, is_a_anomaly)
    VALUES (%s, %s, %s)
    ON CONFLICT (transaction_id) 
    DO UPDATE SET 
        anomaly_probability_score = EXCLUDED.anomaly_probability_score,
        is_a_anomaly = EXCLUDED.is_a_anomaly;
    """
    cursor.executemany(insert_detection_query, records_in_detection)
   
   
    insert_metrics = """
    INSERT INTO learning_algorithm (algorithm_name, presicion_score, score_of_error , f1_score)
    VALUES (%s, %s, %s, %s);
    """
    error_score = 1.0 - f1
    cursor.execute(insert_metrics, ("Isolation Forset", precision, error_score,f1))
    




    conn.commit()
    cursor.close()
    conn.close()





if __name__ == "__main__":
 run_detection_anomaly()
    



    
    


