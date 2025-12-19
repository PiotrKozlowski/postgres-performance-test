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

def run_benchmark():
    # Definiujemy punkt wyszukiwania (Search Target)
    target_coords = {"org": "ORG_50", "prod": "PROD_25", "currency": "EUR"}
    target_json = json.dumps(target_coords)

    queries = {
        "Dokładne dopasowanie (=)":
            f"SELECT count(*) FROM cell_comments WHERE coordinates @> '{target_json}' AND coordinates <@ '{target_json}'",

        "Dopasowanie nadrzędne (Komentarze 'nad' komórką - operator <@)":
            f"SELECT count(*) FROM cell_comments WHERE coordinates <@ '{target_json}'",

        "Dopasowanie podrzędne (Komentarze 'pod' komórką - operator @>)":
            f"SELECT count(*) FROM cell_comments WHERE coordinates @> '{{\"org\": \"ORG_50\"}}'"
    }

    for desc, sql in queries.items():
        # Rozgrzewka (Warm-up)
        cur.execute(sql)

        start_time = time.perf_counter()
        cur.execute(sql)
        res = cur.fetchone()[0]
        end_time = time.perf_counter()

        print(f"\nTest: {desc}")
        print(f"Wyników: {res}")
        print(f"Czas wykonania: {(end_time - start_time) * 1000:.2f} ms")

try:
    run_benchmark()
finally:
    cur.close()
    conn.close()