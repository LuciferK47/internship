import csv
import math
from collections import defaultdict

def distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points"""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * math.asin(math.sqrt(a)) * 6371  # Earth radius in km

# Load data
print("Loading data...")

# Load vendors
vendors = {}
with open('Train/vendors.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        vendors[int(row['id'])] = {
            'lat': float(row['latitude']),
            'lon': float(row['longitude']),
            'rating': float(row.get('vendor_rating', 0) or 0),
            'delivery_charge': float(row.get('delivery_charge', 0) or 0)
        }

print(f"Loaded {len(vendors)} vendors")

# Load orders to understand preferences
customer_orders = defaultdict(set)
with open('Train/orders.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        customer_orders[row['customer_id']].add(int(row['vendor_id']))

print(f"Loaded orders for {len(customer_orders)} customers")

# Load test customers and locations
test_data = []
with open('Test/test_customers.csv', 'r') as f:
    reader = csv.DictReader(f)
    test_customers = {row['customer_id']: row for row in reader}

with open('Test/test_locations.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        customer_id = row['customer_id']
        if customer_id in test_customers:
            # Skip rows with empty latitude or longitude
            if not row['latitude'] or not row['longitude']:
                continue
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                test_data.append({
                    'customer_id': customer_id,
                    'location_number': int(row['location_number']),
                    'lat': lat,
                    'lon': lon
                })
            except (ValueError, TypeError):
                # Skip invalid coordinate data
                continue

print(f"Loaded {len(test_data)} test location records")

# Generate recommendations
print("Generating recommendations...")
recommendations = []

for test_loc in test_data:
    customer_id = test_loc['customer_id']
    location_num = test_loc['location_number']
    customer_lat = test_loc['lat']
    customer_lon = test_loc['lon']
    
    # Score each vendor for this customer-location
    vendor_scores = []
    
    for vendor_id, vendor_info in vendors.items():
        # Calculate distance
        dist = distance(customer_lat, customer_lon, vendor_info['lat'], vendor_info['lon'])
        
        # Simple scoring: closer is better, higher rating is better, lower delivery charge is better
        score = 0
        
        # Distance score (closer = higher score)
        if dist < 1:
            score += 10
        elif dist < 5:
            score += 5
        elif dist < 10:
            score += 2
        
        # Rating score
        score += vendor_info['rating']
        
        # Delivery charge score (lower = better)
        if vendor_info['delivery_charge'] == 0:
            score += 3
        elif vendor_info['delivery_charge'] < 1:
            score += 1
        
        # Historical preference bonus
        if vendor_id in customer_orders.get(customer_id, set()):
            score += 15  # Strong bonus for previous orders
        
        vendor_scores.append((vendor_id, score, dist))
    
    # Sort by score (descending) and take top vendors
    vendor_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Select top vendors with good scores
    for vendor_id, score, dist in vendor_scores[:5]:  # Top 5 vendors
        if score > 3:  # Minimum score threshold
            recommendations.append({
                'customer_id': customer_id,
                'location_number': location_num,
                'vendor_id': vendor_id,
                'score': score
            })

# Create submission file
print("Creating submission...")
with open('submission.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['CID X LOC_NUM X VENDOR', 'target'])
    
    for rec in recommendations:
        identifier = f"{rec['customer_id']} X {rec['location_number']} X {rec['vendor_id']}"
        writer.writerow([identifier, 1])

print(f"Generated {len(recommendations)} recommendations")
print("Submission saved to submission.csv")
