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
    print("Pobieranie losowego wiersza do testów...")
    # Pobieramy losowy wiersz, aby mieć pewność, że dane istnieją
    # ORDER BY random() jest wolne dla dużych tabel, ale akceptowalne dla jednorazowego pobrania w teście
    cur.execute("SELECT coordinates FROM cell_comments ORDER BY random() LIMIT 1")
    row = cur.fetchone()
    
    if not row:
        print("Brak danych w tabeli cell_comments. Uruchom najpierw add_data.py.")
        return

    target_coords = row[0]
    
    # Obsługa formatu danych (czy psycopg2 zwrócił dict czy string)
    if isinstance(target_coords, dict):
        target_dict = target_coords
        target_json = json.dumps(target_coords)
    else:
        # Jeśli zwrócił string (np. dla kolumny typu TEXT lub JSON bez autokonwersji)
        target_json = target_coords
        target_dict = json.loads(target_coords)

    print(f"Cel testu (target): {target_json[:100]}... (długość: {len(target_json)})")

    # Przygotowanie fragmentu do zapytania "podrzędnego" (np. tylko org)
    # Używamy klucza 'org', który jest generowany w add_data.py
    org_val = target_dict.get("org")
    if org_val:
        partial_json = json.dumps({"org": org_val})
    else:
        # Fallback na pierwszy dostępny klucz
        k = list(target_dict.keys())[0]
        partial_json = json.dumps({k: target_dict[k]})

    queries = {
        "Dokładne dopasowanie (=)":
            f"SELECT count(*) FROM cell_comments WHERE coordinates @> '{target_json}' AND coordinates <@ '{target_json}'",

        "Dopasowanie nadrzędne (Komentarze 'nad' komórką - operator <@)":
            f"SELECT count(*) FROM cell_comments WHERE coordinates <@ '{target_json}'",

        "Dopasowanie podrzędne (Komentarze 'pod' komórką - operator @>)":
            f"SELECT count(*) FROM cell_comments WHERE coordinates @> '{partial_json}'"
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