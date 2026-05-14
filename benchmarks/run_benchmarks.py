import argparse
import time
import sqlite3
import re
from pathlib import Path
from rapidfuzz import process, fuzz

# Resolve paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "src" / "lexisearch" / "data" / "dictionary.db"
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"
RESULTS_DIR = ROOT_DIR / "benchmarks" / "results"

def get_version():
    """Extracts the version from pyproject.toml."""
    try:
        content = PYPROJECT_PATH.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "unknown"

def benchmark(name, func, iterations=100):
    start = time.perf_counter()
    for _ in range(iterations):
        func()
    end = time.perf_counter()
    avg_ms = ((end - start) / iterations) * 1000
    return avg_ms

def run_suite():
    """Runs one full pass of the benchmark suite."""
    results = {}
    
    # 1. Indexing Benchmark
    def load_index():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT word FROM entries ORDER BY word")
        words = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return words
        
    results["index_ms"] = benchmark("Load Index", load_index, iterations=10)
    words = load_index() # load once for the subsequent search tests
    
    # 2. Short Query Benchmark
    short_q = "wo"
    def short_search():
        process.extract(short_q, words, scorer=fuzz.QRatio, limit=40, score_cutoff=30)
        
    results["short_ms"] = benchmark("Short Search", short_search, iterations=50)

    # 3. Long Query Benchmark
    long_q = "dictionary"
    def long_search():
        process.extract(long_q, words, scorer=fuzz.WRatio, limit=40, score_cutoff=50)
        
    results["long_ms"] = benchmark("Long Search", long_search, iterations=50)
    
    # 4. DB Retrieval Benchmark
    def fetch_def():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT word, wordtype, definition FROM entries WHERE word = ?", ("work",))
        cursor.fetchall()
        conn.close()
        
    results["db_ms"] = benchmark("Fetch Definition", fetch_def, iterations=100)
    
    return results

def generate_report(results, version=None, num_runs=1):
    """Generates a markdown report from the results."""
    title = f"Benchmark Results: LexiSearch v{version}" if version else "Quick Benchmark Results"
    
    md_report = f"# {title}\n\n"
    md_report += f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_report += f"**Total Suite Runs:** {num_runs}\n\n"
    
    md_report += "### Average Latency Metrics\n\n"
    md_report += "| Operation | Average Time (ms) | Iterations per Run |\n"
    md_report += "|---|---|---|\n"
    md_report += f"| Load 111k+ Index (SQLite) | {results['index_ms']:.2f} ms | 10 |\n"
    md_report += f"| Short Query ('wo', QRatio) | {results['short_ms']:.2f} ms | 50 |\n"
    md_report += f"| Long Query ('dictionary', WRatio) | {results['long_ms']:.2f} ms | 50 |\n"
    md_report += f"| Fetch Definition (SQLite) | {results['db_ms']:.2f} ms | 100 |\n\n"
    
    md_report += "*(Lower is better.)*\n"
    return md_report

def main():
    parser = argparse.ArgumentParser(description="Run LexiSearch benchmarks.")
    parser.add_argument("--version", action="store_true", help="Run a full versioned benchmark (3 runs, saves report).")
    args = parser.parse_args()

    if args.version:
        version = get_version()
        print(f"🚀 Starting Versioned Multi-Run Benchmark for v{version}...\n")
        num_runs = 3
        all_runs = []
        for i in range(1, num_runs + 1):
            print(f"Executing suite run {i}/{num_runs}...")
            all_runs.append(run_suite())
        
        avg_results = {k: sum(r[k] for r in all_runs) / num_runs for k in all_runs[0]}
        md_report = generate_report(avg_results, version=version, num_runs=num_runs)
        
        # Save versioned MD file
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        report_file = RESULTS_DIR / f"v{version}.md"
        report_file.write_text(md_report, encoding="utf-8")
        print("\n" + md_report)
        print(f"\n✅ Versioned report saved to {report_file}")
    else:
        print("🚀 Starting Quick Benchmark (Single Run)...\n")
        results = run_suite()
        md_report = generate_report(results, num_runs=1)
        print("\n" + md_report)

if __name__ == "__main__":
    main()

