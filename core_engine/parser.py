# core_engine/parser.py
import re

def parse_query_from_string(query_string: str) -> dict:
    """
    Parses a simplified SQL-like query string into a structured dictionary
    that the SimpleCQC engine can understand.

    Example Syntax:
    SELECT customers.Name, organizations.Industry
    FROM customers JOIN organizations ON customers.Company = organizations.Name
    WHERE customers.Country = 'Canada' AND organizations.NumberOfEmployees > 1000
    """
    query_parts = {
        "select_cols": [],
        "join_order": [],
        "join_conditions": [],
        "compare_conditions": []
    }

    # Normalize and split lines
    query_string = query_string.replace('\n', ' ').strip()

    # --- Parse SELECT ---
    select_match = re.search(r'SELECT (.*?) FROM', query_string, re.IGNORECASE)
    if select_match:
        cols_str = select_match.group(1).strip()
        query_parts["select_cols"] = [col.strip() for col in cols_str.split(',')]

    # --- Parse FROM and JOIN ---
    from_join_str = re.search(r'FROM (.*?) (?:WHERE|END)', query_string + " END", re.IGNORECASE).group(1)
    # This regex finds all tables and their join conditions
    join_pattern = re.compile(r'(\w+)\s+JOIN\s+(\w+)\s+ON\s+([\w\.]+)\s*=\s*([\w\.]+)', re.IGNORECASE)
    
    # Initial table
    first_table = from_join_str.split(' ')[0]
    query_parts["join_order"].append(first_table)

    for match in join_pattern.finditer(from_join_str):
        t1, t2, on1, on2 = match.groups()
        if t2 not in query_parts["join_order"]:
            query_parts["join_order"].append(t2)
        
        t1_name, col1 = on1.split('.')
        t2_name, col2 = on2.split('.')
        query_parts["join_conditions"].append((t1_name, col1, t2_name, col2))

    # --- Parse WHERE ---
    where_match = re.search(r'WHERE (.*)', query_string, re.IGNORECASE)
    if where_match:
        where_str = where_match.group(1)
        # Split by AND/OR, preserving the delimiter
        conditions = re.split(r'\s+(AND|OR)\s+', where_str, flags=re.IGNORECASE)
        
        i = 0
        while i < len(conditions):
            condition_part = conditions[i]
            # Regex for a single condition: table.column operator value
            comp_match = re.match(r'([\w\.]+)\s*([<>=!]+|IS\s+NULL|LIKE|IN|NOT\s+IN)\s*(.*)', condition_part.strip(), re.IGNORECASE)
            if comp_match:
                table_col, op, val_str = comp_match.groups()
                table, col = table_col.split('.')
                
                # Clean up value
                val_str = val_str.strip()
                if (val_str.startswith("'") and val_str.endswith("'")) or \
                   (val_str.startswith('"') and val_str.endswith('"')):
                    val = val_str.strip("'\"")
                else:
                    try: val = int(val_str)
                    except ValueError:
                        try: val = float(val_str)
                        except ValueError: val = val_str # It's a variable

                # Get the logical operator (AND/OR) for the next condition
                logic = "AND" # Default
                if i + 1 < len(conditions):
                    logic = conditions[i+1].upper()

                query_parts["compare_conditions"].append((table, col, op.strip(), val, logic))
            i += 2 # Move to the next condition part

    return query_parts