import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from math import radians, cos, sin, asin, sqrt
import warnings
warnings.filterwarnings('ignore')

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on earth (in km)"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371  # Earth radius in km

def main():
    print("Loading data...")
    
    # Load data
    train_customers = pd.read_csv('Train/train_customers.csv')
    vendors = pd.read_csv('Train/vendors.csv')
    train_locations = pd.read_csv('Train/train_locations.csv')
    orders = pd.read_csv('Train/orders.csv')
    test_customers = pd.read_csv('Test/test_customers.csv')
    test_locations = pd.read_csv('Test/test_locations.csv')
    
    print(f"Loaded {len(train_customers)} customers, {len(vendors)} vendors, {len(orders)} orders")
    
    # Create training features
    print("Creating training features...")
    train_features = []
    
    for _, customer in train_customers.iterrows():
        customer_id = customer['customer_id']
        customer_locations = train_locations[train_locations['customer_id'] == customer_id]
        
        for _, location in customer_locations.iterrows():
            for _, vendor in vendors.iterrows():
                # Calculate distance
                distance = haversine_distance(
                    location['latitude'], location['longitude'],
                    vendor['latitude'], vendor['longitude']
                )
                
                # Check if customer ordered from this vendor
                customer_orders = orders[orders['customer_id'] == customer_id]
                vendor_orders = customer_orders[customer_orders['vendor_id'] == vendor['id']]
                target = 1 if len(vendor_orders) > 0 else 0
                
                train_features.append({
                    'customer_id': customer_id,
                    'location_number': location['location_number'],
                    'vendor_id': vendor['id'],
                    'distance_km': distance,
                    'vendor_rating': vendor.get('vendor_rating', 0),
                    'delivery_charge': vendor['delivery_charge'],
                    'serving_distance': vendor['serving_distance'],
                    'target': target
                })
    
    train_df = pd.DataFrame(train_features)
    print(f"Created {len(train_df)} training samples")
    
    # Prepare training data
    feature_cols = ['distance_km', 'vendor_rating', 'delivery_charge', 'serving_distance']
    X_train = train_df[feature_cols].fillna(0)
    y_train = train_df['target']
    
    print(f"Training model on {len(X_train)} samples...")
    
    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    print(f"Model accuracy on training data: {model.score(X_train, y_train):.3f}")
    
    # Create test features and predictions
    print("Creating test predictions...")
    test_features = []
    
    for _, customer in test_customers.iterrows():
        customer_id = customer['customer_id']
        customer_locations = test_locations[test_locations['customer_id'] == customer_id]
        
        for _, location in customer_locations.iterrows():
            for _, vendor in vendors.iterrows():
                distance = haversine_distance(
                    location['latitude'], location['longitude'],
                    vendor['latitude'], vendor['longitude']
                )
                
                test_features.append({
                    'customer_id': customer_id,
                    'location_number': location['location_number'],
                    'vendor_id': vendor['id'],
                    'distance_km': distance,
                    'vendor_rating': vendor.get('vendor_rating', 0),
                    'delivery_charge': vendor['delivery_charge'],
                    'serving_distance': vendor['serving_distance']
                })
    
    test_df = pd.DataFrame(test_features)
    X_test = test_df[feature_cols].fillna(0)
    
    # Make predictions
    probabilities = model.predict_proba(X_test)[:, 1]
    test_df['prediction_prob'] = probabilities
    
    # Create submission
    print("Creating submission...")
    recommendations = []
    
    grouped = test_df.groupby(['customer_id', 'location_number'])
    for (customer_id, location_num), group in grouped:
        # Select top vendors with probability > threshold
        top_vendors = group[group['prediction_prob'] > 0.1].sort_values('prediction_prob', ascending=False)
        
        if len(top_vendors) == 0:
            top_vendors = group.sort_values('prediction_prob', ascending=False).head(1)
        
        for _, row in top_vendors.iterrows():
            recommendations.append({
                'CID X LOC_NUM X VENDOR': f"{customer_id} X {int(location_num)} X {int(row['vendor_id'])}",
                'target': 1
            })
    
    submission_df = pd.DataFrame(recommendations)
    submission_df.to_csv('submission.csv', index=False)
    
    print(f"Submission saved with {len(submission_df)} predictions")
    print("Sample predictions:")
    print(submission_df.head())

if __name__ == "__main__":
    main()
