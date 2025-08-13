import time, datetime, re, sys
from rich.console import Console #type: ignore
from rich import print
from rich.panel import Panel
from pollen import get_pollen
from display_weather_table import print_table
from gmaps_package import get_geocode, extended_forecast, get_current_weather

# HELPERS

def is_plants(choice):
    return choice == "p"

def prompt_plants():
    console = Console()
    print("")
    console.rule("[bold red]WELCOME TO YOUR VIRTUAL GARDEN", align="left")
    print("")

    plants = []
    time.sleep(1)
    print("""
=================================================================================
          
            Your garden is more than decoration, it's a living ecosystem.
    Every plant and tree you care for contributes to cleaner air, biodiversity,
and a sense of peace and beauty. Taking good care of them is great responsability
            and lots of fun, too. Let me help you in doing so!
          
=================================================================================
    """)

    while True:
        user_input= input("\nList the plants and/or trees in your garden (separate names with commas, e.g. fern, roses, etc): ").lower().strip()
        new_plants = [plant.strip().lower() for plant in user_input.split(",") if plant.strip()] # takes raw user input and transforms it into a clean, lowercase list of plant names.
        plants.extend(new_plants)
        print("\nYour garden currently includes: \n")

        for i, plant in enumerate(plants, 1): # Numbered list. Makes it easy to read and visually organized. 
            print(f"{i}. {plant.capitalize()}")

        print("\n [I] Display care information")
        print(" [A] Add more plants")
        print(" [Q] Quit")
        choice = input("➤ ").lower().strip()
        if choice == "i":
            ... # WIP 
        elif choice == "q":
            print("\nThanks for creating a virtual garden with me!\n")
        elif choice == "a":
            continue
        else:
            print("\nInvalid option")
            continue
        return plants
    
def validate_input(place):
    pattern =r"^([A-Za-zÀ-ÿ\s\-']+), ([A-Za-zÀ-ÿ\s\-']+)$"
    if re.search(pattern, place):
        return place
    else:
        time.sleep(0.5)
        raise ValueError('Input not recognized. Try please "city, country" format [e.g., Madrid, Spain].')
        
def prompt_location():
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

def get_location():
    while True:
        location = prompt_location()
        try:
            latitude, longitude = get_geocode(location)
            if valid_coordinates(latitude, longitude):
                return location, latitude, longitude
            else:
                time.sleep(1)
                print(f"(Could not find coordinates for '{location}')")
                if ask_retry():
                    continue
                else:
                    return get_location(), None, None
        except ValueError as e:
            print(f"(Error handling location '{location}': {e})")
            if ask_retry():
                continue
            else:
                return get_location(), None, None


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

def get_recommendation(is_daytime, temp, rain_prob, humidity, grass_pollen_risk, tree_pollen_risk, weed_pollen_risk) -> str:
    
    recommendation = ""

    # Pollen risk level variables
    grass = grass_pollen_risk.lower()
    tree = tree_pollen_risk.lower()
    weed = weed_pollen_risk.lower()


    # Time of Day
    if not is_daytime:
        recommendation += "🕚➱🌃 Night owl mode: dim lights, indoor chill. Cozy up with blanket-movie combo. Or....sweat dreams 💤💤\n"
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
    elif 20 < rain_prob < 40:
        recommendation += "☁️  Grey skies: maybe rain, probably not. Trust issues remain.\n"
    elif rain_prob < 20 and is_daytime:
        recommendation += "🌞 Sun's out. Perfect day to bloom and roam!\n"
    
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
    elif grass == "moderate":
        recommendation += "🌾 Moderate grass pollen levels. Keep allergy meds handy.\n"
    # if low risk no need to recommend. 
    
    # Analyze tree pollen
    if tree == "high":
        recommendation += "🤧🌳 Tree pollen is spiking. Avoid parks or wooded areas if you're sensitive.\n"
    elif tree == "moderate":
        recommendation += "🌳 Moderate tree pollen. Check symptoms and avoid peak hours.\n"
    # if low risk no need to recommend. 
    
    # Analyze weed pollen
    if weed == "high":
        recommendation += "🤧🌿 Weed pollen levels are high. Keep windows closed and limit outdoor exposure.\n"
    elif weed == "moderate":
        recommendation += "🌿 Moderate weed pollen. Some discomfort possible if you're allergic.\n"
    # if low risk no need to recommend. 
    
    return recommendation

def valid_coordinates(lat, lon):
    return lat is not None and lon is not None

def ask_retry():
    choice = input("\nWould you like to try again? ➤ yes [Y], or no [N]?  ➤ ").lower()
    return choice == "y"

def custom_location(location, latitude, longitude):
        
    #1 fetch data from Google Maps API

    is_day, temp, description, humidity, rain_prob = get_current_weather(latitude, longitude)

    #2 Fetch pollen data from getambee.com API. WIP....Migrate to Google Maps pollen API

    grass, tree, weed = get_pollen(location)

    #3 Display today's forecast for chosen location.

    print_table(location, is_day, temp, description, rain_prob, humidity)

    #4 Display recommendations

    print(Panel(f"\n{get_recommendation(is_day, temp, rain_prob, humidity, grass, tree, weed)}"))


def main_menu():
    while True:
        console = Console()
        print("")
        console.rule("[bold red]MAIN MENU", align="left")
        print("")
        print("\n  [E] Check extended forecast for 'HOME' location.")
        print("  [L] Type in custom location.")
        print("  [G] Enter virtual garden.")
        print("  [Q] Quit.")
        choice = input("➤ ").strip().lower()

        if choice == "q":
            print("")
            console.rule("[bold red]GOOD BYE!", align="left")
            sys.exit()
        elif choice == "l":
            print("")
            location, latitude, longitude = get_location()
            custom_location(location, latitude, longitude)
            print("\n  [E] Check your location extended forecast")
            print("  [Q] Quit")
            custom_choice = input("➤ ").strip().lower()
            while True:
                if custom_choice == "e":
                    print("")
                    extended_forecast(location, latitude, longitude)
                    break
                elif custom_choice == "q":
                    break
                else:
                    print("Invalid option")
                    continue
            continue
        elif choice == "e":
            print("")
            extended_forecast(location="Statenkwartier, Zuid Holland", lat=52.0945228, long=4.279590499999999) # default for 'Home' location
        elif choice == "g":
            prompt_plants()
            continue
        else:
            print("\nInvalid option")
            continue