import re

def generate_sql_equivalent_query(query_parts: dict, select_cols: list = None) -> str:
    """
    Generates a standard SQL query string from a structured SimpleCQ query dictionary.
    Handles column name sanitization and proper SQL syntax for advanced features.
    """
    if not query_parts.get("join_order"):
        raise ValueError("Query must specify at least one table in 'join_order'.")

    # SELECT clause
    select_items = []
    if query_parts.get("select_aggs"):
        for func, t, c, alias in query_parts["select_aggs"]:
            arg = f"{t}.{c}" if t and c != "*" else (c if c != "*" else "*")
            agg_str = f"{func}({arg})"
            if alias:
                agg_str += f" AS {alias}"
            select_items.append(agg_str)
    if select_cols:
        for t, c, alias in select_cols:
            col = f"{t}.{c}" if t else c
            if alias:
                col += f" AS {alias}"
            select_items.append(col)
    if not select_items:
        select_items = ["*"]
    select_str = ", ".join(select_items)
    sql = f"SELECT {'DISTINCT ' if query_parts.get('distinct') else ''}{select_str}"

    # FROM clause
    from_table = query_parts['join_order'][0]
    sql += f" FROM {from_table}"

    # JOIN clauses
    if len(query_parts['join_order']) > 1 and query_parts.get("join_conditions"):
        processed_joins = set()
        for t1, c1, t2, c2 in query_parts["join_conditions"]:
            join_key = tuple(sorted([t1, t2]))
            if join_key not in processed_joins:
                c1_sanitized = c1.strip('"\'').replace(' ', '_')
                c2_sanitized = c2.strip('"\'').replace(' ', '_')
                sql += f" JOIN {t2} ON {t1}.{c1_sanitized} = {t2}.{c2_sanitized}"
                processed_joins.add(join_key)

    # WHERE clause
    if query_parts.get("compare_conditions"):
        where_clauses = []
        for t, c, op, val, logic in query_parts["compare_conditions"]:
            c_sanitized = c.strip('"\'').replace(' ', '_')
            if op.upper() == "IS NULL":
                clause = f"{t}.{c_sanitized} IS NULL"
            elif op.upper() == "LIKE":
                clause = f"{t}.{c_sanitized} LIKE '{val}'"
            elif op.upper() in ("IN", "NOT IN"):
                val_str = "(" + ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in val]) + ")"
                clause = f"{t}.{c_sanitized} {op.upper()} {val_str}"
            else:
                val_str = f"'{val}'" if isinstance(val, str) and not val.isdigit() else str(val)
                clause = f"{t}.{c_sanitized} {op} {val_str}"
            where_clauses.append((clause, logic))
        if where_clauses:
            expr = f"({where_clauses[0][0]})"
            for i in range(1, len(where_clauses)):
                logic = where_clauses[i-1][1] or "AND"
                expr = f"({expr}) {logic} ({where_clauses[i][0]})"
            sql += f" WHERE {expr}"

    # GROUP BY
    if query_parts.get("group_by"):
        gb_cols = []
        for t, c in query_parts["group_by"]:
            gb_cols.append(f"{t}.{c}" if t else c)
        sql += " GROUP BY " + ", ".join(gb_cols)

    # HAVING
    if query_parts.get("having_conditions"):
        having_clauses = []
        for func, t, c, op, val, logic in query_parts["having_conditions"]:
            if func == "VALUE":
                col_name = f"{t}.{c}" if t else c
                clause = f"{col_name} {op} {val}"
            else:
                arg = f"{t}.{c}" if t and c != "*" else (c if c != "*" else "*")
                clause = f"{func}({arg}) {op} {val}"
            having_clauses.append((clause, logic))
        expr = having_clauses[0][0]
        for (clause, logic) in having_clauses[1:]:
            expr = f"({expr}) {logic} ({clause})"
        sql += f" HAVING {expr}"

    # ORDER BY
    if query_parts.get("order_by"):
        ob_items = []
        for t, c, asc in query_parts["order_by"]:
            ob_items.append(f"{t}.{c} {'ASC' if asc else 'DESC'}" if t else f"{c} {'ASC' if asc else 'DESC'}")
        sql += " ORDER BY " + ", ".join(ob_items)

    # LIMIT/OFFSET
    if query_parts.get("limit") is not None:
        sql += f" LIMIT {query_parts['limit']}"
    if query_parts.get("offset") is not None:
        sql += f" OFFSET {query_parts['offset']}"

    print(f"Debug: Generated SQL query: {sql}")
    return sql.strip()