import pandas as pd
import random
import os
from datetime import datetime, timedelta

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# ========== ORGANIZATIONS ==========
organizations = pd.DataFrame({
    'Org Index': range(1, 100001),
    'Organization Id': [f'ORG{i:06d}' for i in range(1, 100001)],
    'Name': [f'Org{i}' for i in range(1, 100001)],
    'Website': [f'https://org{i}.com' for i in range(1, 100001)],
    'Country': ['Canada'] * 50000 + ['USA'] * 50000,
    'Description': ['Description'] * 100000,
    'Founded': [2010 + i % 15 for i in range(1, 100001)],
    'Industry': ['Technology'] * 50000 + ['Healthcare'] * 50000,
    'Number of employees': [random.randint(50, 10000) for _ in range(100000)]
})
organizations.to_csv('data/organizations.csv', index=False)

# ========== CUSTOMERS ==========
customer_ids = [f'CID{i:06d}' for i in range(1, 10001)]
organization_names = random.choices(organizations['Name'].tolist(), k=10000)

customers = pd.DataFrame({
    'Cust Index': range(1, 10001),
    'Customer Id': customer_ids,
    'First Name': [f'Name{i}' for i in range(1, 10001)],
    'Last Name': [random.choice(['Smith', 'Johnson', 'Lee', 'Patel', 'Garcia']) for _ in range(10000)],
    'Company': organization_names,
    'City': ['Toronto'] * 5000 + ['New York'] * 5000,
    'Country': ['Canada'] * 6000 + ['USA'] * 4000,
    'Phone 1': [f'{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}' for _ in range(10000)],
    'Phone 2': [f'{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}' for _ in range(10000)],
    'Email': [f'name{i}@example.com' for i in range(1, 10001)],
    'Subscription Date': ['2023-01-01'] * 10000,
    'Website': ['http://example.com'] * 10000
})
customers.to_csv('data/customers.csv', index=False)

# ========== PRODUCTS ==========
product_ids = [f'INT{i:06d}' for i in range(1, 100001)]
product_names = [f'Product{i}' for i in range(1, 100001)]
customer_id_choices = random.choices(customer_ids, k=100000)

products = pd.DataFrame({
    'Prod Index': range(1, 100001),
    'Internal ID': product_ids,
    'Name': product_names,
    'Description': [f'Smart device {i}' if i % 2 == 0 else f'Basic device {i}' for i in range(1, 100001)],
    'Brand': ['BrandA'] * 50000 + ['BrandB'] * 50000,
    'Category': ['Electronics'] * 50000 + ['Clothing'] * 50000,
    'Price': [round(random.uniform(20, 1000), 2) for _ in range(100000)],
    'Currency': ['USD'] * 100000,
    'Stock': [random.randint(0, 100) for _ in range(100000)],
    'EAN': [f'EAN{i:013d}' for i in range(1, 100001)],
    'Color': random.choices(['Black', 'White', 'Blue', 'Red'], k=100000),
    'Size': random.choices(['S', 'M', 'L', 'XL'], k=100000),
    'Availability': ['In Stock'] * 100000,
    'Customer Id': customer_id_choices
})
products.to_csv('data/products.csv', index=False)

# ========== TRANSACTIONS ==========
transaction_ids = [f'TX{i:07d}' for i in range(1, 200001)]
transaction_customer_ids = random.choices(customer_ids, k=200000)
transaction_product_ids = random.choices(product_ids, k=200000)

# Generate random purchase timestamps
start_date = datetime(2023, 1, 1)
timestamps = [(start_date + timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S') for i in range(200000)]

transactions = pd.DataFrame({
    'Transaction Id': transaction_ids,
    'Customer Id': transaction_customer_ids,
    'Product Id': transaction_product_ids,
    'Purchase Date': timestamps,
    'Quantity': [random.randint(1, 5) for _ in range(200000)],
    'Total Price': [round(random.uniform(20, 1500), 2) for _ in range(200000)]
})
transactions.to_csv('data/transactions.csv', index=False)

print("✅ All CSV files generated successfully in 'data/' folder.")
