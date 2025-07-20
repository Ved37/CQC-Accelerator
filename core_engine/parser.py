import re

def parse_query_from_string(query_string: str) -> dict:
    """
    Parses a simplified SQL-like query string into a structured dictionary
    that the SimpleCQ engine can understand.
    """
    query_parts = {
        "select_cols": [],
        "join_order": [],
        "join_conditions": [],
        "compare_conditions": []
    }

    query_string = query_string.replace('\n', ' ').strip()

    # Parse SELECT
    select_match = re.search(r'SELECT (.*?) FROM', query_string, re.IGNORECASE)
    if select_match:
        cols_str = select_match.group(1).strip()
        cols = re.findall(r'(\w+)\."([^"]+)"|(\w+)\.(\w+)', cols_str)
        query_parts["select_cols"] = [f"{t}.{c.strip()}" for t, c, t2, c2 in cols if c or c2]

    # Parse FROM and JOIN
    from_join_str = re.search(r'FROM (.*?) (?:WHERE|END|$)', query_string + " END", re.IGNORECASE).group(1)
    join_pattern = re.compile(r'(\w+)\s+JOIN\s+(\w+)\s+ON\s+(\w+)\."?([\w\s]+)"?\s*=\s*(\w+)\."?([\w\s]+)"?', re.IGNORECASE)
    
    first_table = from_join_str.split(' ')[0]
    query_parts["join_order"].append(first_table)

    for match in join_pattern.finditer(from_join_str):
        t1, t2, t1_col_t, t1_col, t2_col_t, t2_col = match.groups()
        if t2 not in query_parts["join_order"]:
            query_parts["join_order"].append(t2)
        query_parts["join_conditions"].append((t1, t1_col.strip(), t2, t2_col.strip()))

    # Parse WHERE
    where_match = re.search(r'WHERE (.*)', query_string, re.IGNORECASE)
    if where_match:
        where_str = where_match.group(1)
        conditions = re.split(r'\s+(AND|OR)\s+', where_str, flags=re.IGNORECASE)
        
        i = 0
        while i < len(conditions):
            condition_part = conditions[i]
            comp_match = re.match(r'(\w+)\."?([\w\s]+)"?\s*([<>=!]+|IS\s+NULL|LIKE|IN|NOT\s+IN)\s*(.*)', condition_part.strip(), re.IGNORECASE)
            if comp_match:
                table, col, op, val_str = comp_match.groups()
                col = col.strip()
                val_str = val_str.strip()
                if (val_str.startswith("'") and val_str.endswith("'")) or \
                   (val_str.startswith('"') and val_str.endswith('"')):
                    val = val_str.strip("'\"")
                else:
                    try: val = int(val_str)
                    except ValueError:
                        try: val = float(val_str)
                        except ValueError: val = val_str
                logic = "AND" if i + 1 >= len(conditions) else conditions[i+1].upper()
                query_parts["compare_conditions"].append((table, col, op.strip(), val, logic))
            i += 2

    return query_parts