import random
from datetime import datetime, timedelta
import psycopg2


Database_Config = {
    "host": "localhost",
    "port": 5432,
    "database": "anomaly_database",
    "user": "postgres",
    "password": "mypassword"
}

def datas_of_database(num_of_records=1000):
    conn = psycopg2.connect(**Database_Config)
    cursor = conn.cursor()
    locations = ['New York','İstanbul','London','Paris','Pensilvania','St.Petersburg','Berlin','Osaka','Miami','Rome','Madrid','Chicago','Baghdad','Moscow','New Mexico', 'Kocaeli','Bursa','Ankara','İzmir']
    catagories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Sports & Outdoors', 'Books', 'Toys & Games', 'Health & Personal Care', 'Beauty', 'Automotive', 'Grocery','Jewelry','Taxes','Insurance','Travel']
    records = []
    base_time = datetime.now() - timedelta(days=180)
    for i in range(num_of_records):
        user_id = random.randint(1000,9999)
        location = random.choice(locations)
        category_of_expense = random.choice(catagories)
        time_of_action = base_time + timedelta(minutes=random.randint(0, 180*24*60))
        is_an_anomaly = 1 if random.random()<0.032 else 0
        if is_an_anomaly:
            amount_of_expense = round(random.uniform(5000, 9999),5)
        else:
            amount_of_expense = round(random.uniform(1, 4999),5)
        records.append((user_id,location,category_of_expense,time_of_action,is_an_anomaly,amount_of_expense))        

