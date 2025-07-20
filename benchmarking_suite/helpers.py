import re

def generate_sql_equivalent_query(query_parts: dict, select_cols: list = None) -> str:
    """
    Generates a standard SQL query string from a structured SimpleCQ query dictionary.
    Handles column name sanitization and proper SQL syntax.
    """
    if not query_parts.get("join_order"):
        raise ValueError("Query must specify at least one table in 'join_order'.")

    # SELECT clause
    select_items = []
    if select_cols:
        for col in select_cols:
            # Handle both table.column and table."column name" formats
            if '.' in col:
                parts = col.split('.', 1)
                t_name = parts[0]
                c_name = parts[1].strip('"\'')
                c_name_sanitized = c_name.replace(' ', '_')
                select_items.append(f"{t_name}.{c_name_sanitized}")
            else:
                select_items.append(col)
    else:
        select_items = ["*"]
    
    if not select_items:
        raise ValueError("No valid columns specified in SELECT clause")
    
    select_str = ", ".join(select_items)
    sql = f"SELECT {select_str}"

    # FROM clause
    from_table = query_parts['join_order'][0]
    sql += f" FROM {from_table}"

    # JOIN clauses
    if len(query_parts['join_order']) > 1 and query_parts.get("join_conditions"):
        processed_joins = set()
        for t1, c1, t2, c2 in query_parts["join_conditions"]:
            join_key = tuple(sorted([t1, t2]))  # Avoid duplicate joins
            if join_key not in processed_joins:
                c1_sanitized = c1.strip('"\'').replace(' ', '_')
                c2_sanitized = c2.strip('"\'').replace(' ', '_')
                sql += f" JOIN {t2} ON {t1}.{c1_sanitized} = {t2}.{c2_sanitized}"
                processed_joins.add(join_key)

    # WHERE clause
    if query_parts.get("compare_conditions"):
        where_clauses = []
        for condition in query_parts["compare_conditions"]:
            if len(condition) >= 4:  # Handle both 4 and 5 element tuples
                t, c, op, val = condition[:4]
                c_sanitized = c.strip('"\'').replace(' ', '_')
                
                # Handle different operators and value types
                if op.upper() == "IS NULL":
                    where_clauses.append(f"{t}.{c_sanitized} IS NULL")
                elif op.upper() == "LIKE":
                    if not val.startswith("'") and not val.startswith('"'):
                        val = f"'{val}'"
                    where_clauses.append(f"{t}.{c_sanitized} LIKE {val}")
                elif op.upper() in ("IN", "NOT IN"):
                    if isinstance(val, (list, tuple)):
                        val_str = "(" + ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in val]) + ")"
                    else:
                        val_str = f"('{val}')" if isinstance(val, str) else f"({val})"
                    where_clauses.append(f"{t}.{c_sanitized} {op.upper()} {val_str}")
                else:
                    # Numeric and string comparisons
                    if isinstance(val, str) and not val.isdigit():
                        val_str = f"'{val}'"
                    else:
                        val_str = str(val)
                    where_clauses.append(f"{t}.{c_sanitized} {op} {val_str}")
        
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

    return sql.strip()