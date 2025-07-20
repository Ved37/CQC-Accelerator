import re

def parse_query_from_string(query_string: str) -> dict:
    """
    Parses a simplified SQL-like query string into a structured dictionary
    that the SimpleCQ engine can understand. Supports DISTINCT, JOIN, WHERE (AND/OR),
    ORDER BY, LIMIT, OFFSET, GROUP BY, HAVING, and aggregate functions.
    """
    query_parts = {
        "select_cols": [],
        "select_aggs": [],  # List of tuples: (func, table, column, alias)
        "distinct": False,
        "join_order": [],
        "join_conditions": [],
        "compare_conditions": [],
        "order_by": [],      # List of tuples: (table, col, asc)
        "limit": None,
        "offset": None,
        "group_by": [],
        "having_conditions": [],
        "aliases": {},
    }

    # Remove trailing semicolon
    query_string = query_string.strip().rstrip(';')

    # Remove line breaks
    query_string = query_string.replace('\n', ' ')

    # Parse SELECT [DISTINCT]
    select_match = re.search(r'SELECT\s+(DISTINCT\s+)?(.*?)(\s+FROM\s+)', query_string, re.IGNORECASE)
    if select_match:
        query_parts["distinct"] = bool(select_match.group(1))
        cols_str = select_match.group(2).strip()
        # Split columns by comma and handle each individually
        cols = [col.strip() for col in re.split(r',(?![^(]*\))', cols_str) if col.strip()]
        for col in cols:
            # Aggregate function?
            agg_match = re.match(r'(\w+)\((\*|\w+\.\w+|\w+)\)(?:\s+AS\s+(\w+))?', col, re.IGNORECASE)
            if agg_match:
                func, arg, alias = agg_match.groups()
                if '.' in arg:
                    table, column = arg.split('.', 1)
                elif arg == '*':
                    table, column = None, '*'
                else:
                    table, column = None, arg
                query_parts["select_aggs"].append((func.upper(), table, column, alias))
            else:
                # Qualified? (table.col)
                col_match = re.match(r'(\w+)\."?([\w\s]+)"?(?:\s+AS\s+(\w+))?$', col)
                if col_match:
                    table, column, alias = col_match.groups()
                    query_parts["select_cols"].append((table, column.strip(), alias))
                else:
                    # Unqualified
                    col_match = re.match(r'"?([\w\s]+)"?(?:\s+AS\s+(\w+))?$', col)
                    if col_match:
                        column, alias = col_match.groups()
                        query_parts["select_cols"].append((None, column.strip(), alias))
                    else:
                        print(f"Warning: Could not parse SELECT column: {col}")

    # Parse FROM, JOINs, and Aliases
    from_match = re.search(r'FROM\s+([^\s,]+)(?:\s+AS\s+(\w+))?', query_string, re.IGNORECASE)
    if from_match:
        main_table, alias = from_match.groups()
        query_parts["join_order"].append(main_table)
        if alias:
            query_parts["aliases"][alias] = main_table
    # All JOINs
    join_pattern = re.compile(
        r'(?:INNER\s+)?JOIN\s+([^\s]+)(?:\s+AS\s+(\w+))?\s+ON\s+(\w+)\."?([\w\s]+)"?\s*=\s*(\w+)\."?([\w\s]+)"?',
        re.IGNORECASE)
    for match in join_pattern.finditer(query_string):
        t2, alias2, t1, col1, t2b, col2 = match.groups()
        query_parts["join_order"].append(t2)
        if alias2:
            query_parts["aliases"][alias2] = t2
        query_parts["join_conditions"].append((t1, col1.strip(), t2b, col2.strip()))

    # Parse WHERE
    where_match = re.search(r'WHERE (.*?)(GROUP BY|ORDER BY|HAVING|LIMIT|OFFSET|$)', query_string, re.IGNORECASE)
    if where_match:
        where_str = where_match.group(1).strip()
        tokens = re.split(r'(\s+(?:AND|OR)\s+)', where_str, flags=re.IGNORECASE)
        conditions = []
        logic_ops = []
        for token in tokens:
            if token.strip().upper() in ('AND', 'OR'):
                logic_ops.append(token.strip().upper())
            elif token.strip():
                conditions.append(token.strip())
        for i, cond_str in enumerate(conditions):
            # Try table.column first
            comp_match = re.match(r'(\w+)\."?([\w\s]+)"?\s*([<>=!]+|IS\s+NULL|LIKE|IN|NOT\s+IN)\s*(.*)', cond_str, re.IGNORECASE)
            if comp_match:
                table, col, op, val_str = comp_match.groups()
            else:
                # Try just column
                comp_match = re.match(r'"?([\w\s]+)"?\s*([<>=!]+|IS\s+NULL|LIKE|IN|NOT\s+IN)\s*(.*)', cond_str, re.IGNORECASE)
                if comp_match:
                    col, op, val_str = comp_match.groups()
                    table = query_parts["join_order"][0]
                else:
                    print(f"Warning: Could not parse WHERE condition: {cond_str}")
                    continue
            col = col.strip()
            val_str = val_str.strip()
            if (val_str.startswith("'") and val_str.endswith("'")) or (val_str.startswith('"') and val_str.endswith('"')):
                val = val_str.strip("'\"")
            elif val_str.upper() == "NULL":
                val = None
            elif op.upper() in ("IN", "NOT IN"):
                # Parse IN list
                val = [v.strip(" '\"") for v in re.split(r',', val_str.strip("() ")) if v.strip()]
            else:
                try: val = int(val_str)
                except ValueError:
                    try: val = float(val_str)
                    except ValueError: val = val_str
            logic = logic_ops[i] if i < len(logic_ops) else None
            query_parts["compare_conditions"].append((table, col, op.strip(), val, logic))

    # Parse GROUP BY
    gb_match = re.search(r'GROUP BY\s+(.*?)(ORDER BY|HAVING|LIMIT|OFFSET|$)', query_string, re.IGNORECASE)
    if gb_match:
        gb_str = gb_match.group(1).strip()
        gb_cols = [col.strip() for col in gb_str.split(',')]
        for gb_col in gb_cols:
            if '.' in gb_col:
                table, col = gb_col.split('.', 1)
            else:
                table, col = None, gb_col
            query_parts["group_by"].append((table, col))

    # Parse HAVING
    having_match = re.search(r'HAVING\s+(.*?)(ORDER BY|LIMIT|OFFSET|$)', query_string, re.IGNORECASE)
    if having_match:
        having_str = having_match.group(1).strip()
        tokens = re.split(r'(\s+(?:AND|OR)\s+)', having_str, flags=re.IGNORECASE)
        conditions = []
        logic_ops = []
        for token in tokens:
            if token.strip().upper() in ('AND', 'OR'):
                logic_ops.append(token.strip().upper())
            elif token.strip():
                conditions.append(token.strip())
        for i, cond_str in enumerate(conditions):
            # Support aggregates in HAVING
            agg_match = re.match(r'(\w+)\((\*|\w+\.\w+|\w+)\)\s*([<>=!]+)\s*(.*)', cond_str, re.IGNORECASE)
            if agg_match:
                func, arg, op, val_str = agg_match.groups()
                if '.' in arg:
                    table, col = arg.split('.', 1)
                elif arg == '*':
                    table, col = None, '*'
                else:
                    table, col = None, arg
                val = val_str.strip("'\"")
                logic = logic_ops[i] if i < len(logic_ops) else None
                query_parts["having_conditions"].append((func.upper(), table, col, op.strip(), val, logic))
            else:
                # Try table.column
                comp_match = re.match(r'(\w+)\."?([\w\s]+)"?\s*([<>=!]+)\s*(.*)', cond_str, re.IGNORECASE)
                if comp_match:
                    table, col, op, val_str = comp_match.groups()
                else:
                    comp_match = re.match(r'"?([\w\s]+)"?\s*([<>=!]+)\s*(.*)', cond_str, re.IGNORECASE)
                    if comp_match:
                        col, op, val_str = comp_match.groups()
                        table = query_parts["join_order"][0]
                    else:
                        print(f"Warning: Could not parse HAVING condition: {cond_str}")
                        continue
                col = col.strip()
                val = val_str.strip("'\"")
                logic = logic_ops[i] if i < len(logic_ops) else None
                query_parts["having_conditions"].append(("VALUE", table, col, op.strip(), val, logic))

    # Parse ORDER BY
    ob_match = re.search(r'ORDER BY\s+(.*?)(LIMIT|OFFSET|$)', query_string, re.IGNORECASE)
    if ob_match:
        ob_str = ob_match.group(1).strip()
        ob_items = [o.strip() for o in ob_str.split(',')]
        for ob in ob_items:
            ob_parts = ob.split()
            if len(ob_parts) == 2:
                col, direction = ob_parts
            else:
                col, direction = ob_parts[0], "ASC"
            if '.' in col:
                table, col = col.split('.', 1)
            else:
                table, col = None, col
            query_parts["order_by"].append((table, col, direction.upper() == "ASC"))

    # Parse LIMIT
    limit_match = re.search(r'LIMIT\s+(\d+)', query_string, re.IGNORECASE)
    if limit_match:
        query_parts["limit"] = int(limit_match.group(1))

    # Parse OFFSET
    offset_match = re.search(r'OFFSET\s+(\d+)', query_string, re.IGNORECASE)
    if offset_match:
        query_parts["offset"] = int(offset_match.group(1))

    print(f"Debug: Parsed query parts: {query_parts}")
    return query_parts