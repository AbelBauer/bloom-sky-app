'''
Bloom and Sky - Interactive Forecast & Garden Advisor

This module serves as the interactive entry point for the Bloom and Sky ecosystem. It orchestrates weather forecasting, pollen analysis, 
plant care recommendations, and user interaction through a rich command-line interface. Designed for personal use, it integrates multiple 
submodules to deliver a responsive and informative experience tailored to gardeners, nature enthusiasts, and weather-aware users.

Core Responsibilities:
----------------------
- Prompt users for location input and validate geocoding coordinates.
- Display current weather and pollen conditions using Google Maps APIs.
- Generate actionable recommendations based on environmental factors.
- Offer extended forecasts and plant care guidance via a virtual garden interface.
- Handle unsupported regions gracefully and provide retry options.

Key Features:
-------------
- Location Input: Accepts custom or predefined locations and resolves them to latitude/longitude using 'get_geocode()'.
- Forecast Display: Combines 'get_current_weather()' and 'get_pollen()' to present a full environmental snapshot.
- Recommendations: Uses 'get_recommendation()' to suggest actions based on weather and pollen data.
- Garden Interaction: Allows users to explore plant care tips and receive tailored advice via 'plant_weather_advisor()'.
- Rich CLI: Uses 'rich' library to render tables, panels, and menus for a visually engaging experience.
- Retry Logic: Offers retry prompts for failed geocoding or unsupported regions.

Garden Interaction and Plant Care:
----------------------------------
This section of the module handles the garden-specific interaction flow. It guides users through confirming their location, selecting soil type, 
entering plant names, and receiving tailored care recommendations based on environmental conditions and plant growth stages.

It integrates multiple subsystems — including plant care databases, weather compatibility logic, and rich CLI rendering — to create a personalized 
and educational experience for gardeners.

- Location Confirmation: Ensures the user's garden location is accurate before proceeding with care recommendations.
- Plant Prompting: Accepts vernacular, common, or scientific plant names and retrieves care data.
- Growth Stage Awareness: Adjusts care advice based on the plant's current development phase.
- Soil Type Input: Allows users to specify or skip soil type, influencing plant suitability and care logic.
- Weather Compatibility: Uses 'plant_weather_advisor()' to assess how current conditions affect plant health.
- Care Details: Offers optional deep dives into plant care via 'display_care_description()' from perenual.com.
- Retry Flow: Supports multiple plant entries and graceful exits.

Startup and Validation:
-----------------------
This final section of the module handles plant growth stage input, location validation, and app initialization. It enriches the garden experience 
by allowing users to specify plant development phases and soil types, which influence care recommendations and compatibility with current weather conditions.

It also includes robust input validation for location formatting and restricted regions, ensuring that the app only processes supported areas. 
The welcome message and startup logic provide a friendly, guided entry into the Bloom and Sky experience.

- Growth Stage Awareness: Users can specify plant development stages (seed, juvenile, adult, flowering, fruiting, senescence) to receive tailored care.
- Optional Input: Growth stage and soil type can be skipped without breaking the recommendation flow.
- Location Validation: Ensures user input matches the 'City, Country' format and filters out restricted regions.
- Regex Matching: Uses a robust regular expression to validate and normalize location strings.
- Restricted Region Handling: Prevents API calls to unsupported areas and provides clear feedback.
- Welcome Message: Displays a rich CLI introduction to the app, setting the tone for user engagement.

Functions:
----------
ask_retry() → bool  
    Prompts the user to retry an operation after failure. Returns True if user selects 'Y'.

add_more_plants() → str  
    Asks the user whether they want to explore more plants. Returns 'y' or 'n'.

ask_careInfo() → str  
    Prompts the user to view detailed care information or exit the garden. Returns 'y', 'n', or 'e'.

display_custom_forecast(location, latitude, longitude) → None  
    Fetches and displays current weather and pollen data for a given location. Prints forecast and recommendations.

get_location() → tuple[str, float, float]  
    Prompts the user for a location, validates geocoding, and returns the resolved coordinates.

main_menu() → str  
    Displays the main menu and returns the user's selected option: 'e', 'l', 'g', or 'q'.

not_supported_locations(regions: str) → Panel  
    Returns a rich panel warning about unsupported regions.

load_restr_locations(file_path: str) → list[str]  
    Loads and parses a list of restricted regions from a file.

location_subMenu() → str  
    Displays a submenu for location-specific actions. Returns 'e' for extended forecast or 'm' for main menu.

confirm_location(location: str) → str  
    Asks the user to confirm or change their garden location. Returns the confirmed or new location string.

prompt_plants(location: str) → None  
    Guides the user through entering plant data, selecting soil type, and receiving care recommendations. Supports multiple entries.

prompt_soilType() → str | None  
    Prompts the user to specify their garden's soil type. Returns the soil type string or None if skipped. Exits the program if 'e' is selected.

intro_plantGrowth() → None  
    Prints an educational overview of plant growth stages using rich formatting.

prompt_growthStage() → str | None  
    Prompts the user to enter a plant growth stage. Returns the stage or None if skipped.

plants_subMenu() → str  
    Displays the garden submenu and returns the user's choice: 'i', 'a', 'm', or 'd'.

prompt_location() → str | None  
    Prompts the user to enter a location in 'City, Country' format. Validates input and returns the location or None if skipped.

valid_coordinates(lat: float, lon: float) → bool  
    Returns True if both latitude and longitude are not None.

validate_input(location: str) → str  
    Validates and normalizes a location string. Raises ValueError or HTTPError if format is invalid or region is restricted.

welcome(description: str) → None  
    Displays the welcome message and app introduction using rich CLI formatting.

Email Provider Compatibility:
-----------------------------
This module is currently designed to work exclusively with Gmail, using Gmail's SMTP server and app-specific passwords. 
No other email providers are supported at this time.

If the project scales up, future versions may include support for other popular providers such as Outlook, Yahoo, and custom domains.

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project
'''


import time, datetime, re, sys
from googlemaps.exceptions import HTTPError
import requests, re
from rich.console import Console
from rich import print
from rich.panel import Panel

from recommendations import get_recommendation
from display_weather_table import print_table
from gmaps_package import get_geocode, get_current_weather, get_extended_forecast
from gmaps_pollen import get_pollen
from garden_care_guide import display_care_info, display_care_description, sanitize, clear_cache
from plant_vs_weather import plant_weather_advisor

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
        is_day, temp, description, rain_prob, humidity = get_current_weather(latitude, longitude)
    except (TypeError, IndexError, ValueError, requests.RequestException, HTTPError):
        raise

    #2 Fetch pollen data from Google Maps pollen API
    try:
        grass, weed, tree = get_pollen(latitude, longitude)
    except (TypeError, IndexError, ValueError) as e:  #requests.RequestException, HTTPError
        #safe_url = sanitize(e.request.url)
        print(f"Error processing pollen data for '{location}' location. ({e})")
        raise

    #3 Display today's forecast for chosen location.

    print_table(location, is_day, temp, description, rain_prob, humidity)

    #4 Display recommendations
    try:
        print(Panel.fit(f"{get_recommendation(is_day, temp, rain_prob, humidity, grass, tree, weed)}"))
    except TypeError:
        raise
    
def get_location():
    while True:
        try:
            location = prompt_userLocation()
            latitude, longitude = get_geocode(location)
            if valid_coordinates(latitude, longitude):
                return location, latitude, longitude
            else:
                time.sleep(0.5)
                print(f"Error: Invalid geocoding coordinates for provided location.\n")
                if ask_retry():
                    continue
                else:
                    raise IndexError
        except (IndexError, ValueError, HTTPError, AttributeError) as e:
            print(f"Error: Could not resolve geocoding coordinates for provided location. {e}")
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

def confirm_location(location: str):
    console = Console()
    while True:
        console.print(f"\nIs your garden located in [bold red]{location.upper()}[/bold red]?")
        choice = input(f"Press [C] to confirm or [L] to enter a new location: ➤ ").lower().strip()
        if choice == "c":
           return location
        elif choice == "l":
            custom_location = prompt_userLocation()
            return custom_location
        else:
            time.sleep(1)
            print("\nInvalid choice. Please, try again.\n")
            time.sleep(1)
            continue

def prompt_plants(location):
    console = Console()
    while True:
        soil_choice = prompt_soilType() # Prompt user for soil type.
        user_plant= input("\nType in here the name of a plant and/or tree in your garden. Use vernacular, common or scientific name: ➤  ").lower().strip() # Ask the user for plant name.         
        intro_plantGrowth() # Introduce soil choice to user.
        growth_stage = prompt_growthStage() # Ask the user for plant growth stage.
        try:
            plant_name, plant_id, watering, sunlight = display_care_info(user_plant, growth_stage, soil_choice) # Display table and recommendations.
        except ValueError as v:
            print(f"Error. Plant not found: {v}")
            continue

        console.print(Panel.fit(plant_weather_advisor(location, watering, sunlight)))

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
            clear_cache()
            print("")
            console = Console()
            console.rule("[bold red]GOOD BYE!", align="left") # EXIT program.
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
        
def prompt_userLocation():
        console = Console()
        for _ in range(3):
            try:
                print("")
                location = input("Please, type your location here (e.g., Paris, France): ").title().strip()
                print("")
                location = validate_input(location)
                return location
            except ValueError:
                console.print("Input not recognized. Try please format 'City, Country' (e.g., Paris, France). [red]Use 'English' for full app compatibility.[/red]")
                continue
            except HTTPError:
                print(f"Sorry, data for that region isn't available right now.")
                continue
        print("\nNo worries! Skipping your location forecast for now...")
        return

def valid_coordinates(lat, lon):
    if lat is not None and lon is not None:
        return lat and lon

# Load restricted locations (9 Countries, China: 34 Divisions, Cuba: 15 Provinces + 1 Special Municipality, Iran: 31 Provinces,
# Japan: 47 Prefectures, North Korea: 9 Provinces + 3 Cities, South Korea: 9 Provinces + 7 Cities, 
# Syria: 14 Governorates and Vietnam: 58 Provinces + 5 Municipalities ) from .txt in local disk.
RESTRICTED_SET = load_restr_locations("gmaps_restricted_locations.txt") #----{location.title() for location in RESTRICTED_LOCATIONS}---- for when i used to have the locations list inside Helpers. Dont remove in case the last modifications break the program.

def validate_input(location: str) -> str:
    # Regex for "City, Country" format
    LOCATION_PATTERN = re.compile(r"^([A-Za-zÀ-ÿ\s\-'\.]+), ([A-Za-zÀ-ÿ\s\-'\.]+)$", re.IGNORECASE)

    # Normalize comma spacing
    location = re.sub(r"\s*,\s*", ", ", location.strip())
    match = LOCATION_PATTERN.match(location)
    if not match:
        raise ValueError

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