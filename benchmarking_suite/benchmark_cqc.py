import time
import tracemalloc
from core_engine.simple_cqc import SimpleCQC

def benchmark_cqc(tables: dict, query_parts: dict):
    # The CQC engine needs tables with prefixed columns
    prepared_tables = SimpleCQC.prepare_tables(tables)
    engine = SimpleCQC(prepared_tables)
    
    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        df_result = engine.run_query(
            query_parts["join_order"],
            query_parts["join_conditions"],
            query_parts["compare_conditions"]
        )
        error_msg = None
    except Exception as e:
        df_result = None
        error_msg = str(e)
        print(f"Error during CQC query: {e}")

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    result_rows = df_result.shape[0] if df_result is not None else 0
    result_cols = df_result.shape[1] if df_result is not None else 0

    return {
        'query_expr': "CQC Query",
        'execution_time_seconds': end_time - start_time,
        'memory_peak_bytes': peak,
        'result_rows': result_rows,
        'result_columns': result_cols,
        'error': error_msg
    }
