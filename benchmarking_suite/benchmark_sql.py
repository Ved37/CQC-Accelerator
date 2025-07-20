import time
import tracemalloc
import sqlite3
import pandas as pd

def benchmark_sql(tables: dict, sql_query: str):
    """
    Benchmark SQLite with proper error handling and connection management.
    """
    conn = None
    try:
        # Create in-memory SQLite database
        conn = sqlite3.connect(":memory:")
        
        # Load tables into SQLite with sanitized column names
        for tname, df in tables.items():
            df_copy = df.copy()
            # Sanitize column names to match what SimpleCQ expects
            df_copy.columns = [col.replace(' ', '_') for col in df_copy.columns]
            df_copy.to_sql(tname, conn, index=False, if_exists='replace')
        
        # Start benchmarking
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Execute query
        df_result = pd.read_sql_query(sql_query, conn)
        
        # Stop benchmarking
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "query_expr": "SQLite Query",
            "execution_time_seconds": end_time - start_time,
            "memory_peak_bytes": peak,
            #"result_rows": len(df_result),
            "result_columns": len(df_result.columns),
            "error": None
        }
        
    except Exception as e:
        # Ensure cleanup on error
        try:
            tracemalloc.stop()
        except:
            pass
            
        print(f"Error executing SQLite query: {sql_query}")
        print(f"Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "query_expr": "SQLite Query",
            "execution_time_seconds": 0,
            "memory_peak_bytes": 0,
            #"result_rows": 0,
            "result_columns": 0,
            "error": str(e)
        }
    finally:
        if conn:
            conn.close()