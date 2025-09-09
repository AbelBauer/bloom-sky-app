import time, datetime, re, sys
from googlemaps.exceptions import HTTPError
import requests
from rich.console import Console
from rich import print
from rich.panel import Panel

from recommendations import get_recommendation
from display_weather_table import print_table
from gmaps_package import get_geocode, get_current_weather, get_extended_forecast
from gmaps_pollen import get_pollen
from garden_care_guide import display_care_info, display_care_description
from plant_vs_weather import weather_plant

# HELPERS
def ask_retry():
    choice = input("\nWould you like to try again? yes [Y], or no [N]?  ➤  ").lower().strip()
    return choice == "y"

def add_more_plants():
    while True:
        user_choice = input("\nWould you like to see more plants?: yes [Y] or no [N] to exit the garden?  ➤  ").lower().strip()
        valid_choices = ["y", "n"] 
        if user_choice in valid_choices:
                return user_choice
        else:
            time.sleep(0.5)
            print("Invalid choice. Please, try again.")
            time.sleep(0.5)
            continue

def ask_careInfo():
    while True:
        user_choice = input("\nWould you like to see detailed care information?: yes [Y], no [N], exit the garden [E]?  ➤  ").lower().strip()
        valid_choices = ["y", "n", "e"]
        if user_choice in valid_choices:
            return user_choice
        else:
            time.sleep(0.5)
            print("Invalid choice. Please, try again.")
            time.sleep(0.5)
            continue

def display_custom_forecast(location, latitude, longitude):
        
    #1 fetch data from Google Maps API
    try:
        is_day, temp, description, humidity, rain_prob = get_current_weather(latitude, longitude)
    except (TypeError, IndexError, ValueError, requests.RequestException, HTTPError):
        print(f"Error fetching current weather data for '{location}' location.")
        raise

    #2 Fetch pollen data from Google Maps pollen API
    try:
        grass, weed, tree = get_pollen(latitude, longitude)
    except (TypeError, IndexError, ValueError, requests.RequestException, HTTPError):
        print(f"Error fetching pollen data for '{location}' location.")
        raise

    #3 Display today's forecast for chosen location.

    print_table(location, is_day, temp, description, rain_prob, humidity)

    #4 Display recommendations

    print(Panel.fit(f"{get_recommendation(is_day, temp, rain_prob, humidity, grass, tree, weed)}"))

def get_location():
    while True:
        try:
            location = prompt_location()
            latitude, longitude = get_geocode(location)
            if valid_coordinates(latitude, longitude):
                return location.upper(), latitude, longitude
            else:
                time.sleep(0.5)
                print(f"Error: Invalid geocoding coordinates for provided location.\n")
                if ask_retry():
                    continue
                else:
                    raise IndexError #return get_location(location)
        except (IndexError, ValueError, HTTPError) as e:
            print(f"Error: Could not resolve geocoding coordinates for provided location. {e}\n")
            if ask_retry():
                continue
            else:
                break

def main_menu():
    while True:
        console = Console()
        print("")
        console.rule("[bold red]MAIN MENU", align="left")
        console.print("\n  [bold cyan][E][/bold cyan] Check extended forecast for 'HOME' location.")
        console.print("  [bold cyan][L][/bold cyan] Type in custom location.")
        console.print("  [bold cyan][G][/bold cyan] Enter virtual garden.")
        console.print("  [bold cyan][Q][/bold cyan] Quit.")
        choice = input("➤  ").strip().lower()
        valid_choices = ["e", "l", "g", "q"]
        if choice in valid_choices:
            return choice
        else:
            time.sleep(0.5)
            print("\nInvalid choice. Please, try again.")
            time.sleep(0.5)
            continue
    
def not_supported_locations(regions):
    message = f"⚠️  [red]Heads-up: Weather and pollen data isn't currently available for a few regions, including: {regions.title()}."
    return Panel.fit(message)

def load_restr_locations(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        # split by comma, strip quotes and whitespace
        return sorted([name.strip().strip('"') for name in content.split(",") if name.strip()])

def location_subMenu():
    console = Console()
    while True:
        console.print("\n  [bold cyan][E][/bold cyan] - Check this location extended forecast")
        console.print("  [bold cyan][M][/bold cyan] - Main Menu")
        choice = input("➤  ").strip().lower()
        valid_choice = ["e", "m"]
        if choice in valid_choice:
            return choice
        else:
            time.sleep(0.5)
            print("\nInvalid choice. Please, try again.")
            time.sleep(0.5)
            continue

def confirm_location(location):
    console = Console()
    while True:
        console.print(f"\nIs your garden located in [bold red]{location.upper()}[/bold red]?")
        choice = input(f"Press [C] to confirm or [L] to enter a new location: ➤ ").lower().strip()
        if choice == "c":
           return location
        elif choice == "l":
            custom_location = prompt_location()
            return custom_location
        else:
            time.sleep(1)
            print("\nInvalid choice. Please, try again.\n")
            time.sleep(1)
            continue

def prompt_plants(location):
    console = Console()
    while True:
        soil_choice = prompt_soilType() # Prompt user for soil type. This is a global garden parameter.  
        user_plant= input("\nType in here the name of a plant and/or tree in your garden. Use vernacular, common or scientific name: ➤  ").lower().strip() # Ask the user for plant name.         
        intro_plantGrowth() # Introduce soil choice to user.
        growth_stage = prompt_growthStage() # Ask the user for the plant growth stage.
        plant_name, plant_id, watering, sunlight = display_care_info(user_plant, growth_stage, soil_choice) # Display table and recommendations.
        #today_forecast, tomorrow_forecast = get_forecast(location)
        console.print(Panel.fit(weather_plant(location=location, watering=watering, sunlight=sunlight)))

        retry_choice = ask_careInfo()
        print("")
        if retry_choice == "y":
            display_care_description(plant_id, plant_name) # Display detailed care information from perenual.com.
            add_plants_choice = add_more_plants() # Ask the user for more plants.
            if add_plants_choice == "y":
                continue
            elif add_plants_choice == "n":
                break
        elif retry_choice == "n":
            continue
        else:
            break 
        
def prompt_soilType() -> str: # Prompt the user for soil type. Return soil type.
    console = Console()
    while True:
        console.print("\nKnowing whether your soil type is [bold green]CLAY[/bold green], [bold green]SAND[/bold green], [bold green]SILT[/bold green], [bold green]LOAM[/bold green], [bold green]PEAT[/bold green] or [bold green]CHALK[/bold green] " \
        "will help you choose the right plants for your garden and maintain them in good health. (Source: https://www.rhs.org.uk/)")
        console.print("\nType in your garden's soil type here. Press [bold cyan][S][/bold cyan] to skip or [bold cyan][E][/bold cyan] to exit the program:  ")
        soil_choice = input(" ➤ ").lower().strip()
        valid_choices= ["clay", "sand", "silt", "loam", "peat", "chalk"]
        if soil_choice in valid_choices:
            return soil_choice
        elif soil_choice == "s":
            return None
        elif soil_choice == "e":
            sys.exit()
        else:
            time.sleep(0.5)
            print("")
            print("Invalid option. Please, try again.")
            time.sleep(1)
            continue

def intro_plantGrowth(): # Intro to plants growth stages
    console = Console()
    console.print("\nThere are many ways that the grower can influence the life cycle of a plant; " \
    "forcing it to live longer, look younger or more attractive. The growth stages of plants can be define in seven stages: " \
    "[bold green]SEED[/bold green], [bold green]JUVENILE[/bold green], [bold green]ADULT[/bold green], [bold green]FLOWERING[/bold green], " \
    "[bold green]FRUITING[/bold green], [bold green]SENESCENCE[/bold green] and [bold white]DEATH[/bold white]. (Source: https://leafylearning.co.uk/)")
    
def prompt_growthStage(): # Prompt the user for plant growth stage. Return growth stage. 
    #Find a way to optionally return growth without consequences to get_recommendations() function.
    console= Console()
    while True:
        console.print("\nType in your plant growth stage. Press [bold cyan][S][/bold cyan] to skip or [bold cyan][E][/bold cyan] to exit the program:")
        growth_choice= input(" ➤ ").lower().strip()
        valid_choices= ["seed", "juvenile", "adult", "flowering", "fruiting", "senescence"]
        if growth_choice in valid_choices:
            return growth_choice
        elif growth_choice == "s":
            return None
        else:
            print("")
            time.sleep(0.5)
            print("Invalid option. Please, try again.")
            time.sleep(1)
            continue

def plants_subMenu():
    while True:
        console = Console()
        print("")
        console.rule("[bold red]GARDEN MENU", align="left")
        console.print("\n [bold cyan][I][/bold cyan] - Display [red]Plant Care Information[/red]")
        console.print(" [bold cyan][A][/bold cyan] - Add more plants")
        console.print(" [bold cyan][M][/bold cyan] - [bold green]Main Menu[/bold green]")
        choice = input("➤ ").lower().strip()
        print("")
        valid_choices = ["i", "a", "m", "d"]
        if choice in valid_choices:
            return choice
        else:
            print("")
            time.sleep(0.5)
            print("\nInvalid option. Please, try again.")
            time.sleep(0.5)
            continue
        
def prompt_location():
        for _ in range(3):
            try:
                print("")
                location = input("Please, type your location here (e.g., Paris, France): ").title().strip()
                print("")
                location = validate_input(location)
                return location
            except ValueError:
                print("Input not recognized. Try please format 'City, Country' (e.g., Paris, France).")
                continue
            except HTTPError:
                print(f"Sorry, data for that region isn't available right now.")
                continue
        print("\nNo worries! Skipping your location forecast for now...")
        return

# Helper to format datetime like "July 30th, 12 AM". Currently not in use.
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

# Load the restricted locations (9 Countries, China: 34 Divisions, Cuba: 15 Provinces + 1 Special Municipality, Iran: 31 Provinces,
# Japan: 47 Prefectures, North Korea: 9 Provinces + 3 Cities, South Korea: 9 Provinces + 7 Cities, 
# Syria: 14 Governorates and Vietnam: 58 Provinces + 5 Municipalities ) from .txt in local disk.
RESTRICTED_SET = load_restr_locations("gmaps_restricted_locations.txt") #----{location.title() for location in RESTRICTED_LOCATIONS}---- for when i used to have the locations list inside Helpers. Dont remove in case the last modifications break the program.

# Regex for "City, Country" format
LOCATION_PATTERN = re.compile(r"^([A-Za-zÀ-ÿ\s\-']+),\s*([A-Za-zÀ-ÿ\s\-']+)$", re.IGNORECASE)

def validate_input(location: str) -> str:
    # Normalize comma spacing
    location = re.sub(r"\s*,\s*", ", ", location.strip())
    match = LOCATION_PATTERN.match(location)
    if not match:
        raise ValueError("Invalid input. Please use the format 'City, Country' (e.g., Paris, France).")

    city, region = match.groups()
    city = city.strip()
    region = region.strip().title()

    if region in RESTRICTED_SET:
        raise HTTPError(f"Sorry, data for location '{location}' isn't available right now.")

    return location

# Display welcome message to start the app.
def welcome(description):
    console = Console()
    print("")
    print("")
    console.rule("[bold red]WELCOME TO BLOOM & SKY APP", align="left")
    print(description)
    time.sleep(0.6)