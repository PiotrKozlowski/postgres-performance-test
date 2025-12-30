import psycopg2

conn = psycopg2.connect(
    dbname="comment_db", user="test_user", password="test_password", host="localhost"
)
cur = conn.cursor()

cur.execute("""
    SELECT indexname, indexdef 
    FROM pg_indexes 
    WHERE tablename = 'cell_comments';
""")

indexes = cur.fetchall()
if indexes:
    print("Indexes found:")
    for name, definition in indexes:
        print(f"- {name}: {definition}")
else:
    print("No indexes found on table cell_comments.")

cur.close()
conn.close()