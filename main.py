'''
Main Execution Module for Bloom & Sky CLI

This module serves as the entry point for the Bloom & Sky application, a Python-based CLI tool
that provides weather-driven gardening and health recommendations. It integrates geolocation,
forecast data, and expressive advice to guide users in plant care and daily planning.

Core Workflow:
--------------
- Displays default weather and pollen data for the user's home location.
- Generates expressive recommendations based on current conditions.
- Presents an interactive main menu with options to:
    - View extended forecasts
    - Explore weather in custom locations
    - Receive personalized plant care guidance
    - Exit the application gracefully

Key Features:
-------------
- Uses Google Maps and Weather APIs to retrieve location-based data.
- Applies caching and error handling to manage API limits and connectivity issues.
- Provides rich console output using styled tables and panels.
- Supports fallback messaging for unsupported regions and malformed inputs.

Dependencies:
-------------
- helper_functions: UI prompts, location handling, recommendation logic
- gmaps_package: weather forecast retrieval and display
- gmaps_pollen: pollen level data for default location
- garden_care_guide: application state management and cache utilities
- rich: console styling and layout
- requests, googlemaps: API communication and error handling

Note:
-----
This module is designed for interactive use and should be run directly.
Ensure that environment variables (e.g. GMAPS_API_KEY) are properly configured via .env.
'''


from helper_functions import not_supported_locations, display_custom_forecast, confirm_location
from helper_functions import main_menu, location_subMenu, prompt_plants, get_recommendation, get_location, welcome
from gmaps_pollen import default_pollen
from gmaps_package import get_extended_forecast, print_table, default_forecast
from garden_care_guide import AppState, clear_cache, sanitize
from rich import print
from rich.console import Console
from rich.panel import Panel
import time, sys, requests
from googlemaps.exceptions import HTTPError

def main():
    state = AppState()

    welcome(description="A Python application for gardening and health recommendations based on the weather forecast.\n")

    # Display 'HOME' info as default
    is_day, temp, description, rain_prob, humidity = default_forecast()
    grass, weed, trees = default_pollen() #unittest DONE!
    print("")
    print_table(f"{state.location.upper()} (HOME)", is_day, temp, description, rain_prob, humidity)
    try:
        weather_recommendation = get_recommendation(is_day, temp, rain_prob, humidity, grass, trees, weed) #unittest DONE!
        print(Panel.fit(weather_recommendation))
    except TypeError:
        print("Error displaying recommendations.")
        pass

    # Interactive Main Menu...
    while True:
        console = Console()
        main_choice = main_menu()

        if main_choice == "q":
            print("")
            clear_cache()
            print("")
            time.sleep(0.7)
            console.rule("[bold red]GOOD BYE!", align="left")
            sys.exit()

        elif main_choice == "l":
            print("")
            print(not_supported_locations(regions="China, Cuba, Iran, Japan, North Korea, South Korea, Syria, and Vietnam"))
            try:
                location, latitude, longitude = get_location()
                state.update_location(new_location=location)
                print("")
                time.sleep(0.3)
                display_custom_forecast(location.upper(), latitude, longitude)
            except TypeError as e:
                print(f"\nError displaying recommendations: {e}.") 
                console.print("[bold red]Please, try another location.")
                continue
            except (ValueError, IndexError) as e:
                print(f"\nError fetching weather data for '{location.upper()}' ({e}).") 
                console.print("[bold red]Please, try another location.")
                continue
            except (requests.RequestException, HTTPError) as e:
                safe_msg = sanitize(e.response.url)
                print(f"\nError fetching current weather data for '{location.upper()}' ({safe_msg}).") 
                console.print("[bold red]Please, try another location.")
                continue
            sub_choice = location_subMenu()
            if sub_choice == "m":
                continue
            elif sub_choice == "e":
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
            get_extended_forecast(location="STATENKWARTIER, DEN HAAG", lat="52.0945228", lon="4.2795905") # default for 'Home' location
            state.update_location("statenkwartier, den haag")
        elif main_choice == "g":
            time.sleep(0.5)
            console = Console()
            print("")
            console.rule("[bold red]WELCOME TO YOUR VIRTUAL GARDEN", align="left")
            print("Your garden is more than decoration, it's a living ecosystem. Every plant and tree you care for contributes to cleaner air, biodiversity, and a sense of peace and beauty. Taking good care of them is great responsability and lots of fun, too!\n")
            time.sleep(1)
            new_location = confirm_location(location=state.location)
            prompt_plants(location=new_location)

if __name__ == "__main__":
    main()