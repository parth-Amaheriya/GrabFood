
FOLDER_PATH = "files"
OUTPUT_FOLDER_PATH="output_files"
import mysql.connector
import json

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
}

DATABASE = 'grabfood_db'


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_database(cursor):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cursor.execute(f"USE {DATABASE}")


def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        restaurant_name TEXT,
        product_category TEXT,
        product_img TEXT,
        
        latitude DOUBLE,
        longitude DOUBLE,
        
        time_zone TEXT,
        currency TEXT,
        delivery_time INT,
        rating DOUBLE,
        
        deliverable_distance DOUBLE,
        
        availability JSON,
        menu JSON
    )
    """)


def insert_data(cursor, grab_food):
    # ✅ skip invalid parse
    if grab_food is None:
        return

    query = """
    INSERT INTO restaurant_data (
        restaurant_name,
        product_category,
        product_img,
        latitude,
        longitude,
        time_zone,
        currency,
        delivery_time,
        rating,
        deliverable_distance,
        availability,
        menu
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        grab_food.restaurant_name,
        grab_food.product_category,
        grab_food.img,
        grab_food.location.latitude,
        grab_food.location.longitude,
        grab_food.timeZone,
        grab_food.currency,
        int(grab_food.delivery_time),
        grab_food.rating,
        grab_food.deliverable_distance,
        json.dumps([a.model_dump() for a in grab_food.availability]),  # ✅ FIX
        json.dumps([m.model_dump() for m in grab_food.menu])           # ✅ FIX
    ))