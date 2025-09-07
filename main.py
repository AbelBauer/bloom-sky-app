from helpers import not_supported_locations, display_custom_forecast, confirm_location
from helpers import main_menu, location_subMenu, prompt_plants, get_recommendation, get_location,  welcome
from default_forecast import get_default_forecast
from display_weather_table import print_table
from gmaps_pollen import get_pollen
from gmaps_package import get_extended_forecast
from rich import print
from rich.console import Console
from rich.panel import Panel
import time, sys, requests
from googlemaps.exceptions import HTTPError

LOCATION = "Statenkwartier, Den Haag"

welcome(description="A Python application for gardening and health recommendations based on the weather forecast.\n")

# Display 'HOME' info as default
is_day, temp, description, humidity, rain_prob = get_default_forecast(lat="52.094523",long= "4.279590")
grass, weed, trees = get_pollen(lat="52.094523",long= "4.279590")
print("")
print_table(f"{LOCATION.upper()} (HOME)", is_day, temp, description, humidity, rain_prob)
print(Panel.fit(f"{get_recommendation(is_day, temp, rain_prob, humidity, grass, trees, weed)}"))

# Interactive Main Menu...
while True:
    console = Console()
    main_choice = main_menu()

    if main_choice == "q":
        print("")
        time.sleep(0.3)
        console.rule("[bold red]GOOD BYE!", align="left")
        sys.exit()

    elif main_choice == "l":
        print("")
        print(not_supported_locations(regions="China, Cuba, Iran, Japan, North Korea, South Korea, Syria, and Vietnam"))
        try:
            location, latitude, longitude = get_location()
            LOCATION = location
            time.sleep(0.3)
            display_custom_forecast(location, latitude, longitude)
        except (TypeError, IndexError, ValueError, requests.RequestException, HTTPError):
            continue
        sub_choice_1 = location_subMenu()
        if sub_choice_1 == "m":
            continue
        elif sub_choice_1 == "e":
            time.sleep(0.4)
            get_extended_forecast(location, latitude, longitude)
            continue
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            continue
    elif main_choice == "e":
        print("")
        time.sleep(0.4)
        get_extended_forecast(location="STATENKWARTIER, ZUID HOLLAND", lat=52.0945228, long=4.279590499999999) # default for 'Home' location
    elif main_choice == "g":
        time.sleep(0.5)
        console = Console()
        print("")
        console.rule("[bold red]WELCOME TO YOUR VIRTUAL GARDEN", align="left")
        print("Your garden is more than decoration, it's a living ecosystem. Every plant and tree you care for contributes to cleaner air, biodiversity, and a sense of peace and beauty. Taking good care of them is great responsability and lots of fun, too!\n")
        time.sleep(1)
        place = confirm_location(location=LOCATION)
        prompt_plants(location=place)