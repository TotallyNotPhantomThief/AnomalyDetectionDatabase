import random
import sys
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values

from db_config import get_db_config


def datas_of_database(num_of_records=10000, clear_existing=True):
    conn = psycopg2.connect(**get_db_config())
    cursor = conn.cursor()

    if clear_existing:
        
        cursor.execute(
            "TRUNCATE TABLE anomaly_detections, recorded_transactions_of_money RESTART IDENTITY;"
        )
        print("Cleared recorded_transactions_of_money and anomaly_detections.")

    locations = ['New York','İstanbul','London','Paris','Pensilvania','St.Petersburg','Berlin','Osaka','Miami','Rome','Madrid','Chicago','Baghdad','Moscow','New Mexico', 'Kocaeli','Bursa','Ankara','İzmir']
    catagories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Sports & Outdoors', 'Books', 'Toys & Games', 'Health & Personal Care', 'Beauty', 'Automotive', 'Grocery','Jewelry','Taxes','Insurance','Travel']
    records = []
    base_time = datetime.now() - timedelta(days=180)
    for i in range(num_of_records):
        users_id = random.randint(1000,9999)
        location = random.choice(locations)
        category_of_expense = random.choice(catagories)
        time_of_action = base_time + timedelta(minutes=random.randint(0, 180*24*60))
        is_an_anomaly = 1 if random.random()<0.032 else 0
        if is_an_anomaly:
            amount_of_expense = round(random.uniform(5000, 9999),5)
        else:
            amount_of_expense = round(random.uniform(1, 4999),5)
        records.append((users_id,amount_of_expense,location,category_of_expense,time_of_action,is_an_anomaly))

    insert_query = """
    INSERT INTO recorded_transactions_of_money 
    (users_id, transfered_amount, location_of_transfer, category_of_spent, transfer_time, flagged_as_anomaly)
    VALUES %s;
    """

    execute_values(cursor, insert_query, records, page_size=1000)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted {num_of_records} records.")


if __name__ == "__main__":
    
    datas_of_database(clear_existing="--keep" not in sys.argv)