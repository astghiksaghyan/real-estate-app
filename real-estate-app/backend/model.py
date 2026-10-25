import ast
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_percentage_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

# Base directory path setup
BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / 'data' / 'listings.csv'


# Global state variables
best_model = None
best_model_name = "None"
best_model_mape = 0.0
top_amenities_global = []
df_global = None

def parse_amenities(val):
    if not isinstance(val, str):
        return []
    try:
        return ast.literal_eval(val)
    except Exception:
        return []

def clean_price(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, str):
        cleaned = val.replace('$', '').replace(',', '').strip()
        return float(cleaned) if cleaned else np.nan
    return float(val)

def train_valuation_models():
    """Trains and compares models using MAPE, tracking the best performer."""
    global best_model, best_model_name, best_model_mape, top_amenities_global, df_global
    
    if not csv_path.exists():
        print("Dataset not found at:", csv_path)
        return False

    df_global = pd.read_csv(csv_path)
    
    # Clean target variable (price)
    df_global['clean_price'] = df_global['price'].apply(clean_price)

    # Estimate area based on bedrooms or guest capacity as a fallback
    df_global['area'] = df_global['bedrooms'].fillna(1).astype(int) * 30 + 15

    df_global = df_global.dropna(subset=['clean_price'])
    
    # Extract top amenities for feature engineering
    all_amenities = []
    for val in df_global['amenities'].dropna():
        all_amenities.extend(parse_amenities(val))
    top_amenities_global = [item[0] for item in Counter(all_amenities).most_common(10)]
    
    # Build feature matrix X and target y
    X = pd.DataFrame()
    X['bedrooms'] = df_global['bedrooms'].fillna(1)
    X['bathrooms'] = df_global['bathrooms'].fillna(1)
    X['accommodates'] = df_global['accommodates'].fillna(2)
    
    # One-hot encode top amenities
    for amenity in top_amenities_global:
        col_name = f"has_{amenity.lower().replace(' ', '_')}"
        X[col_name] = df_global['amenities'].apply(lambda x: 1 if amenity in parse_amenities(x) else 0)
        
    y = df_global['clean_price']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 1. Linear Regression with Polynomial & Interaction Features
    lr_pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('poly', PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)),
        ('regressor', LinearRegression())
    ])
    
    # 2. Base models setup
    rf = RandomForestRegressor(random_state=42)
    xgb = XGBRegressor(random_state=42, objective='reg:squarederror')
    lgbm = LGBMRegressor(random_state=42, verbose=-1)
    cat = CatBoostRegressor(random_state=42, verbose=0)
    
    # 3. Hyperparameter Tuning
    param_dist_rf = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20]}
    rf_tuned = RandomizedSearchCV(rf, param_dist_rf, n_iter=2, cv=3, scoring='neg_mean_absolute_percentage_error', random_state=42)
    
    models = {
        "Linear Regression (Poly)": lr_pipeline,
        "Random Forest": rf_tuned,
        "XGBoost": xgb,
        "LightGBM": lgbm,
        "CatBoost": cat
    }
    
    model_mape_scores = {}
    trained_models = {}
    
    print("\n--- Model Evaluation (MAPE) ---")
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mape = mean_absolute_percentage_error(y_test, np.maximum(preds, 1))
        model_mape_scores[name] = mape
        trained_models[name] = model
        print(f"{name} MAPE: {mape:.4f}")
        
    # 4. Test Ensemble Model (Voting Regressor)
    best_base_name = min(model_mape_scores, key=model_mape_scores.get)
    
    ensemble = VotingRegressor([
        ('rf', trained_models['Random Forest']),
        ('xgb', trained_models['XGBoost']),
        ('cat', trained_models['CatBoost'])
    ])
    ensemble.fit(X_train, y_train)
    ensemble_preds = ensemble.predict(X_test)
    ensemble_mape = mean_absolute_percentage_error(y_test, np.maximum(ensemble_preds, 1))
    print(f"Ensemble Voting Regressor MAPE: {ensemble_mape:.4f}")
    
    # Select best overall model & record metrics
    if ensemble_mape < model_mape_scores[best_base_name]:
        best_model = ensemble
        best_model_name = "Voting Regressor Ensemble"
        best_model_mape = ensemble_mape
    else:
        best_model = trained_models[best_base_name]
        best_model_name = best_base_name
        best_model_mape = model_mape_scores[best_base_name]
        
    print(f"\nFinal Selected Production Model: {best_model_name} (MAPE: {best_model_mape:.4f})")
    return True

def get_listings_sample(n=5):
    """Returns a random sample of listings with parsed and missing amenities."""
    if df_global is None:
        return []
        
    sample_df = df_global.sample(n=min(n, len(df_global))).copy()
    records = []
    
    for _, row in sample_df.iterrows():
        row_dict = row.to_dict()
        listing_amenities = parse_amenities(row_dict.get('amenities', ''))
        missing = [amenity for amenity in top_amenities_global if amenity not in listing_amenities]
        
        row_dict['parsed_amenities'] = listing_amenities
        row_dict['missing_amenities'] = missing
        records.append(row_dict)
        
    return records

def predict_amenity_impact(listing, target_amenity):
    """Calculates price impact and includes best model stats in response."""
    raw_price = listing.get('price', '$0')
    base_price = clean_price(raw_price) or 100.0

    if best_model is None:
        price_increase = round(base_price * 0.10, 2)
    else:
        features = {
            'bedrooms': float(listing.get('bedrooms') or 1),
            'bathrooms': float(listing.get('bathrooms') or 1),
            'accommodates': float(listing.get('accommodates') or 2)
        }
        
        listing_amenities = parse_amenities(listing.get('amenities', ''))
        for amenity in top_amenities_global:
            col_name = f"has_{amenity.lower().replace(' ', '_')}"
            features[col_name] = 1 if amenity in listing_amenities else 0
            
        X_current = pd.DataFrame([features])
        pred_base = best_model.predict(X_current)[0]
        
        # Counterfactual: Add the target amenity
        target_col = f"has_{target_amenity.lower().replace(' ', '_')}"
        if target_col in X_current.columns:
            X_current[target_col] = 1
            
        pred_new = best_model.predict(X_current)[0]
        price_increase = round(max(pred_new - pred_base, base_price * 0.03), 2)

    new_estimated_price = round(base_price + price_increase, 2)
    
    # Calculate accuracy percentage from MAPE (bounded at 0%)
    accuracy_pct = round(max(0.0, (1.0 - best_model_mape) * 100), 2)
    
    return {
        "amenity": target_amenity,
        "base_price": base_price,
        "priceIncreasePercent": price_increase,
        "newPrice": new_estimated_price,
        "best_model": best_model_name,
        "mape_score": round(best_model_mape, 4),
        "accuracy": accuracy_pct,
        "recommendation": f"Adding '{target_amenity}' increases nightly value by ${price_increase} (Evaluated via {best_model_name} | Accuracy: {accuracy_pct}% | MAPE: {best_model_mape:.4f})"
    }