import psycopg2
from psycopg2.extras import execute_values
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

from preprocessing import preprocess, build_transformer
from db_config import get_db_config

TEST_SIZE = 0.2
RANDOM_STATE = 42
CONTAMINATION = 0.032


def run_detection_anomaly():
    conn = psycopg2.connect(**get_db_config())

    print("Taking data from database.")
    df = preprocess(conn)
    df["flagged_as_anomaly"] = df["flagged_as_anomaly"].astype(int)

    
    df_train, df_test = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["flagged_as_anomaly"],
    )
    print(f"Total: {len(df)} rows | Train: {len(df_train)} | Test: {len(df_test)}")

    
    transformer = build_transformer()
    x_train = transformer.fit_transform(df_train[["transfered_amount"]])
    x_test = transformer.transform(df_test[["transfered_amount"]])

    model = IsolationForest(
        n_estimators=100, contamination=CONTAMINATION, random_state=RANDOM_STATE
    )
    model.fit(x_train)

    
    y_true = df_test["flagged_as_anomaly"]
    y_pred = (model.predict(x_test) == -1).astype(int)

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    print(
        f"Test set performance; Precision: {precision:.2f}, "
        f"Recall: {recall:.2f}, F1: {f1:.2f}"
    )

    
    x_all = transformer.transform(df[["transfered_amount"]])
    raw_score = model.decision_function(x_all)
    df["anomaly_probability_score"] = (raw_score.max() - raw_score) / (
        raw_score.max() - raw_score.min()
    )
    df["is_a_anomaly"] = model.predict(x_all) == -1

    records_in_detection = [
        (
            int(row["transaction_id"]),
            float(row["anomaly_probability_score"]),
            bool(row["is_a_anomaly"]),
        )
        for _, row in df.iterrows()
    ]

    cursor = conn.cursor()

    insert_detection_query = """
    INSERT INTO anomaly_detections (transaction_id, anomaly_probability_score, is_a_anomaly)
    VALUES %s
    ON CONFLICT (transaction_id)
    DO UPDATE SET
        anomaly_probability_score = EXCLUDED.anomaly_probability_score,
        is_a_anomaly = EXCLUDED.is_a_anomaly;
    """
    execute_values(cursor, insert_detection_query, records_in_detection, page_size=1000)

    insert_metrics = """
    INSERT INTO learning_algorithm (algorithm_name, presicion_score, score_of_error, f1_score)
    VALUES (%s, %s, %s, %s);
    """
    error_score = 1.0 - f1
    cursor.execute(insert_metrics, ("Isolation Forest", precision, error_score, f1))

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    run_detection_anomaly()