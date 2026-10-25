import pandas as pd
from flask import Flask, jsonify, request
from model import train_valuation_models, get_listings_sample, predict_amenity_impact, csv_path

app = Flask(__name__)

# Initialize and train ML models on startup
print("Initializing ML models...")
train_valuation_models()

@app.route('/api/listings', methods=['GET'])
def get_listings():
    if not csv_path.exists():
        return jsonify({"error": "Dataset not found"}), 404

    records = get_listings_sample(n=5)
    clean_records = pd.DataFrame(records).where(pd.notnull(pd.DataFrame(records)), 0).to_dict(orient='records')
    return jsonify(clean_records), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_amenity_impact():
    data = request.get_json() or {}
    listing = data.get('listing', {})
    target_amenity = data.get('missingFeature', '')

    if not listing or not target_amenity:
        return jsonify({"error": "Missing listing data or amenity"}), 400

    result = predict_amenity_impact(listing, target_amenity)
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)






