import pandas as pd

class SimpleCQ:
    """
    Advanced engine for acyclic conjunctive queries with comparisons, aggregates,
    grouping, ordering, limit/offset, and distinct.
    """
    def __init__(self, tables: dict):
        self.tables = tables

    @staticmethod
    def prepare_tables(raw_tables: dict):
        tables = {}
        for tname, df in raw_tables.items():
            new_columns = [f"{tname}_{col.replace(' ', '_')}" for col in df.columns]
            df = df.copy()
            df.columns = new_columns
            tables[tname] = df
            print(f"Debug: Table {tname} columns: {df.columns.tolist()}")
        return tables

    def run_query(
        self,
        join_order,
        join_conditions,
        compare_conditions,
        select_cols=None,
        select_aggs=None,
        distinct=False,
        order_by=None,
        limit=None,
        offset=None,
        group_by=None,
        having_conditions=None
    ):
        # 1. JOIN tables
        df = self.tables[join_order[0]].copy()
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
            else:
                df = df.merge(self.tables[right], how='cross')

        # 2. WHERE filtering
        if compare_conditions:
            mask = None
            for comp in compare_conditions:
                if len(comp) == 5:
                    t1, col1, op, val, logic = comp
                    col1_sanitized = col1.replace(' ', '_')
                    left_col = f"{t1}_{col1_sanitized}" if t1 else col1_sanitized
                    if left_col not in df.columns:
                        raise ValueError(f"Column {left_col} not found in DataFrame. Available columns: {df.columns.tolist()}")
                    # Build condition mask
                    if op == "=": op = "=="
                    if op == "IS NULL":
                        cond_mask = df[left_col].isnull()
                    elif op == "LIKE":
                        pattern = str(val).replace('%', '.*')
                        cond_mask = df[left_col].astype(str).str.contains(pattern, case=False, na=False, regex=True)
                    elif op in ["IN", "NOT IN"]:
                        if not isinstance(val, (list, tuple, set)):
                            val = [val]
                        if op == "IN":
                            cond_mask = df[left_col].isin(val)
                        else:
                            cond_mask = ~df[left_col].isin(val)
                    else:
                        if op == '<': cond_mask = df[left_col] < val
                        elif op == '<=': cond_mask = df[left_col] <= val
                        elif op == '>': cond_mask = df[left_col] > val
                        elif op == '>=': cond_mask = df[left_col] >= val
                        elif op == '==': cond_mask = df[left_col] == val
                        elif op == '!=': cond_mask = df[left_col] != val
                        else:
                            raise ValueError(f"Unsupported operator: {op}")
                    if mask is None:
                        mask = cond_mask
                    else:
                        if logic == "AND" or logic is None:
                            mask = mask & cond_mask
                        elif logic == "OR":
                            mask = mask | cond_mask
                        else:
                            raise ValueError(f"Unsupported logic operator: {logic}")
                else:
                    raise ValueError("Invalid compare_conditions tuple length. Expected 5 elements.")
            df = df[mask] if mask is not None else df

        # 3. GROUP BY and AGGREGATE
        if group_by and (select_aggs or having_conditions):
            # Build groupby columns
            gb_cols = []
            for t, c in group_by:
                gb_col = f"{t}_{c.replace(' ', '_')}" if t else c.replace(' ', '_')
                gb_cols.append(gb_col)
            grouped = df.groupby(gb_cols, dropna=False)
            agg_dict = {}
            agg_names = []
            for func, t, c, alias in select_aggs or []:
                if c == "*":
                    agg_col = None
                else:
                    agg_col = f"{t}_{c.replace(' ', '_')}" if t else c.replace(' ', '_')
                key = alias or f"{func}_{agg_col or 'all'}"
                agg_names.append(key)
                if func == "COUNT":
                    agg_dict[key] = (agg_col, 'count') if agg_col else ('count')
                elif func == "SUM":
                    agg_dict[key] = (agg_col, 'sum')
                elif func == "AVG":
                    agg_dict[key] = (agg_col, 'mean')
                elif func == "MIN":
                    agg_dict[key] = (agg_col, 'min')
                elif func == "MAX":
                    agg_dict[key] = (agg_col, 'max')
            # pandas groupby agg
            result_df = grouped.agg(**agg_dict).reset_index()
            # HAVING
            if having_conditions:
                mask = None
                for cond in having_conditions:
                    func, t, c, op, val, logic = cond
                    if func == "VALUE":
                        col_name = f"{t}_{c.replace(' ', '_')}" if t else c.replace(' ', '_')
                    else:
                        col_name = None
                        for f, t2, c2, alias in select_aggs or []:
                            if f == func and ((t2 == t and c2 == c) or (c == "*" and c2 == "*")):
                                col_name = alias or f"{func}_{f'{t2}_{c2}' if t2 and c2 else 'all'}"
                                break
                        if not col_name:
                            col_name = f"{func}_{t}_{c}"
                    # Build mask
                    if op == "=": op = "=="
                    cond_mask = None
                    if op == '<': cond_mask = result_df[col_name] < float(val)
                    elif op == '<=': cond_mask = result_df[col_name] <= float(val)
                    elif op == '>': cond_mask = result_df[col_name] > float(val)
                    elif op == '>=': cond_mask = result_df[col_name] >= float(val)
                    elif op == '==': cond_mask = result_df[col_name] == float(val)
                    elif op == '!=': cond_mask = result_df[col_name] != float(val)
                    else:
                        raise ValueError(f"Unsupported HAVING operator: {op}")
                    if mask is None:
                        mask = cond_mask
                    else:
                        if logic == "AND" or logic is None:
                            mask = mask & cond_mask
                        elif logic == "OR":
                            mask = mask | cond_mask
                        else:
                            raise ValueError(f"Unsupported HAVING logic: {logic}")
                result_df = result_df[mask] if mask is not None else result_df
        else:
            result_df = df.copy()
            # Select columns (if not using aggregates)
            if select_cols:
                final_cols = []
                for t, col, alias in select_cols:
                    sanitized_col = f"{t}_{col.replace(' ', '_')}" if t else col.replace(' ', '_')
                    if sanitized_col in result_df.columns:
                        final_cols.append(sanitized_col)
                if final_cols:
                    result_df = result_df[final_cols]
        # 4. DISTINCT
        if distinct:
            result_df = result_df.drop_duplicates()

        # 5. ORDER BY
        if order_by and result_df is not None and not result_df.empty:
            ob_cols = []
            ascending = []
            for t, col, asc in order_by:
                ob_col = f"{t}_{col.replace(' ', '_')}" if t else col.replace(' ', '_')
                if ob_col in result_df.columns:
                    ob_cols.append(ob_col)
                    ascending.append(asc)
            if ob_cols:
                result_df = result_df.sort_values(by=ob_cols, ascending=ascending)

        # 6. LIMIT/OFFSET
        if offset is not None and result_df is not None:
            result_df = result_df[offset:]
        if limit is not None and result_df is not None:
            result_df = result_df.head(limit)

        return result_df