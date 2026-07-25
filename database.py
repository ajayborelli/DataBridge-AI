import sqlite3
import os
import random
from datetime import datetime, timedelta

DATABASE_PATH = "data/business.db"

def create_database():
    # Create data folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT NOT NULL,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            region TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            revenue REAL NOT NULL
        )
    """)

    # Avoid inserting duplicate sample data
    cursor.execute("SELECT COUNT(*) FROM sales")
    record_count = cursor.fetchone()[0]

    if record_count > 0:
        print(f"Database already contains {record_count} records.")
        conn.close()
        return

    products = [
        ("Laptop", "Electronics", 65000),
        ("Smartphone", "Electronics", 35000),
        ("Headphones", "Electronics", 5000),
        ("Monitor", "Electronics", 22000),
        ("Office Chair", "Furniture", 12000),
        ("Desk", "Furniture", 18000),
        ("Keyboard", "Accessories", 2500),
        ("Mouse", "Accessories", 1500)
    ]

    regions = ["North", "South", "East", "West"]

    start_date = datetime(2025, 1, 1)

    # Generate 500 realistic sample transactions
    for _ in range(10000):
        product, category, unit_price = random.choice(products)
        region = random.choice(regions)
        quantity = random.randint(1, 10)

        order_date = start_date + timedelta(
            days=random.randint(0, 364)
        )

        revenue = quantity * unit_price

        cursor.execute("""
            INSERT INTO sales (
                order_date,
                product,
                category,
                region,
                quantity,
                unit_price,
                revenue
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order_date.strftime("%Y-%m-%d"),
            product,
            category,
            region,
            quantity,
            unit_price,
            revenue
        ))

    conn.commit()
    conn.close()

    print("Business database created successfully!")
    print("10000 sales records inserted.")

if __name__ == "__main__":
    create_database()