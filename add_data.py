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

def seed_data(count=1_000_000):
    print(f"Generowanie {count} rekordów... to może chwilę potrwać.")
    orgs = [f"ORG_{i}" for i in range(1, 101)]  # 100 organizacji
    prods = [f"PROD_{i}" for i in range(1, 50)]   # 50 produktów
    currs = ["EUR", "USD", "PLN", "GBP", None]     # Waluty (z null dla agregacji)

    batch_size = 10_000
    for i in range(0, count, batch_size):
        batch = []
        for _ in range(batch_size):
            # Losujemy różny stopień szczegółowości koordynatów
            coords = {
                "org": random.choice(orgs),
                "prod": random.choice(prods)
            }
            c = random.choice(currs)
            if c: coords["currency"] = c

            batch.append((
                "sales_cube",
                json.dumps(coords),
                f"Komentarz testowy nr {random.randint(1, 1000000)}",
                random.choice(["INFO", "WARNING", "CRITICAL"])
            ))

        execute_values(cur,
            "INSERT INTO cell_comments (resource_type, coordinates, content, severity) VALUES %s",
            batch)
        if i % 100_000 == 0:
            print(f"Wstawiono {i} rekordów...")

    conn.commit()
    print("Zakończono seedowanie danych.")

try:
    seed_data(1_000_000) # Odkomentuj przy pierwszym uruchomieniu
finally:
    cur.close()
    conn.close()