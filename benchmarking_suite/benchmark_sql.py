import time
import tracemalloc
import sqlite3
import pandas as pd

def benchmark_sql(tables: dict, sql_query: str):
    conn = sqlite3.connect(":memory:")

    try:
        # Load tables into SQLite, sanitizing column names
        for tname, df in tables.items():
            df_copy = df.copy()
            # Replace spaces with underscores for SQL compatibility
            df_copy.columns = [col.replace(' ', '_') for col in df_copy.columns]
            df_copy.to_sql(tname, conn, index=False, if_exists='replace')

        # The helper now generates a sanitized query, so we can use it directly.
        # The previous error was caused by replacing spaces in the whole string.
        # sql_query_sanitized = sql_query.replace(' ', '_') <-- This was the bug.

        start_time = time.perf_counter()
        tracemalloc.start()

        df_result = pd.read_sql_query(sql_query, conn)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        end_time = time.perf_counter()

        return {
            "query_expr": "SQL Query",
            "execution_time_seconds": end_time - start_time,
            "memory_peak_bytes": peak,
            "result_rows": len(df_result),
            "result_columns": len(df_result.columns),
            "error": None
        }
    except Exception as e:
        # Provide more context on error
        print(f"Error executing SQL query: {sql_query}")
        raise e
    finally:
        conn.close()