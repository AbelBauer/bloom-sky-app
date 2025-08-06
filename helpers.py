import time, datetime, re, sys
from geo_convert import get_coordinates

# HELPERS

def validate_input(place):
    pattern =r"^([A-Za-zÀ-ÿ\s\-']+), ([A-Za-zÀ-ÿ\s\-']+)$"
    if re.search(pattern, place):
        return place
    else:
        time.sleep(0.5)
        raise ValueError('Input not recognized. Try please "city, country" format [e.g., Madrid, Spain].')
        
def user_input():
    while True:       
        print("\n  [L] Type in your location.")
        print("  [P] Type in your garden plants.")
        print("  [Q] Quit")
        choice = input("➤ ").strip().lower()
        if choice == "l":
            for _ in range(3):
                try:
                    location = input("\nPlease, type your location here (e.g. Madrid, Spain): ").title().strip()
                    location = validate_input(location)
                    if location:
                        return location # Returns a LOCATION to plug into the get_location() in geo_convert.py
                except ValueError:
                    print('Input not recognized. Try please "city, country" format [e.g., Madrid, Spain].')
                    continue           
            print("No worries! Skipping your location forecast for now...")
        # elif choice == "p": Plants logic still to be implemented. Waiting for API
        elif choice == "q":
            sys.exit("\nGood bye. Have a nice day!")
        else:
            time.sleep(1)
            print("\nInvalid option. Please, try again.")
            continue

def prompt_location():
    while True:
        location = user_input()
        try:
            latitude, longitude = get_coordinates(location)
            if valid_coordinates(latitude, longitude):
                return location, latitude, longitude
            else:
                time.sleep(1)
                print(f"(Could not find coordinates for '{location}')")
                if ask_retry():
                    continue
                else:
                    return user_input(), None, None
        except ValueError as e:
            print(f"(Error handling location '{location}': {e})")
            if ask_retry():
                continue
            else:
                return user_input(), None, None

def time_to_emoji(value): # Convert is_day to emoji
    if value == False:
        return "🌘"
    else:
        return "🌞"
    
def daytime_to_bool(value): # Convert is_day to bool
    if value == 1.0:
        return True
    return False

# Helper to format datetime like "July 30th, 12 AM"
def readable_datetime(ts):
    dt = datetime.fromtimestamp(ts)
    day = dt.day
    # Add ordinal suffix
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return dt.strftime(f"%B {day}{suffix}, %I %p").lstrip("0")  # Removes leading zero in hour

def get_recommendation(is_daytime, temp, rain_prob, humidity, grass_pollen_risk, tree_pollen_risk, weed_pollen_risk):
    
    recommendation = ""

    # Pollen risk level variables
    grass = grass_pollen_risk.lower()
    tree = tree_pollen_risk.lower()
    weed = weed_pollen_risk.lower()


    # Time of Day
    if not is_daytime:
        recommendation += "🕚➱🌃 Night owl mode: dim lights, indoor chill. Cozy up with blanket-movie combo.\n"
    else:
        recommendation += "🕗➱🌅 The day's in full swing. Soak it up your way!\n"

    # Temperature
    if 28 <= temp <= 37 and humidity < 80 and rain_prob < 25 and is_daytime:
        recommendation += "☀️  Beach vibes activated! Rock your swimwear, flip-flops, and sunglasses.\n"
    elif temp > 37:
        recommendation += "🥵 It's a desert out there. Hydrate like it's your job!\n"
    elif 20 <= temp <= 28 and rain_prob < 50:
        if is_daytime:
            recommendation += "😎 Perfect time for a park stroll or café terrace. You are good to go!\n"
        else:
            recommendation += "🍽️  Warm evening out there. Perfect time for a dinner out or catching a late film.\n"
    elif 10 <= temp < 20 and is_daytime:
        recommendation += "🧥 Light layers recommended, it's brisk but charming. Channel that autumn wanderer vibe.\n"
    elif temp < 10 and is_daytime:
        recommendation += "🥶 Stay layered and warm. Consider indoor fun and skip the frostbite.\n"

    # Rain
    if rain_prob >= 60 and temp > 15:
        recommendation += "☔ Umbrella alert! Waterproof vibes only.\n"
    elif rain_prob >= 40:
        recommendation += "🌧️  Light rain possible. Bring a hoodie just in case.\n"
    elif 25 < rain_prob < 40:
        recommendation += "☁️  Grey skies: maybe rain, probably not. Trust issues remain.\n"
    
    # Humidity
    if humidity >= 80:
        recommendation += "💦 Sticky alert! Hydrate well and skip the heavy fabrics.\n"
    elif humidity < 30:
        recommendation += "💨 Dry air today. Moisturize and sip that water.\n"
    elif 30 < humidity < 80 and is_daytime:
        if temp < 32:
            recommendation += "⛹️  Comfortable humidity today. Great for any activity!\n"
        else:
            recommendation += "🥵 Step out and it's instant bake mode. Shade up, hydrate hard!\n"

    # Pollen Alert
    # Analyze grass pollen
    if grass == "high":
        recommendation += "🤧🌾 Grass pollen is high today. Mask up or stay indoors!\n"
    elif grass == "medium":
        recommendation += "🌾 Moderate grass pollen levels. Keep allergy meds handy.\n"
    # if low risk no need to recommend. 
    
    # Analyze tree pollen
    if tree == "high":
        recommendation += "🤧🌳 Tree pollen is spiking. Avoid parks or wooded areas if you're sensitive.\n"
    elif tree == "medium":
        recommendation += "🌳 Moderate tree pollen. Check symptoms and avoid peak hours.\n"
    # if low risk no need to recommend. 
    
    # Analyze weed pollen
    if weed == "high":
        recommendation += "🤧🌿 Weed pollen levels are high. Keep windows closed and limit outdoor exposure.\n"
    elif weed == "medium":
        recommendation += "🌿 Moderate weed pollen. Some discomfort possible if you're allergic.\n"
    # if low risk no need to recommend. 
    
    return recommendation

def valid_coordinates(lat, lon):
    return lat is not None and lon is not None

def ask_retry():
    choice = input("\nWould you like to try again? ➤ yes [Y], or no [N]?  ➤ ").lower()
    return choice == "y"