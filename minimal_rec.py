import csv
from collections import defaultdict

# Load basic data
vendors = []
with open('Train/vendors.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        vendors.append(int(row['id']))

# Load test data and create simple recommendations
recommendations = []
with open('Test/test_customers.csv', 'r') as f:
    reader = csv.DictReader(f)
    customers = [row['customer_id'] for row in reader]

with open('Test/test_locations.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        customer_id = row['customer_id']
        location_num = int(row['location_number'])
        
        # Simple approach: recommend top vendors for each customer-location
        for vendor_id in vendors[:5]:  # Top 5 vendors by ID
            identifier = f"{customer_id} X {location_num} X {vendor_id}"
            recommendations.append([identifier, 1])

# Save submission
with open('submission.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['CID X LOC_NUM X VENDOR', 'target'])
    writer.writerows(recommendations)

print("Done")
