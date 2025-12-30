import psycopg2
import json
import random
import time
import string
from psycopg2.extras import execute_values

# Konfiguracja połączenia
conn = psycopg2.connect(
    dbname="comment_db", user="test_user", password="test_password", host="localhost"
)
cur = conn.cursor()

def generate_random_string(min_len=5, max_len=1000):
    length = random.randint(min_len, max_len)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def seed_data(count=1_000_000):
    print(f"Generowanie {count} rekordów... to może chwilę potrwać.")
    
    # Generate random strings for orgs and prods to satisfy length requirements
    # while maintaining cardinality (100 orgs, 50 prods)
    orgs = [generate_random_string() for _ in range(100)]
    prods = [generate_random_string() for _ in range(50)]
    
    # Generate random strings for currencies as well
    currs = [generate_random_string() for _ in range(4)] + [None]

    batch_size = 10_000
    for i in range(0, count, batch_size):
        batch = []
        for _ in range(batch_size):
            # Losujemy różny stopień szczegółowości koordynatów
            coords = {
                "org": random.choice(orgs),
                "prod": random.choice(prods),
                "extra_field_1": generate_random_string(),
                "extra_field_2": generate_random_string(),
                "extra_field_3": generate_random_string(),
                "extra_field_4": generate_random_string(),
                "extra_field_5": generate_random_string(),
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