import streamlit as st
import pandas as pd
import os
import ast
from core_engine.simple_cqc import SimpleCQC

st.set_page_config(page_title="CQC-Accelerator", layout="wide")
st.title("🚀 CQC-Accelerator")

uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])
tables = {}

if uploaded_files:
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        table_name = os.path.splitext(uploaded_file.name)[0]
        tables[table_name] = df

    st.success("Tables loaded: " + ", ".join(tables.keys()))
    prepared_tables = SimpleCQC.prepare_tables(tables)
    engine = SimpleCQC(prepared_tables)

    st.header("🧩 Define Query")
    table_names = list(tables.keys())

    join_order = st.multiselect("Join Order", options=table_names, default=table_names)
    join_conditions = []

    st.subheader("🔗 Join Conditions")
    for i in range(len(join_order) - 1):
        t1 = join_order[i]
        t2 = join_order[i + 1]
        c1 = st.selectbox(f"{t1} column", tables[t1].columns, key=f"{t1}_{i}")
        c2 = st.selectbox(f"{t2} column", tables[t2].columns, key=f"{t2}_{i}")
        join_conditions.append((t1, c1, t2, c2))

    st.subheader("⚖️ Compare Conditions")

    # Initialize session state for compare_conditions list
    if "compare_conditions" not in st.session_state:
        st.session_state.compare_conditions = []

    if st.button("Add Comparison Condition"):
        st.session_state.compare_conditions.append({
            "table": table_names[0] if table_names else None,
            "column": tables[table_names[0]].columns[0] if table_names else None,
            "operator": "=",
            "value": ""
        })

    remove_indices = []
    for i, cond in enumerate(st.session_state.compare_conditions):
        st.markdown(f"### Condition #{i+1}")
        table = st.selectbox(f"Table {i+1}", table_names, index=table_names.index(cond["table"]) if cond["table"] in table_names else 0, key=f"table_{i}")
        columns = tables[table].columns if table else []
        column = st.selectbox(f"Column {i+1}", columns, index=columns.get_loc(cond["column"]) if cond["column"] in columns else 0 if columns else 0, key=f"col_{i}")
        operator = st.selectbox(f"Operator {i+1}", ["=", "!=", "<", "<=", ">", ">=", "IN", "NOT IN", "LIKE", "IS NULL"], index=["=", "!=", "<", "<=", ">", ">=", "IN", "NOT IN", "LIKE", "IS NULL"].index(cond["operator"]) if cond["operator"] else 0, key=f"op_{i}")

        val = None
        if operator != "IS NULL":
            val_input = st.text_input(f"Value {i+1}", value=cond["value"], key=f"val_{i}")
            val = val_input

        # Update the condition in session state
        st.session_state.compare_conditions[i] = {
            "table": table,
            "column": column,
            "operator": operator,
            "value": val if val is not None else ""
        }

        if st.button(f"Remove Condition {i+1}"):
            remove_indices.append(i)

    # Remove conditions after the loop to avoid index shifting issues
    for idx in sorted(remove_indices, reverse=True):
        st.session_state.compare_conditions.pop(idx)
        st.experimental_rerun()

    # Convert session_state conditions to the engine format
    compare_conditions = []
    for cond in st.session_state.compare_conditions:
        val_raw = cond["value"]
        op = cond["operator"]

        try:
            val = ast.literal_eval(val_raw) if val_raw else None
        except:
            val = val_raw

        if op == "IS NULL":
            compare_conditions.append((cond["table"], cond["column"], op, None, "AND"))
        else:
            if op in ["IN", "NOT IN"] and isinstance(val, str):
                val = [v.strip() for v in val.split(",")]
            compare_conditions.append((cond["table"], cond["column"], op, val, "AND"))

    if st.button("Run Query"):
        try:
            result = engine.run_query(join_order, join_conditions, compare_conditions)
            st.dataframe(result)
        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Upload at least one CSV file to begin.")

st.sidebar.markdown("**Tip:** Uploaded data is not saved after session ends.")
