from flask import Flask, jsonify, request
from pathlib import Path
from collections import Counter
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import ast
import xgboost as xgb

# Get the folder where this python script lives
BASE_DIR = Path(__file__).resolve().parent

# Build the absolute path to the CSV file
csv_path = BASE_DIR / 'data' / 'listings.csv'

app = Flask(__name__)

# Load the CSV dataset (assuming listings.csv is located in the same directory)
try:
    df = pd.read_csv(csv_path)

    # Estimate area based on bedrooms or guest capacity as a fallback
    df['area'] = df['bedrooms'].fillna(1).astype(int) * 30 + 15
except Exception as e:
    df = None

def parse_amenities(val):
    """Safely parse stringified python/json lists from CSV."""
    if not isinstance(val, str):
        return []
    try:
        return ast.literal_eval(val)
    except Exception:
        return []

# Compute top 10 most common amenities globally across the dataset
TOP_COMMON_AMENITIES = []
if df is not None and 'amenities' in df.columns:
    all_amenities = []
    for val in df['amenities'].dropna():
        all_amenities.extend(parse_amenities(val))
    TOP_COMMON_AMENITIES = [item[0] for item in Counter(all_amenities).most_common(10)]

@app.route('/api/listings', methods=['GET'])
def get_listings():
    if df is None:
        return jsonify({"error": "Dataset not found"}), 404

    # Take a random sample
    sample_df = df.sample(n=min(5, len(df))).copy()
    
    records = []
    for _, row in sample_df.iterrows():
        row_dict = row.to_dict()
        
        # Parse amenities for this specific listing
        listing_amenities = parse_amenities(row_dict.get('amenities', ''))
        
        # Find missing amenities by comparing against top common amenities
        missing = [amenity for amenity in TOP_COMMON_AMENITIES if amenity not in listing_amenities]
        
        row_dict['parsed_amenities'] = listing_amenities
        row_dict['missing_amenities'] = missing
        records.append(row_dict)

    # Replace NaN values with None for safe JSON serialization
    clean_records = pd.DataFrame(records).where(pd.notnull(pd.DataFrame(records)), None).to_dict(orient='records')
    
    return jsonify(clean_records), 200

@app.route('/api/analyze', methods=['POST'])
def analyze_amenity_impact():
    data = request.get_json() or {}
    listing = data.get('listing', {})
    target_amenity = data.get('amenity', '')

    # Placeholder for your ML valuation model logic
    # Example logic: estimate base price and calculate delta for adding the amenity
    base_price = float(listing.get('price_quote_price_per_night') or listing.get('price', 100))
    
    # Simulate valuation increase based on amenity addition (e.g., +5% to +12%)
    estimated_increase = round(base_price * 0.07, 2)
    new_estimated_price = round(base_price + estimated_increase, 2)

    return jsonify({
        "amenity": target_amenity,
        "base_price": base_price,
        "price_increase": estimated_increase,
        "new_estimated_price": new_estimated_price,
        "message": f"Adding '{target_amenity}' is estimated to increase nightly value by ${estimated_increase}."
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)