import pandas as pd
from core_engine.simple_cqc import SimpleCQC

# Toy data setup
A = pd.DataFrame({
    "id": [1, 2, 3],
    "x": [5, 6, 7],
})
B = pd.DataFrame({
    "a_id": [1, 2, 2, 3],
    "y": [10, 12, 13, 15],
})
C = pd.DataFrame({
    "b_id": [10, 12, 13, 15],
    "z": [100, 200, 300, 400],
})

tables = SimpleCQC.prepare_tables({"A": A, "B": B, "C": C})

# Build a query:
# SELECT * FROM A, B, C WHERE
#   A.id = B.a_id AND
#   B.y = C.b_id AND
#   A.x < B.y AND
#   C.z > 150

join_order = ["A", "B", "C"]
join_conditions = [
    ("A", "id", "B", "a_id"),
    ("B", "y", "C", "b_id"),
]
compare_conditions = [
    ("A", "x", "<", "B", "y"),
    ("C", "z", ">", 150),
]

cqc = SimpleCQC(tables)
result = cqc.run_query(join_order, join_conditions, compare_conditions)

print("CQC Query Results:")
print(result)