import csv
import os

print("Data files:")
for f in ['Train/train_customers.csv', 'Train/vendors.csv', 'Train/orders.csv']:
    if os.path.exists(f):
        size = os.path.getsize(f) / 1024 / 1024
        print(f"{f}: {size:.1f}MB")
        
        with open(f, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            print(f"  Columns: {header[:5]}...")
            row1 = next(reader)
            print(f"  Sample: {row1[:3]}...")
        print()
