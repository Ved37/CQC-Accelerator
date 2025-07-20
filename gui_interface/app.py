import streamlit as st
import pandas as pd
from core_engine.simple_cqc import SimpleCQ
from core_engine.parser import parse_query_from_string
from benchmarking_suite.benchmark_cqc import benchmark_cq
from benchmarking_suite.benchmark_sql import benchmark_sql
from benchmarking_suite.helpers import generate_sql_equivalent_query
from benchmarking_suite.visualize import plot_benchmark_results
import os
import re

st.set_page_config(layout="wide")
st.title("📊 SimpleCQ Explorer")
st.caption("Interactive Conjunctive Query Benchmarking")

# --- Sidebar for File Upload and Benchmarking ---
with st.sidebar:
    st.header("Setup")
    uploaded_files = st.file_uploader(
        "Upload your CSV datasets here",
        type=["csv"],
        accept_multiple_files=True
    )
    st.header("Benchmarking")
    run_benchmark_option = st.checkbox("Compare SimpleCQ vs. SQLite Performance")
    st.info("If checked, a performance benchmark will run for the query and a comparison chart will be displayed.")

# --- Main Application Logic ---
if not uploaded_files:
    st.info("Upload one or more CSV files using the sidebar to begin.")
    st.stop()

# Load and validate tables
tables = {}
table_info = {}

for uploaded_file in uploaded_files:
    try:
        df = pd.read_csv(uploaded_file)
        table_name = uploaded_file.name.split(".")[0].lower()
        tables[table_name] = df
        table_info[table_name] = {
            'rows': len(df),
            'columns': list(df.columns),
            'file_name': uploaded_file.name
        }
        st.success(f"✅ Loaded {table_name}: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        st.error(f"❌ Failed to load {uploaded_file.name}: {e}")
        st.stop()

# Display table information
st.header("📋 Loaded Tables")
for table_name, info in table_info.items():
    with st.expander(f"Table: {table_name} ({info['rows']} rows)"):
        st.write("**Columns:**", ", ".join(info['columns']))
        st.dataframe(tables[table_name].head(3))

st.markdown("---")

# Dynamic query suggestions based on loaded tables
st.header("🔍 Query Interface")

# Generate sample queries based on available tables
sample_queries = []
if 'products' in tables:
    sample_queries.append("""SELECT DISTINCT products.Name, products.Price
FROM products
WHERE products.Price > 500
ORDER BY products.Price DESC
LIMIT 10""")

if 'customers' in tables and 'products' in tables:
    sample_queries.append("""SELECT customers.First_Name, products.Name, COUNT(products.Name) AS ProductCount
FROM customers
JOIN products ON customers.Customer_Id = products.Customer_Id
WHERE products.Price > 300
GROUP BY customers.First_Name, products.Name
ORDER BY ProductCount DESC""")

if 'transactions' in tables and 'products' in tables:
    sample_queries.append("""SELECT products.Name, AVG(transactions.Quantity) AS AvgQ
FROM products
JOIN transactions ON products.Internal_ID = transactions.Product_Id
WHERE transactions.Quantity > 2
GROUP BY products.Name
HAVING AvgQ > 10""")

# Query selection
query_option = st.selectbox("Choose a query template or write custom:", 
                           ["Custom Query"] + [f"Sample {i+1}" for i in range(len(sample_queries))])

if query_option == "Custom Query":
    default_query = "SELECT * FROM " + list(tables.keys())[0]
else:
    query_idx = int(query_option.split()[-1]) - 1
    default_query = sample_queries[query_idx]

query_input = st.text_area("Write your SQL-like conjunctive query here:", 
                          value=default_query, height=150)

if st.button("⚡ Run Query", type="primary"):
    if not query_input.strip():
        st.warning("Please enter a query.")
    else:
        try:
            # Parse the query
            with st.spinner("Parsing query..."):
                parsed_query = parse_query_from_string(query_input)
            
            # Debug information
            with st.expander("🔧 Debug Information"):
                st.write("**Parsed Query Structure:**")
                st.json(parsed_query)
                
                # Show table column mapping
                st.write("**Available Table Columns:**")
                for table_name, df in tables.items():
                    st.write(f"- **{table_name}:** {list(df.columns)}")

            # Validate that referenced tables exist
            missing_tables = []
            for table in parsed_query.get("join_order", []):
                if table not in tables:
                    missing_tables.append(table)
            
            if missing_tables:
                st.error(f"Referenced tables not found: {', '.join(missing_tables)}")
                st.info(f"Available tables: {', '.join(tables.keys())}")
                st.stop()

            # Run the SimpleCQ Engine
            st.subheader("✅ SimpleCQ Query Result")
            with st.spinner("Executing SimpleCQ query..."):
                prepared_tables = SimpleCQ.prepare_tables(tables)
                engine = SimpleCQ(prepared_tables)
                result_df = engine.run_query(
                    parsed_query["join_order"],
                    parsed_query["join_conditions"],
                    parsed_query["compare_conditions"],
                    select_cols=parsed_query.get("select_cols"),
                    select_aggs=parsed_query.get("select_aggs"),
                    distinct=parsed_query.get("distinct", False),
                    order_by=parsed_query.get("order_by"),
                    limit=parsed_query.get("limit"),
                    offset=parsed_query.get("offset"),
                    group_by=parsed_query.get("group_by"),
                    having_conditions=parsed_query.get("having_conditions")
                )

            # Display results
            st.write(f"**Query returned {len(result_df)} rows**")
            if len(result_df) > 0:
                st.dataframe(result_df)
                
                # Download option
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
            else:
                st.info("Query returned no results.")

            # Run Benchmark if selected
            if run_benchmark_option:
                st.markdown("---")
                st.subheader("⏱️ Performance Benchmark Results")
                
                try:
                    with st.spinner("Running benchmarks..."):
                        # Generate SQL query
                        sql_query = generate_sql_equivalent_query(parsed_query, parsed_query.get("select_cols"))
                        st.write("**Generated SQLite Query:**")
                        st.code(sql_query, language="sql")
                        
                        # Run benchmarks
                        cq_metrics = benchmark_cq(tables, parsed_query)
                        sql_metrics = benchmark_sql(tables, sql_query)
                        
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**SimpleCQ Results:**")
                        if cq_metrics.get("error"):
                            st.error(f"Error: {cq_metrics['error']}")
                        else:
                            st.metric("Execution Time", f"{cq_metrics['execution_time_seconds']:.4f}s")
                            st.metric("Memory Peak", f"{cq_metrics['memory_peak_bytes'] / 1024 / 1024:.2f} MB")
                    
                    with col2:
                        st.write("**SQLite Results:**")
                        if sql_metrics.get("error"):
                            st.error(f"Error: {sql_metrics['error']}")
                        else:
                            st.metric("Execution Time", f"{sql_metrics['execution_time_seconds']:.4f}s")
                            st.metric("Memory Peak", f"{sql_metrics['memory_peak_bytes'] / 1024 / 1024:.2f} MB")
                    
                    # Create comparison table
                    benchmark_df = pd.DataFrame([cq_metrics, sql_metrics])
                    benchmark_df = benchmark_df.set_index('query_expr')
                    
                    st.write("**Detailed Comparison:**")
                    st.dataframe(benchmark_df)
                    
                    # Plot results if no errors
                    if not cq_metrics.get("error") and not sql_metrics.get("error"):
                        st.write("**Performance Charts:**")
                        fig = plot_benchmark_results([cq_metrics, sql_metrics])
                        if fig:
                            st.pyplot(fig)
                
                except Exception as benchmark_error:
                    st.error(f"Benchmark error: {benchmark_error}")
                    with st.expander("🐛 Benchmark Error Details"):
                        import traceback
                        st.code(traceback.format_exc())

        except Exception as e:
            st.error(f"An error occurred: {e}")
            with st.expander("🐛 Error Details"):
                import traceback
                st.code(traceback.format_exc())

# Help section
with st.expander("❓ Help & Query Examples"):
    st.markdown("""
    ### Query Format
    Your queries should follow this pattern:
    ```sql
    SELECT [DISTINCT] col1, col2, COUNT(col3) AS cnt
    FROM table1
    JOIN table2 ON table1.key = table2.key
    WHERE table1.column > value AND table2.column < value2
    GROUP BY col1, col2
    HAVING cnt > 5
    ORDER BY col1 ASC, col2 DESC
    LIMIT 10 OFFSET 5
    ```
    ### Supported Operations
    - **Joins:** INNER JOIN with ON conditions
    - **Filters:** =, !=, <, <=, >, >=, LIKE, IS NULL, IN, NOT IN
    - **Logic:** AND/OR operations between WHERE/HAVING conditions
    - **Ordering:** ORDER BY multiple columns (ASC/DESC)
    - **Distinct:** SELECT DISTINCT
    - **Grouping:** GROUP BY columns and HAVING for aggregates
    - **Aggregates:** COUNT, SUM, AVG, MIN, MAX
    - **Limits:** LIMIT and OFFSET
    - **Aliases:** Limited support for table/column aliases
    - **Column names with spaces**
    """)