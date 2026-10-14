import math

# ==========================================
# 🌍 THE MASSIVE DATA POOL
# Real-world estimated CO2 values (in kg CO2)
# Positive values mean emissions created.
# ==========================================

CARBON_DB = {
    "🥤 Beverages & Packaging (Base Units)": {
        "Plastic Water Bottle (250ml)": 0.050,
        "Plastic Water Bottle (500ml)": 0.082,
        "Plastic Water Bottle (1L)": 0.160,
        "Plastic Water Bottle (2L)": 0.280,
        "Glass Bottle (Single-use)": 0.350,
        "Aluminum Can (330ml)": 0.170,
        "Paper Cup (No Lid)": 0.030,
        "Paper Cup (with Plastic Lid)": 0.080,
        "Styrofoam Cup": 0.040,
        "Plastic Straw": 0.003,
        "Paper Straw": 0.001,
        "Reusable Metal Straw (per use)": 0.0005,
        "Reusable Metal Flask (per use)": 0.005,
        "Reusable Hard Plastic Bottle (per use)": 0.003,
        "Ceramic Mug (per use)": 0.004,
        "Plastic Shopping Bag (Thin)": 0.015,
        "Plastic Shopping Bag (Thick/Reusable)": 0.033,
        "Paper Shopping Bag": 0.055,
        "Cotton Tote Bag (per use)": 0.002,
        "Cardboard Pizza Box": 0.150,
        "Styrofoam Takeout Container": 0.060,
        "Plastic Clamshell Container": 0.120,
        "Compostable Takeout Container": 0.030,
        "Aluminum Foil (1 meter)": 0.025,
        "Cling Film / Plastic Wrap (1 meter)": 0.012
    },

    "🍔 Food & Diet (Base Units / Average Portions)": {
        "Beef/Mutton Portion (100g)": 7.70,
        "Pork Portion (100g)": 1.80,
        "Chicken Portion (100g)": 1.36,
        "Turkey Portion (100g)": 1.60,
        "Fish (Farmed, 100g)": 1.80,
        "Fish (Wild-caught, 100g)": 0.50,
        "Prawns/Shrimp (100g)": 2.50,
        "Egg (Single)": 0.20,
        "Cheese (50g serving)": 0.65,
        "Cow's Milk (1 Glass / 250ml)": 0.80,
        "Soy Milk (1 Glass / 250ml)": 0.25,
        "Oat Milk (1 Glass / 250ml)": 0.22,
        "Almond Milk (1 Glass / 250ml)": 0.18,
        "Butter (20g serving)": 0.23,
        "Tofu (100g serving)": 0.20,
        "Rice (1 serving, dry)": 0.33,
        "Pasta (1 serving, dry)": 0.12,
        "Bread (1 slice)": 0.05,
        "Lentils/Dal (1 serving, dry)": 0.07,
        "Potato (1 large)": 0.05,
        "Tomato (100g, Locally grown)": 0.04,
        "Tomato (100g, Greenhouse)": 0.25,
        "Apple/Banana/Orange (1 piece)": 0.04,
        "Avocado (1 piece, imported)": 0.20,
        "Fast Food Burger (Beef)": 3.50,
        "Fast Food Burger (Chicken)": 2.00,
        "Fast Food Burger (Plant-based)": 1.00,
        "Chocolate Bar (Milk, 50g)": 0.90,
        "Chocolate Bar (Dark, 50g)": 0.45,
        "Potato Chips (50g bag)": 0.16,
        "Coffee (Black, 1 cup)": 0.21,
        "Coffee (Latte with Cow's Milk)": 0.55,
        "Tea (Black/Green, 1 cup)": 0.05,
        "Tea (Milk Tea/Chai, 1 cup)": 0.30,
        "Beer (1 Pint, Local)": 0.50,
        "Wine (1 Glass, Imported)": 0.40,
        "Food waste thrown in trash (per 1 kg)": 2.50,
        "Food waste composted (per 1 kg)": 0.20
    },

    "🚶 Mobility: Active & Vertical (Per Floor/Km)": {
        "Walked (per 1 km)": 0.00,
        "Bicycle / Manual Scooter (per 1 km)": 0.00,
        "Staircase - Going UP (per 1 floor)": 0.00,
        "Staircase - Going DOWN (per 1 floor)": 0.00,
        "Elevator - Going UP (per 1 floor)": 0.015,
        "Elevator - Going DOWN (per 1 floor)": 0.010,
        "Escalator - Going UP (per 1 floor)": 0.010,
        "Escalator - Going DOWN (per 1 floor)": 0.005
    },

    "🚗 Mobility: Transit (Per Km)": {
        "Electric Scooter / Hoverboard (per 1 km)": 0.030,
        "Petrol Car - Solo driving (per 1 km)": 0.192,
        "Diesel Car - Solo driving (per 1 km)": 0.171,
        "Hybrid Car - Solo driving (per 1 km)": 0.110,
        "Electric Vehicle - Solo (per 1 km)": 0.053,
        "Carpool / Cab (Petrol, per 1 km per person)": 0.080,
        "Carpool / Cab (EV, per 1 km per person)": 0.025,
        "Motorcycle / Petrol Scooter (per 1 km)": 0.103,
        "Auto Rickshaw / Tuk-Tuk (per 1 km)": 0.070,
        "Public Bus (Standard Diesel, per 1 km)": 0.105,
        "Public Bus (Electric, per 1 km)": 0.040,
        "Metro / Subway / Light Rail (per 1 km)": 0.041,
        "National Train (per 1 km)": 0.035,
        "Domestic Flight (per 1 km)": 0.145,
        "International Flight (per 1 km)": 0.115,
        "Ferry / Boat (per 1 km)": 0.120
    },

    "⚡ Energy & HVAC (Per Hour)": {
        "Air Conditioner (< 1 Ton, per 1 hour)": 0.60,
        "Air Conditioner (1.5 Ton, per 1 hour)": 0.85,
        "Air Conditioner (2 Ton+, per 1 hour)": 1.20,
        "Electric Space Heater (per 1 hour)": 0.70,
        "Ceiling Fan (per 1 hour)": 0.03,
        "Table/Pedestal Fan (per 1 hour)": 0.02,
        "Incandescent Bulb (60W, per 1 hour)": 0.025,
        "CFL Bulb (15W, per 1 hour)": 0.006,
        "LED Bulb (9W, per 1 hour)": 0.003,
        "Fluorescent Tube Light (per 1 hour)": 0.015,
        "Laptop charging/use (per 1 hour)": 0.020,
        "Desktop PC + Monitor (per 1 hour)": 0.080,
        "High-End Gaming PC / Console (per 1 hour)": 0.250,
        "TV - LED 42 inch (per 1 hour)": 0.040,
        "Streaming Video/Netflix (Standard Def, per 1 hour)": 0.030,
        "Streaming Video/Netflix (4K/HD, per 1 hour)": 0.080,
        "Zoom / Video Call (per 1 hour)": 0.150,
        "Audio Streaming / Spotify (per 1 hour)": 0.010,
        "Wi-Fi Router (running per 1 hour)": 0.002
    },

    "🍳 Home, Kitchen & Hygiene (Base Units)": {
        "Microwave (per 1 min)": 0.007,
        "Electric Kettle (Boiling 1L water)": 0.070,
        "Electric Stove/Hob (per 15 mins)": 0.120,
        "Gas Stove/Hob (per 15 mins)": 0.150,
        "Electric Oven (per 15 mins)": 0.200,
        "Toaster (per 2 slices)": 0.010,
        "Refrigerator (Standard, per 24 hours)": 1.100,
        "Dishwasher (Standard cycle)": 0.600,
        "Washing Machine - Cold wash 20°C (per load)": 0.300,
        "Washing Machine - Hot wash 60°C (per load)": 0.900,
        "Clothes Dryer (per 10 mins)": 0.300,
        "Air-drying clothes on rack (per load)": 0.000,
        "Ironing Clothes (per 10 mins)": 0.080,
        "Vacuum Cleaning (per 10 mins)": 0.065,
        "Cold Water Shower (per 1 min)": 0.010,
        "Warm Water Shower (per 1 min)": 0.080,
        "Hot Water Shower (Electric heater, per 1 min)": 0.120,
        "Hot Bath (Full tub)": 2.500,
        "Toilet Flush (Standard - 9 Liters)": 0.003,
        "Toilet Flush (Dual/Eco - 4 Liters)": 0.001,
        "Electric Hand Dryer (per use)": 0.010,
        "Paper Towel (per sheet)": 0.010
    },

    "🎓 Bioscience Lab & Campus (Base Units)": {
        "Printing - B&W Single-Sided (per page)": 0.005,
        "Printing - Color Single-Sided (per page)": 0.007,
        "Wooden Pencil (entire lifespan)": 0.020,
        "Plastic Pen (entire lifespan)": 0.040,
        "Paper Notebook (100 pages)": 0.500,
        "Lab: Fume Hood (running per 1 hour)": 0.350,
        "Lab: Biosafety Cabinet (running per 1 hour)": 0.400,
        "Lab: Bunsen Burner (per 10 mins)": 0.033,
        "Lab: Microscope (per 1 hour)": 0.010,
        "Lab: Centrifuge (per 10 mins)": 0.030,
        "Lab: Autoclave (per sterilization cycle)": 1.500,
        "Lab: PCR Machine / Thermal Cycler (per 1 hour)": 0.080,
        "Lab: Ultra-low temp Freezer -80°C (per 24 hours)": 1.200,
        "Lab: Standard Refrigerator 4°C (per 24 hours)": 0.250,
        "Lab: Plastic Petri Dish (Single-use)": 0.035,
        "Lab: Glass Petri Dish (Reusable, per use)": 0.002,
        "Lab: Box of 96 Plastic Pipette Tips": 0.450,
        "Lab: Nitrile Gloves (per pair, disposal included)": 0.060
    },

    "🛍️ Shopping & Lifestyle (Manufacturing Footprints)": {
        "T-Shirt (Cotton)": 4.500,
        "T-Shirt (Synthetic/Polyester)": 5.500,
        "Jeans (Denim)": 15.000,
        "Sweater (Wool)": 12.000,
        "Jacket (Winter/Puffer)": 30.000,
        "Thrifted / Second-hand Clothing item": 0.100,
        "Sneakers / Athletic Shoes": 14.000,
        "Leather Shoes": 20.000,
        "Hardcover Book": 2.500,
        "Paperback Book": 1.000,
        "Smartphone (Manufacturing footprint)": 55.000,
        "Laptop (Manufacturing footprint)": 250.000,
        "Smartwatch / Fitness Tracker": 15.000,
        "Headphones (Over-ear)": 10.000,
        "Earbuds (Wireless)": 4.000,
        "Shampoo (Plastic Bottle, 400ml)": 0.600,
        "Bar Soap (Paper wrapped)": 0.150,
        "Toothpaste (Plastic tube)": 0.350,
        "Deodorant (Aerosol spray)": 0.700,
        "Deodorant (Roll-on / Stick)": 0.300,
        "Detergent (Liquid, 1L plastic bottle)": 1.100,
        "Detergent (Powder, cardboard box)": 0.400,
        "Hotel Stay (per night, standard room)": 15.000,
        "Gym Session (per 1 hour)": 1.200,
        "Cut Flowers (Imported, 1 bunch)": 32.000,
        "Cut Flowers (Local, 1 bunch)": 2.500
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
