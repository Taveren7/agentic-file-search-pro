import os
import time
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from fs_explorer.fs import parse_file, CACHE_DB_PATH

def test_performance():
    # Find some files to parse (e.g., in data or README.md)
    files = ["README.md", "ARCHITECTURE.md"]
    files = [f for f in files if os.path.exists(f)]
    
    if not files:
        print("No files found to test.")
        return

    print(f"Testing with files: {files}")
    
    # 1. First run (should be normal speed + DB init)
    start = time.time()
    for f in files:
        parse_file(f)
    first_duration = time.time() - start
    print(f"First run duration: {first_duration:.4f}s")
    
    # 2. Second run (should be near instant from in-memory cache)
    start = time.time()
    for f in files:
        parse_file(f)
    second_duration = time.time() - start
    print(f"Second run duration (in-memory): {second_duration:.4f}s")
    
    # 3. Third run (simulate restart, should be near instant from SQLite)
    import fs_explorer.fs
    fs_explorer.fs._DOCUMENT_CACHE.clear()
    
    start = time.time()
    for f in files:
        parse_file(f)
    third_duration = time.time() - start
    print(f"Third run duration (SQLite): {third_duration:.4f}s")
    
    assert second_duration < first_duration
    assert third_duration < first_duration
    print("\n✅ Performance gains verified!")

if __name__ == "__main__":
    if os.path.exists(CACHE_DB_PATH):
        os.remove(CACHE_DB_PATH)
    try:
        test_performance()
    finally:
        if os.path.exists(CACHE_DB_PATH):
             pass # Leave it for verification
