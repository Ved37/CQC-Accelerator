import pandas as pd

class SimpleCQC:
    """
    Minimal CQC engine for acyclic conjunctive queries with comparisons.
    Supports:
      - Join queries (acyclic)
      - Comparisons (e.g., A.x < B.y, A.z = 5)
      - Logical combinations of comparisons (AND, OR)
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
        return tables

    def run_query(self, join_order, join_conditions, compare_conditions):
        df = self.tables[join_order[0]].copy()
        for i in range(1, len(join_order)):
            left = join_order[i - 1]
            right = join_order[i]
            cond = [c for c in join_conditions if (c[0], c[2]) == (left, right) or (c[2], c[0]) == (left, right)]
            if cond:
                c = cond[0]
                c1_sanitized = c[1].replace(' ', '_')
                c3_sanitized = c[3].replace(' ', '_')
                if c[0] == left:
                    df = df.merge(self.tables[right], left_on=f"{left}_{c1_sanitized}", right_on=f"{right}_{c3_sanitized}")
                else:
                    df = df.merge(self.tables[right], left_on=f"{left}_{c3_sanitized}", right_on=f"{right}_{c1_sanitized}")
            else:
                df = df.merge(self.tables[right], how='cross')

        # Apply comparison conditions
        for comp in compare_conditions:
            if len(comp) == 5:
                t1, col1, op, val, logic = comp
                col1_sanitized = col1.replace(' ', '_')
                left_col = f"{t1}_{col1_sanitized}"

                # Fix operator for equality
                if op == "=":
                    op = "=="

                if op == "IS NULL":
                    df = df[df[left_col].isnull()]
                elif op == "LIKE":
                    df = df[df[left_col].astype(str).str.contains(str(val), case=False, na=False)]
                elif op in ["IN", "NOT IN"]:
                    if not isinstance(val, (list, tuple, set)):
                        raise ValueError(f"Value for operator '{op}' must be a list, tuple or set")
                    if op == "IN":
                        df = df[df[left_col].isin(val)]
                    else:  # NOT IN
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
