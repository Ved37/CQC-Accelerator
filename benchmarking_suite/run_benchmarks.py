
import os
import sys
import pandas as pd

# Add project root to path to allow imports from other packages
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# These imports will now work correctly
from benchmarking_suite.benchmark_cqc import benchmark_cqc
from benchmarking_suite.benchmark_sql import benchmark_sql
from benchmarking_suite.helpers import generate_sql_equivalent_query
from benchmarking_suite.visualize import plot_benchmark_results

def load_tables_from_dir(data_directory: str) -> dict:
    """
    Helper function to load all CSV files from a directory.
    """
    tables = {}
    if not os.path.isdir(data_directory):
        print(f"Error: Data directory not found at '{data_directory}'")
        return None
        
    for filename in os.listdir(data_directory):
        if filename.endswith(".csv"):
            table_name = filename.split(".")[0].lower()
            file_path = os.path.join(data_directory, filename)
            tables[table_name] = pd.read_csv(file_path)
    return tables

def run_full_benchmark():
    """
    Defines test queries, runs CQC and SQL benchmarks, and plots the results.
    """
    # 1. Load Data
    # Assumes a 'data' folder in the project root
    data_dir = os.path.join(PROJECT_ROOT, "data")
    tables = load_tables_from_dir(data_dir)
    if not tables:
        print("Please create a 'data' directory in your project root and add your CSV files.")
        return
    print(f"Successfully loaded tables: {list(tables.keys())}")

    # 2. Define Test Queries
    test_queries = [
        {
            "name": "Find Canadian Customers & their Company Industry",
            "cqc_query": {
                "join_order": ["customers", "organizations"],
                "join_conditions": [("customers", "Company", "organizations", "Name")],
                "compare_conditions": [("customers", "Country", "=", "Canada", "AND")]
            },
            "select_cols": ["customers.Name", "organizations.Industry"]
        },
        {
            "name": "Find Large IT Companies & their Customers",
            "cqc_query": {
                "join_order": ["customers", "organizations"],
                "join_conditions": [("customers", "Company", "organizations", "Name")],
                "compare_conditions": [
                    ("organizations", "Industry", "=", "IT", "AND"),
                    ("organizations", "Number of employees", ">", 5000, "AND")
                ]
            },
            "select_cols": ["customers.First Name", "organizations.Name"]
        }
    ]

    all_results = []

    # 3. Run Benchmarks for each query
    for query_def in test_queries:
        print(f"\n--- Benchmarking Query: {query_def['name']} ---")
        
        sql_query = generate_sql_equivalent_query(query_def["cqc_query"], query_def["select_cols"])
        print(f"Generated SQL: {sql_query}")

        cqc_result = benchmark_cqc(tables, query_def["cqc_query"])
        all_results.append(cqc_result)
        print("CQC Results:", cqc_result)

        # Pass the generated SQL string to the corrected benchmark_sql function
        sql_result = benchmark_sql(tables, sql_query)
        all_results.append(sql_result)
        print("SQL Results:", sql_result)

    # 4. Visualize the results
    print("\n--- Plotting Benchmark Results ---")
    fig = plot_benchmark_results(all_results)
    import matplotlib.pyplot as plt
    plt.show()


if __name__ == "__main__":
    run_full_benchmark()