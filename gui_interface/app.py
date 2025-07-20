# gui_interface/app.py
# --- HEAVILY MODIFIED ---
# This version integrates the full benchmarking suite into the sidebar.

import streamlit as st
import pandas as pd
from core_engine.simple_cqc import SimpleCQC
from core_engine.parser import parse_query_from_string
from benchmarking_suite.benchmark_cqc import benchmark_cqc
from benchmarking_suite.benchmark_sql import benchmark_sql
from benchmarking_suite.helpers import generate_sql_equivalent_query
from benchmarking_suite.visualize import plot_benchmark_results

st.set_page_config(layout="wide")
st.title("📊 CQC-Accelerator")
st.caption("An Interactive Framework for Conjunctive Queries with Comparisons")

# --- Sidebar for File Upload and Benchmarking ---
with st.sidebar:
    st.header("Setup")
    uploaded_files = st.file_uploader(
        "Upload your CSV datasets here",
        type=["csv"],
        accept_multiple_files=True
    )
    st.header("Benchmarking")
    run_benchmark_option = st.checkbox("Compare CQC vs. SQL Performance")
    st.info("If checked, a performance benchmark will run for the query and a comparison chart will be displayed.")


# --- Main Application Logic ---
if not uploaded_files:
    st.info("Upload one or more CSV files using the sidebar to begin.")
else:
    tables = {}
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)
            table_name = uploaded_file.name.split(".")[0].lower()
            tables[table_name] = df
        except Exception as e:
            st.error(f"Failed to load {uploaded_file.name}: {e}")
    
    st.success(f"Loaded tables: {', '.join(tables.keys())}")
    st.markdown("---")

    # Query Input Area
    # --- FIX: Corrected the default query to use a column that exists ("First Name") ---
    default_query = """SELECT customers."First Name", organizations.Industry
FROM customers JOIN organizations ON customers.Company = organizations.Name
WHERE customers.Country = 'Canada'"""
    query_input = st.text_area("Write your CQC-style query here:", value=default_query, height=150)

    if st.button("⚡ Run Query"):
        if not query_input.strip():
            st.warning("Please enter a query.")
        else:
            try:
                # --- 1. Parse the CQC query ---
                parsed_query = parse_query_from_string(query_input)
                
                # --- 2. Run the CQC Engine to get the main result ---
                st.subheader("✅ CQC Query Result")
                prepared_tables = SimpleCQC.prepare_tables(tables)
                engine = SimpleCQC(prepared_tables)
                result_df = engine.run_query(
                    parsed_query["join_order"],
                    parsed_query["join_conditions"],
                    parsed_query["compare_conditions"]
                )
                
                # Select final columns if specified
                # In the "Run Query" block, update the column selection
                if parsed_query["select_cols"]:
                    final_cols = [f"{col.split('.')[0].lower()}_{col.split('.')[1].replace(' ', '_')}" for col in parsed_query["select_cols"]]
                    existing_cols = [c for c in final_cols if c in result_df.columns]
                    result_df = result_df[existing_cols]
                
                st.dataframe(result_df)

                # --- 3. Run Benchmark if the user selected the option ---
                if run_benchmark_option:
                    st.markdown("---")
                    st.subheader("⏱️ Performance Benchmark Results")
                    with st.spinner("Running CQC and SQL benchmarks..."):
                        # Generate the SQL equivalent for comparison
                        sql_query = generate_sql_equivalent_query(parsed_query, parsed_query["select_cols"])
                        st.code(f"Generated SQL for comparison:\n{sql_query}", language="sql")

                        # Run both benchmarks
                        cqc_metrics = benchmark_cqc(tables, parsed_query)
                        sql_metrics = benchmark_sql(tables, sql_query)
                        
                        # --- MODIFICATION: Display detailed metrics in a table ---
                        st.write("#### Benchmark Metrics")
                        benchmark_df = pd.DataFrame([cqc_metrics, sql_metrics])
                        benchmark_df = benchmark_df.set_index('query_expr')
                        st.dataframe(benchmark_df)
                        
                        # --- MODIFICATION: Plot the results ---
                        st.write("#### Performance Charts")
                        fig = plot_benchmark_results([cqc_metrics, sql_metrics])
                        st.pyplot(fig)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)