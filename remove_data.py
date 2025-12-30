import psycopg2
import json
import random
import time
from psycopg2.extras import execute_values

# Konfiguracja połączenia
conn = psycopg2.connect(
    dbname="comment_db", user="test_user", password="test_password", host="localhost"
)
cur = conn.cursor()


try:
    cur.execute("TRUNCATE cell_comments")
    conn.commit()
    print("Table cell_comments truncated.")
finally:
    cur.close()
    conn.close()