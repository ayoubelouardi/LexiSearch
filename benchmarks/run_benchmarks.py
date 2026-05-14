import time
import sqlite3
from pathlib import Path
from rapidfuzz import process, fuzz

# Resolve path to the database
DB_PATH = Path(__file__).resolve().parent.parent / "src" / "lexisearch" / "data" / "dictionary.db"

def benchmark(name, func, iterations=100):
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    end = time.perf_counter()
    avg_ms = ((end - start) / iterations) * 1000
    return avg_ms

def main():
    print("🚀 Starting LexiSearch Benchmarks...\n")
    
    # 1. Indexing Benchmark
    def load_index():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT word FROM entries ORDER BY word")
        words = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return words
        
    print("Running Index Load Benchmark...")
    index_ms = benchmark("Load Index", load_index, iterations=10)
    words = load_index() # load once for the subsequent search tests
    print(f"Loaded {len(words)} unique words.\n")
    
    # 2. Short Query Benchmark
    short_q = "wo"
    def short_search():
        process.extract(short_q, words, scorer=fuzz.QRatio, limit=40, score_cutoff=30)
        
    print(f"Running Short Query Benchmark ('{short_q}')...")
    short_ms = benchmark("Short Search", short_search, iterations=50)

    # 3. Long Query Benchmark
    long_q = "dictionary"
    def long_search():
        process.extract(long_q, words, scorer=fuzz.WRatio, limit=40, score_cutoff=50)
        
    print(f"Running Long Query Benchmark ('{long_q}')...")
    long_ms = benchmark("Long Search", long_search, iterations=50)
    
    # 4. DB Retrieval Benchmark
    def fetch_def():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT word, wordtype, definition FROM entries WHERE word = ?", ("work",))
        cursor.fetchall()
        conn.close()
        
    print("Running Database Definition Fetch Benchmark...\n")
    db_ms = benchmark("Fetch Definition", fetch_def, iterations=100)
    
    # Print Markdown Summary
    print("### Benchmark Results\n")
    print("| Operation | Average Time (ms) | Iterations |")
    print("|---|---|---|")
    print(f"| Load 111k+ Index (SQLite) | {index_ms:.2f} ms | 10 |")
    print(f"| Short Query ('{short_q}', QRatio) | {short_ms:.2f} ms | 50 |")
    print(f"| Long Query ('{long_q}', WRatio) | {long_ms:.2f} ms | 50 |")
    print(f"| Fetch Definition (SQLite) | {db_ms:.2f} ms | 100 |")

if __name__ == "__main__":
    main()
