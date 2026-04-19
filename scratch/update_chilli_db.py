import sqlite3
import os

db_path = 'instance/site.db'
if not os.path.exists(db_path):
    db_path = 'instance/farmse.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("UPDATE crop SET image = 'green_chilli.png' WHERE name LIKE '%chilli%'")
    conn.commit()
    print(f"Updated {cursor.rowcount} rows.")
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
