import time
import tracemalloc
from core_engine.simple_cqc import SimpleCQ

def benchmark_cq(tables: dict, query_parts: dict):
    """
    Benchmark SimpleCQ engine with proper error handling and memory management.
    """
    try:
        # Prepare tables with prefixed columns
        prepared_tables = SimpleCQ.prepare_tables(tables)
        engine = SimpleCQ(prepared_tables)
        
        # Start memory and time tracking
        tracemalloc.start()
        start_time = time.perf_counter()
        
        # Execute query
        df_result = engine.run_query(
            query_parts["join_order"],
            query_parts["join_conditions"],
            query_parts["compare_conditions"]
        )
        
        # Stop timing and memory tracking
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calculate metrics
        result_rows = df_result.shape[0] if df_result is not None else 0
        result_cols = df_result.shape[1] if df_result is not None else 0
        
        return {
            'query_expr': "SimpleCQ Query",
            'execution_time_seconds': end_time - start_time,
            'memory_peak_bytes': peak,
            'result_rows': result_rows,
            'result_columns': result_cols,
            'error': None
        }
        
    except Exception as e:
        # Ensure tracemalloc is stopped even on error
        try:
            tracemalloc.stop()
        except:
            pass
            
        print(f"Error during SimpleCQ query: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'query_expr': "SimpleCQ Query",
            'execution_time_seconds': 0,
            'memory_peak_bytes': 0,
            'result_rows': 0,
            'result_columns': 0,
            'error': str(e)
        }
