CREATE TABLE IF NOT EXISTS recorded_transactions_of_money (
    transaction_id SERIAL PRIMARY KEY,
    users_id INT,
    transfered_amount NUMERIC(10, 5),
    location_of_transfer VARCHAR(100),
    category_of_spent VARCHAR(100),
    transfer_time TIMESTAMP,
    flagged_as_anomaly INT
);

CREATE TABLE IF NOT EXISTS anomaly_detections (
    detection_id SERIAL PRIMARY KEY,
    transaction_id INT UNIQUE REFERENCES recorded_transactions_of_money(transaction_id),
    anomaly_probability_score NUMERIC(10, 5),
    is_a_anomaly BOOLEAN
);

CREATE TABLE IF NOT EXISTS learning_algorithm (
    algorithm_id SERIAL PRIMARY KEY,
    algorithm_name VARCHAR(100),
    presicion_score NUMERIC(5, 4),
    score_of_error NUMERIC(5, 4),
    f1_score NUMERIC(5, 4),
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);