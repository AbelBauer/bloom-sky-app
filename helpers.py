import time, datetime, re, sys
import googlemaps
from rich.console import Console #type: ignore
from rich import print
from rich.panel import Panel
from display_weather_table import print_table
from gmaps_package import get_geocode, extended_forecast, get_current_weather
from gmaps_pollen import get_pollen

# HELPERS

def ask_retry():
    choice = input("\nWould you like to try again? ➤ yes [Y], or no [N]?  ➤ ").lower()
    return choice == "y"

def custom_location(location, latitude, longitude):
        
    #1 fetch data from Google Maps API

    is_day, temp, description, humidity, rain_prob = get_current_weather(latitude, longitude)

    #2 Fetch pollen data from Google Maps pollen API

    grass, weed, tree = get_pollen(latitude, longitude)

    #3 Display today's forecast for chosen location.

    print_table(location, is_day, temp, description, rain_prob, humidity)

    #4 Display recommendations

    print(Panel.fit(f"{get_recommendation(is_day, temp, rain_prob, humidity, grass, tree, weed)}"))

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
        except (IndexError, ValueError, googlemaps.exceptions.HTTPError):
            print(f"Location '{location}' not recognized.")
            if ask_retry():
                continue
            else:
                break
            
def get_recommendation(is_daytime, temp, rain_prob, humidity, grass_pollen_risk, tree_pollen_risk, weed_pollen_risk) -> str:
    
    recommendation = ""

    # Pollen risk level variables
    grass = grass_pollen_risk.lower()
    tree = tree_pollen_risk.lower()
    weed = weed_pollen_risk.lower()

    high = ["high", "very high"]
    moderate = ["moderate"]
    #low = ["low", "very low"]


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
    if grass in high:
        recommendation += "\n🔴 ➜ 🌾 Grass pollen is high today. Mask up or stay indoors!\n"
    elif grass in moderate:
        recommendation += "\n🟠 ➜ 🌾 Moderate grass pollen levels. Keep allergy meds handy.\n"
    else:
        recommendation += "\n🟢 ➜ 🌾 Grass pollen levels are low right now. If you're super sensitive, there's a good chance you'll feel it today.\n"
    
    # Analyze tree pollen
    if tree in high:
        recommendation += "🔴 ➜ 🌳 Tree pollen is spiking. Avoid parks or wooded areas if you're sensitive.\n"
    elif tree in moderate:
        recommendation += "🟠 ➜ 🌳 Moderate tree pollen. Check symptoms and avoid peak hours.\n"
    else:
        recommendation += "🟢 ➜ 🌳 Trees pollen levels are low right now. If you're super sensitive, there's a good chance you'll feel it today.\n"
    
    # Analyze weed pollen
    if weed in high:
        recommendation += "🔴 ➜ 🌿 Weed pollen levels are high. Keep windows closed and limit outdoor exposure."
    elif weed in moderate:
        recommendation += "🟠 ➜ 🌿 Moderate weed pollen. Some discomfort possible if you're allergic."
    else:
        recommendation += "🟢 ➜ 🌿 Weed pollen levels are low right now. If you're super sensitive, there's a good chance you'll feel it today."
   
    return recommendation

def is_plants(choice):
    return choice == "p"

def main_menu():
    while True:
        console = Console()
        print("")
        console.rule("[bold red]MAIN MENU", align="left")
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
            print(not_supported_locations())

            try:
                location, latitude, longitude = get_location()
            except TypeError:
                print("Returning to Main Menu...")
                continue

            print("")
            custom_location(location, latitude, longitude)
            print("\n  [E] Check this location extended forecast")
            print("  [M] Main menu")
            custom_choice = input("➤ ").strip().lower()
            while True:
                if custom_choice == "e":
                    print("")
                    extended_forecast(location, latitude, longitude)
                    break
                elif custom_choice == "m":
                    break
                else:
                    print("Invalid option")
                    time.sleep(1)
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
            time.sleep(1)
            continue

def not_supported_locations():
    return Panel.fit("⚠️  [red]Heads-up: Weather and pollen data isn't currently available for a few regions, including China, Cuba, Iran, Japan, North Korea, South Korea, Syria, and Vietnam.")

def prompt_plants():
    time.sleep(1)
    console = Console()
    print("")
    console.rule("[bold red]WELCOME TO YOUR VIRTUAL GARDEN", align="left")
    print("Your garden is more than decoration, it's a living ecosystem. Every plant and tree you care for contributes to cleaner air, biodiversity, and a sense of peace and beauty. Taking good care of them is great responsability and lots of fun, too. Let me help you in doing so!\n")

    plants = []
    
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
    
def prompt_location():
        for _ in range(3):
            try:
                print("")
                location = input("Please, type your location here (e.g. Madrid, Spain): ").title().strip()
                location = validate_input(location)
                if location:
                    return location
                else:
                    continue
            except ValueError as v:
                print(f"{v}")
                continue           
        print("No worries! Skipping your location forecast for now...")


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



def valid_coordinates(lat, lon):
    return lat is not None and lon is not None

def validate_input(place):
    restricted_countries = [
        "China", "Cuba", "Iran", "Japan", "North Korea",
        "South Korea", "Syria", "Vietnam",
    ]
    pattern1 = re.compile(r"\b(" + "|".join(restricted_countries) + r")\b", re.IGNORECASE)
    pattern2 = re.compile(r"^([A-Za-zÀ-ÿ\s\-']+), ([A-Za-zÀ-ÿ\s\-']+)$", re.IGNORECASE)

    if re.search(pattern1, place):
        time.sleep(0.5)
        raise ValueError("Sorry, data for that location isn't available right now.")

    if not re.search(pattern2, place):
        time.sleep(0.5)
        raise ValueError("Input not recognized. Try please 'city, country' format [e.g., Paris, France].")
        
    return place
