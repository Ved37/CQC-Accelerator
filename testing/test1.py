# Test script to debug query parsing issues
# You can run this separately to test your queries

from core_engine.parser import parse_query_from_string
from benchmarking_suite.helpers import generate_sql_equivalent_query

def test_query_parsing():
    # Test queries with your data structure
    test_queries = [
        # Simple query - should work
        "SELECT products.Name, products.Price FROM products WHERE products.Price > 500",
        
        # Query with spaces in column names - might fail
        '''SELECT products."Name", products."Price" FROM products WHERE products."Price" > 500''',
        
        # Query with underscore names (what your system expects)
        "SELECT products.Name, products.Price FROM products WHERE products.Price > 500",
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n--- Test Query {i+1} ---")
        print(f"Original: {query}")
        
        try:
            # Parse the query
            parsed = parse_query_from_string(query)
            print(f"Parsed select_cols: {parsed['select_cols']}")
            print(f"Join order: {parsed['join_order']}")
            print(f"Compare conditions: {parsed['compare_conditions']}")
            
            # Generate SQL
            sql = generate_sql_equivalent_query(parsed, parsed.get("select_cols"))
            print(f"Generated SQL: {sql}")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_query_parsing()

# Updated sample queries for your app based on your actual data structure
WORKING_SAMPLE_QUERIES = [
    # Products only
    """SELECT products.Name, products.Price
FROM products
WHERE products.Price > 500""",
    
    # Products with category filter
    """SELECT products.Name, products.Category, products.Price
FROM products
WHERE products.Category = 'Electronics'""",
    
    # Customer-Product join (if you have matching Customer_Id)
    """SELECT customers.First_Name, products.Name
FROM customers
JOIN products ON customers.Customer_Id = products.Customer_Id
WHERE products.Price > 300""",
    
    # Transaction-Product join
    """SELECT products.Name, transactions.Quantity, transactions.Total_Price
FROM products
JOIN transactions ON products.Internal_ID = transactions.Product_Id
WHERE transactions.Quantity > 2""",
]

# Function to validate column names against your actual data
def validate_query_columns(query_parts, tables):
    """
    Check if the columns referenced in the query actually exist in your tables
    """
    issues = []
    
    # Check select columns
    for col in query_parts.get("select_cols", []):
        if '.' in col:
            table, column = col.split('.', 1)
            if table in tables:
                # Check if column exists (with or without spaces/underscores)
                actual_columns = list(tables[table].columns)
                column_variants = [
                    column,
                    column.replace(' ', '_'),
                    column.replace('_', ' ')
                ]
                
                if not any(variant in actual_columns for variant in column_variants):
                    issues.append(f"Column '{column}' not found in table '{table}'. Available: {actual_columns}")
            else:
                issues.append(f"Table '{table}' not found")
    
    # Check join conditions
    for t1, c1, t2, c2 in query_parts.get("join_conditions", []):
        if t1 in tables:
            if c1 not in tables[t1].columns and c1.replace(' ', '_') not in tables[t1].columns:
                issues.append(f"Join column '{c1}' not found in table '{t1}'")
        if t2 in tables:
            if c2 not in tables[t2].columns and c2.replace(' ', '_') not in tables[t2].columns:
                issues.append(f"Join column '{c2}' not found in table '{t2}'")
    
    return issues