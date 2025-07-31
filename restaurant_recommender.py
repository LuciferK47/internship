#!/usr/bin/env python3
"""
Restaurant Recommendation Engine
Predicts which restaurants customers are most likely to order from
"""

import csv
import math
from collections import defaultdict, Counter

class RestaurantRecommender:
    def __init__(self):
        self.vendors = {}
        self.customer_orders = defaultdict(set)
        self.customer_preferences = defaultdict(Counter)
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points on earth (km)"""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return c * 6371  # Earth radius in km
    
    def load_data(self):
        """Load all training data"""
        print("Loading training data...")
        
        # Load vendors
        with open('Train/vendors.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vendor_id = int(row['id'])
                self.vendors[vendor_id] = {
                    'lat': float(row['latitude']),
                    'lon': float(row['longitude']),
                    'category': row['vendor_category_en'],
                    'rating': float(row.get('vendor_rating', 0) or 0),
                    'delivery_charge': float(row.get('delivery_charge', 0) or 0),
                    'serving_distance': float(row.get('serving_distance', 10) or 10),
                    'is_open': int(row.get('is_open', 1) or 1),
                    'discount': float(row.get('discount_percentage', 0) or 0)
                }
        
        print(f"Loaded {len(self.vendors)} vendors")
        
        # Load orders to understand customer preferences
        with open('Train/orders.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_id = row['customer_id']
                vendor_id = int(row['vendor_id'])
                
                self.customer_orders[customer_id].add(vendor_id)
                
                # Track category preferences
                if vendor_id in self.vendors:
                    category = self.vendors[vendor_id]['category']
                    self.customer_preferences[customer_id][category] += 1
        
        print(f"Loaded order history for {len(self.customer_orders)} customers")
    
    def calculate_vendor_score(self, customer_id, customer_lat, customer_lon, vendor_id):
        """Calculate recommendation score for customer-vendor pair"""
        if vendor_id not in self.vendors:
            return 0
        
        vendor = self.vendors[vendor_id]
        
        # Calculate distance
        distance = self.haversine_distance(
            customer_lat, customer_lon,
            vendor['lat'], vendor['lon']
        )
        
        # Skip if outside serving distance
        if distance > vendor['serving_distance']:
            return 0
        
        # Base score
        score = 0
        
        # Distance score (closer is better)
        if distance <= 1:
            score += 20
        elif distance <= 3:
            score += 15
        elif distance <= 5:
            score += 10
        elif distance <= 8:
            score += 5
        else:
            score += 1
        
        # Rating score
        score += vendor['rating'] * 3
        
        # Delivery charge penalty
        score -= vendor['delivery_charge'] * 2
        
        # Discount bonus
        score += vendor['discount'] * 0.5
        
        # Open status
        if not vendor['is_open']:
            score *= 0.1
        
        # Historical preference bonus
        if vendor_id in self.customer_orders.get(customer_id, set()):
            score += 50  # Strong bonus for previous orders
        
        # Category preference bonus
        category = vendor['category']
        if customer_id in self.customer_preferences:
            category_count = self.customer_preferences[customer_id].get(category, 0)
            score += category_count * 2
        
        return max(0, score)
    
    def generate_recommendations(self):
        """Generate recommendations for test data"""
        print("Generating recommendations...")
        
        recommendations = []
        
        # Load test customers
        test_customers = {}
        with open('Test/test_customers.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_customers[row['customer_id']] = row
        
        # Process test locations
        with open('Test/test_locations.csv', 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                customer_id = row['customer_id']
                location_num = int(row['location_number'])
                customer_lat = float(row['latitude'])
                customer_lon = float(row['longitude'])
                
                # Score all vendors for this customer-location
                vendor_scores = []
                
                for vendor_id in self.vendors:
                    score = self.calculate_vendor_score(
                        customer_id, customer_lat, customer_lon, vendor_id
                    )
                    
                    if score > 0:
                        vendor_scores.append((vendor_id, score))
                
                # Sort by score and select top recommendations
                vendor_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Select top vendors (adjust threshold as needed)
                min_score = max(10, vendor_scores[0][1] * 0.1) if vendor_scores else 10
                
                for vendor_id, score in vendor_scores:
                    if score >= min_score and len([r for r in recommendations 
                                                 if r['customer_id'] == customer_id and 
                                                    r['location_number'] == location_num]) < 10:
                        
                        recommendations.append({
                            'customer_id': customer_id,
                            'location_number': location_num,
                            'vendor_id': vendor_id,
                            'score': score
                        })
        
        return recommendations
    
    def save_submission(self, recommendations):
        """Save recommendations in required format"""
        print("Saving submission...")
        
        with open('submission.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['CID X LOC_NUM X VENDOR', 'target'])
            
            for rec in recommendations:
                identifier = f"{rec['customer_id']} X {rec['location_number']} X {rec['vendor_id']}"
                writer.writerow([identifier, 1])
        
        print(f"Saved {len(recommendations)} recommendations to submission.csv")
    
    def run(self):
        """Run the complete recommendation pipeline"""
        print("Restaurant Recommendation Engine")
        print("=" * 40)
        
        # Load training data
        self.load_data()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Save submission
        self.save_submission(recommendations)
        
        print("\nRecommendation engine completed successfully!")
        print(f"Generated {len(recommendations)} total recommendations")
        
        # Show sample recommendations
        print("\nSample recommendations:")
        for i, rec in enumerate(recommendations[:10]):
            print(f"{rec['customer_id']} X {rec['location_number']} X {rec['vendor_id']} (score: {rec['score']:.1f})")

def main():
    recommender = RestaurantRecommender()
    recommender.run()

if __name__ == "__main__":
    main()