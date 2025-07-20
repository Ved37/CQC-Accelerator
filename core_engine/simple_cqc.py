import pandas as pd
import re

class SimpleCQ:
    """
    Minimal engine for acyclic conjunctive queries with comparisons.
    """
    def __init__(self, tables: dict):
        self.tables = tables

    @staticmethod
    def prepare_tables(raw_tables: dict):
        tables = {}
        for tname, df in raw_tables.items():
            df = df.copy()
            df.columns = [f"{tname}_{col.replace(' ', '_')}" for col in df.columns]
            tables[tname] = df
            print(f"Debug: Table {tname} columns: {df.columns.tolist()}")
        return tables

    def run_query(self, join_order, join_conditions, compare_conditions):
        df = self.tables[join_order[0]].copy()
        print(f"Debug: Initial DF columns for {join_order[0]}: {df.columns.tolist()}")
        
        for i in range(1, len(join_order)):
            left = join_order[i - 1]
            right = join_order[i]
            cond = [c for c in join_conditions if (c[0], c[2]) == (left, right) or (c[2], c[0]) == (left, right)]
            if cond:
                c = cond[0]
                c1_sanitized = c[1].replace(' ', '_')
                c3_sanitized = c[3].replace(' ', '_')
                left_key = f"{left}_{c1_sanitized}" if c[0] == left else f"{left}_{c3_sanitized}"
                right_key = f"{right}_{c3_sanitized}" if c[0] == left else f"{right}_{c1_sanitized}"
                print(f"Debug: Merging {left} on {left_key} with {right} on {right_key}")
                df = df.merge(self.tables[right], left_on=left_key, right_on=right_key)
                print(f"Debug: Post-merge columns: {df.columns.tolist()}")
            else:
                df = df.merge(self.tables[right], how='cross')

        for comp in compare_conditions:
            if len(comp) == 5:
                t1, col1, op, val, logic = comp
                col1_sanitized = col1.replace(' ', '_')
                left_col = f"{t1}_{col1_sanitized}"
                if left_col not in df.columns:
                    raise ValueError(f"Column {left_col} not found in DataFrame. Available columns: {df.columns.tolist()}")
                if op == "=":
                    op = "=="
                if op == "IS NULL":
                    df = df[df[left_col].isnull()]
                elif op == "LIKE":
                    pattern = val.strip('%').replace('%', '.*')
                    df = df[df[left_col].astype(str).str.contains(pattern, case=False, na=False, regex=True)]
                elif op in ["IN", "NOT IN"]:
                    if not isinstance(val, (list, tuple, set)):
                        raise ValueError(f"Value for operator '{op}' must be a list, tuple or set")
                    if op == "IN":
                        df = df[df[left_col].isin(val)]
                    else:
                        df = df[~df[left_col].isin(val)]
                else:
                    if op == '<': df = df[df[left_col] < val]
                    elif op == '<=': df = df[df[left_col] <= val]
                    elif op == '>': df = df[df[left_col] > val]
                    elif op == '>=': df = df[df[left_col] >= val]
                    elif op == '==': df = df[df[left_col] == val]
                    elif op == '!=': df = df[df[left_col] != val]
                    else:
                        raise ValueError(f"Unsupported operator: {op}")
            else:
                raise ValueError("Invalid compare_conditions tuple length. Expected 5 elements.")

        return df