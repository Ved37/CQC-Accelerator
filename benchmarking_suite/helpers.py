
def generate_sql_equivalent_query(query_parts: dict, select_cols: list = None) -> str:
    """
    Generates a standard SQL query string from a structured CQC query dictionary.
    Sanitizes column names by replacing spaces with underscores.
    """
    if not query_parts.get("join_order"):
        raise ValueError("Query must specify at least one table in 'join_order'.")

    # SELECT clause
    if select_cols:
        select_items = []
        for col in select_cols:
            t_name, c_name = col.split('.')
            c_name_sanitized = c_name.replace(' ', '_')  # Replace spaces with underscores
            select_items.append(f"{t_name}.{c_name_sanitized}")
    else:
        select_items = ["*"]
    select_str = ", ".join(select_items)
    
    sql = f"SELECT {select_str} "

    # FROM and JOIN clauses
    from_table = query_parts['join_order'][0]
    from_str = f"FROM {from_table}"
    
    if len(query_parts['join_order']) > 1:
        join_clauses = []
        for t1, c1, t2, c2 in query_parts.get("join_conditions", []):
            c1_sanitized = c1.replace(' ', '_')
            c2_sanitized = c2.replace(' ', '_')
            join_clauses.append(f"JOIN {t2} ON {t1}.{c1_sanitized} = {t2}.{c2_sanitized}")
        from_str += " " + " ".join(join_clauses)
    
    sql += from_str

    # WHERE clause
    if query_parts.get("compare_conditions"):
        where_clauses = []
        for t, c, op, val, logic in query_parts["compare_conditions"]:
            c_sanitized = c.replace(' ', '_')
            val_str = f"'{val}'" if isinstance(val, str) else str(val)
            where_clauses.append(f"{t}.{c_sanitized} {op} {val_str}")
        
        where_str = " WHERE " + " AND ".join(where_clauses)
        sql += where_str

    return sql.strip()