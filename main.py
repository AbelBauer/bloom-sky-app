from helpers import main_menu, location_subMenu, prompt_plants, get_recommendation, welcome, not_supported_locations, display_custom_forecast, get_location, get_extended_forecast
from default_forecast import get_default_forecast
from display_weather_table import print_table
from gmaps_pollen import get_pollen
from rich import print
from rich.console import Console
from rich.panel import Panel
import time, sys, requests
from googlemaps.exceptions import HTTPError 

welcome(description="A Python application for gardening and health recommendations based on the weather forecast.\n")

# Display 'HOME' info as default
is_day, temp, description, humidity, rain_prob = get_default_forecast(lat="52.094523",long= "4.279590")
grass, weed, trees = get_pollen(lat="52.094523",long= "4.279590")
print("")
print_table("Statenkwartier, Zuid Holland (Home).", is_day, temp, description, humidity, rain_prob)
print(Panel.fit(f"{get_recommendation(is_day, temp, rain_prob, humidity, grass, trees, weed)}"))

# Interactive Menu...
while True:
    console = Console()
    main_choice = main_menu()

    if main_choice == "q":
        print("")
        console.rule("[bold red]GOOD BYE!", align="left")
        sys.exit()

    elif main_choice == "l":
        print("")
        print(not_supported_locations(regions="China, Cuba, Iran, Japan, North Korea, South Korea, Syria, and Vietnam"))
        try:
            location, latitude, longitude = get_location()
            time.sleep(1)
            print("")
            display_custom_forecast(location, latitude, longitude)
        except (TypeError, IndexError, ValueError, requests.RequestException, HTTPError):
            continue
        sub_choice_1 = location_subMenu()
        if sub_choice_1 == "m":
            continue
        elif sub_choice_1 == "e":
            print("")
            get_extended_forecast(location, latitude, longitude)
            continue
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            continue
        
    elif main_choice == "e":
        print("")
        get_extended_forecast(location="Statenkwartier, Zuid Holland", lat=52.0945228, long=4.279590499999999) # default for 'Home' location
    elif main_choice == "g":
        time.sleep(1)
        console = Console()
        print("")
        console.rule("[bold red]WELCOME TO YOUR VIRTUAL GARDEN", align="left")
        print("Your garden is more than decoration, it's a living ecosystem. Every plant and tree you care for contributes to cleaner air, biodiversity, and a sense of peace and beauty. Taking good care of them is great responsability and lots of fun, too!\n")
        plants = prompt_plants() #WIP...implement what to do with plants list
            
