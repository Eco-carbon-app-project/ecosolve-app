import math

# ==========================================
# 🌍 THE MASSIVE DATA POOL
# Real-world estimated CO2 values (in kg CO2)
# Positive values mean emissions created.
# ==========================================

CARBON_DB = {
    "🥤 Beverages & Packaging": {
        "Plastic Bottle (< 500ml)": 0.082,
        "Plastic Bottle (500ml - 1L)": 0.160,
        "Plastic Bottle (> 1L)": 0.280,
        "Paper Coffee Cup (with plastic lid)": 0.110,
        "Aluminum Can (330ml)": 0.170,
        "Glass Bottle (Single Use)": 0.350,
        "Reusable Metal Flask / Bottle (per use)": 0.005,
        "Ceramic Mug (per use)": 0.005,
        "Plastic Straw": 0.003,
        "Plastic Shopping Bag": 0.033,
        "Reusable Cloth Tote Bag (per use)": 0.001,
    },
    
    "🚶 Mobility & Transport": {
        "Walked (per 1 km)": 0.0,
        "Bicycle (per 1 km)": 0.0,
        "Staircase - Going UP (per 1 floor)": 0.0,
        "Staircase - Going DOWN (per 1 floor)": 0.0,
        "Elevator - Going UP (per 1 floor)": 0.015,
        "Elevator - Going DOWN (per 1 floor)": 0.010,
        "Electric Scooter (per 1 km)": 0.030,
        "Petrol Car - Solo driving (per 1 km)": 0.192,
        "Diesel Car - Solo driving (per 1 km)": 0.171,
        "Electric Vehicle - Solo (per 1 km)": 0.053,
        "Carpool / Shared Cab (per 1 km)": 0.080,
        "Public Bus (per 1 km)": 0.105,
        "Metro / Train (per 1 km)": 0.041,
        "Motorcycle / Scooter (per 1 km)": 0.103,
    },
    
    "🍔 Food & Diet": {
        "Beef / Mutton meal (Average serving)": 7.70,
        "Pork meal (Average serving)": 2.20,
        "Chicken meal (Average serving)": 1.36,
        "Fish / Seafood meal (Average serving)": 1.50,
        "Vegetarian meal (Dairy included)": 0.80,
        "Vegan / Plant-based meal": 0.50,
        "Fast Food Burger Meal": 3.50,
        "Food waste thrown in trash (per 1 kg)": 2.50,
        "Food waste composted (per 1 kg)": 0.20,
    },
    
    "⚡ Energy & Appliances": {
        "Air Conditioner (per 1 hour)": 0.85,
        "Electric Heater (per 1 hour)": 0.70,
        "Ceiling Fan (per 1 hour)": 0.03,
        "Incandescent Bulb (per 1 hour)": 0.02,
        "LED Bulb (per 1 hour)": 0.003,
        "Laptop charging/use (per 1 hour)": 0.01,
        "Desktop PC running (per 1 hour)": 0.08,
        "Washing machine - Hot wash (per load)": 0.90,
        "Washing machine - Cold wash (per load)": 0.30,
        "Clothes Dryer (per load)": 1.80,
        "Air-drying clothes on rack (per load)": 0.0,
        "Hot Water Shower (per 10 mins)": 1.20,
        "Cold Water Shower (per 10 mins)": 0.10,
    }
}

# ==========================================
# 🛠️ HELPER FUNCTIONS
# ==========================================

def get_all_categories():
    """Returns a list of all main categories."""
    return list(CARBON_DB.keys())

def get_items(category_name):
    """
    Returns a list of items for a specific category.
    When passed to Streamlit's st.selectbox, this list is automatically searchable by typing!
    """
    if category_name in CARBON_DB:
        return list(CARBON_DB[category_name].keys())
    return []

def search_items(query):
    """
    Global search function across all categories.
    """
    results = []
    query = query.lower()
    for cat, items in CARBON_DB.items():
        for item in items.keys():
            if query in item.lower():
                results.append({"category": cat, "item": item})
    return results

def get_carbon_value(category, item):
    """Returns the carbon footprint (kg CO2) of a specific item per unit."""
    try:
        return CARBON_DB[category][item]
    except KeyError:
        return 0.0

# ==========================================
# 🧮 THE MATH ENGINE
# ==========================================

def calculate_impact(used_cart, avoided_cart):
    """
    Calculates total emitted, total avoided, net saved, and gamification points.
    """
    total_emitted = 0.0
    total_avoided = 0.0
    
    # 1. What was USED adds to your emissions
    for item in used_cart:
        co2_val = get_carbon_value(item['category'], item['item'])
        total_emitted += (co2_val * float(item['qty']))
        
    # 2. What was AVOIDED saves emissions (acts as your baseline)
    for item in avoided_cart:
        co2_val = get_carbon_value(item['category'], item['item'])
        total_avoided += (co2_val * float(item['qty']))
        
    # 3. Net Carbon Saved
    # E.g., if you avoided driving (0.192 kg) but used a bike (0.00 kg), you saved +0.192 kg!
    # If you avoided the stairs (0.00 kg) and used the elevator (0.015 kg), you saved -0.015 kg (Negative).
    net_saved = total_avoided - total_emitted
    
    # 4. Points system: 100 points for every 1 kg CO2 saved
    if net_saved > 0:
        points = int(math.ceil(net_saved * 100))
    else:
        # If you emitted more than you avoided, you get 0 points (no negative scores)
        points = 0
        
    return round(net_saved, 3), points, round(total_emitted, 3), round(total_avoided, 3)