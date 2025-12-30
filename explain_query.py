import psycopg2
import json

conn = psycopg2.connect(
    dbname="comment_db", user="test_user", password="test_password", host="localhost"
)
cur = conn.cursor()

# Pobieramy przykładowy wiersz jako cel
cur.execute("SELECT coordinates FROM cell_comments LIMIT 1")
row = cur.fetchone()
if row:
    target_json = json.dumps(row[0])
    
    # 1. Analiza wolnego zapytania (<@)
    print("--- PLAN ZAPYTANIA DLA <@ (Contained By) ---")
    query_slow = f"EXPLAIN ANALYZE SELECT count(*) FROM cell_comments WHERE coordinates <@ '{target_json}'"
    cur.execute(query_slow)
    for line in cur.fetchall():
        print(line[0])

    # 2. Analiza szybkiego zapytania (@>)
    print("\n--- PLAN ZAPYTANIA DLA @> (Contains) ---")
    # Tworzymy podzbiór dla zapytania @>
    target_dict = json.loads(target_json)
    # Bierzemy tylko klucz 'org'
    partial_json = json.dumps({"org": target_dict.get("org")})
    
    query_fast = f"EXPLAIN ANALYZE SELECT count(*) FROM cell_comments WHERE coordinates @> '{partial_json}'"
    cur.execute(query_fast)
    for line in cur.fetchall():
        print(line[0])

cur.close()
conn.close()