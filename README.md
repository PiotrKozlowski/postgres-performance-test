### How to run

1. Run docker `docker-compose up -d`
2. Connect to DB with `psql` and initialize it with **GIN INDEX**
```sql
CREATE TABLE cell_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_type TEXT NOT NULL,
    coordinates JSONB NOT NULL,
    content TEXT,
    severity TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indeks GIN dla wydajnego wyszukiwania wewnątrz JSONB
CREATE INDEX idx_comments_coords_gin ON cell_comments USING GIN (coordinates);
```
2.1. `winpty docker exec -it <docker_id> bash` on Windows
2.2. `psql -U test_user -d comment_db`
3. Install required deps `pip install psycopg2-binary`
4. Seed database with `python add_data.py`
5. Run benchmark with `python run_benchmark.py`
6. Remove database with `python remove_data.py`

### Results
$ python run_benchmark.py

Test: Dokładne dopasowanie (=)
Wyników: 47
Czas wykonania: 8.08 ms

Test: Dopasowanie nadrzędne (Komentarze 'nad' komórką - operator <@)
Wyników: 92
Czas wykonania: 47.46 ms

Test: Dopasowanie podrzędne (Komentarze 'pod' komórką - operator @>)
Wyników: 10025
Czas wykonania: 9.82 ms
