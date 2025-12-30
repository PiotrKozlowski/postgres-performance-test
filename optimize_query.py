import psycopg2
import json
import time

conn = psycopg2.connect(
    dbname="comment_db", user="test_user", password="test_password", host="localhost"
)
conn.autocommit = True
cur = conn.cursor()

def run_test():
    # 1. Create B-Tree index on 'org'
    print("Tworzenie indeksu B-Tree na polu 'org'...")
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_comments_org ON cell_comments ((coordinates ->> 'org'))")
        print("Indeks utworzony.")
    except Exception as e:
        print(f"Błąd tworzenia indeksu: {e}")

    # 2. Fetch target
    cur.execute("SELECT coordinates FROM cell_comments LIMIT 1")
    row = cur.fetchone()
    if not row: return
    
    target_json = json.dumps(row[0])
    target_dict = json.loads(target_json)
    org_val = target_dict.get("org")

    print(f"\nTarget Org: {org_val}")

    # 3. Benchmark Original Slow Query
    print("\n--- 1. Oryginalne zapytanie (<@) ---")
    sql_slow = f"SELECT count(*) FROM cell_comments WHERE coordinates <@ '{target_json}'"
    
    start = time.perf_counter()
    cur.execute(sql_slow)
    res = cur.fetchone()[0]
    dur = (time.perf_counter() - start) * 1000
    print(f"Wynik: {res}, Czas: {dur:.2f} ms")

    # 4. Benchmark Optimized Query
    print("\n--- 2. Zoptymalizowane zapytanie (Index + <@) ---")
    # We add an explicit check on 'org' to force usage of the B-Tree index
    sql_fast = f"SELECT count(*) FROM cell_comments WHERE (coordinates ->> 'org') = '{org_val}' AND coordinates <@ '{target_json}'"
    
    start = time.perf_counter()
    cur.execute(sql_fast)
    res = cur.fetchone()[0]
    dur = (time.perf_counter() - start) * 1000
    print(f"Wynik: {res}, Czas: {dur:.2f} ms")

    # 5. Explain Analyze for Optimized Query
    print("\n--- PLAN ZAPYTANIA (Zoptymalizowane) ---")
    cur.execute(f"EXPLAIN ANALYZE {sql_fast}")
    for line in cur.fetchall():
        print(line[0])

try:
    run_test()
finally:
    cur.close()
    conn.close()