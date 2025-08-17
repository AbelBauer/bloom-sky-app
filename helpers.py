import time, datetime, re
from googlemaps.exceptions import HTTPError
import requests
from rich.console import Console #type: ignore
from rich import print
from rich.panel import Panel

from recommendations import get_recommendation
from display_weather_table import print_table
from gmaps_package import get_geocode, get_extended_forecast, get_current_weather
from gmaps_pollen import get_pollen

# HELPERS

def ask_retry():
    choice = input("\nWould you like to try again? ➤ yes [Y], or no [N]?  ➤  ").lower()
    return choice == "y"

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
                return location, latitude, longitude
            else:
                time.sleep(1)
                print(f"Error: Could not resolve geocoding coordinates for provided location.\n")
                if ask_retry():
                    continue
                else:
                    raise IndexError #return get_location(location)
        except (IndexError, ValueError, HTTPError):
            print(f"Error: Could not resolve geocoding coordinates for provided location.\n")
            if ask_retry():
                continue
            else:
                break

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
        choice = input("➤  ").strip().lower()
        valid_choices = ["e", "l", "g", "q"]
        if choice in valid_choices:
            return choice
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            continue

def not_supported_locations(regions):
    message = f"⚠️  [red]Heads-up: Weather and pollen data isn't currently available for a few regions, including: {regions.title()}."
    return Panel.fit(message)

def location_subMenu():
    while True:
        print("\n  [E] Check this location extended forecast")
        print("  [M] Main Menu")
        choice = input("➤  ").strip().lower()
        valid_choice = ["e", "m"]
        if choice in valid_choice:
            return choice
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            continue

def prompt_plants():
    plants = []
    while True:
        user_input= input("\nList the plants and/or trees in your garden (separate names with commas, e.g. fern, roses, etc):  ➤ ").lower().strip()
        new_plants = [plant.strip().lower() for plant in user_input.split(",") if plant.strip()] # takes raw user input and transforms it into a clean, lowercase list of plant names.
        plants.extend(new_plants)
        print("\nYour garden currently includes: \n")

        for i, plant in enumerate(plants, 1): # Numbered list. Makes it easy to read and visually organized.
            print(f"{i}. {plant.capitalize()}")

        choice = plants_subMenu()
        if choice == "i":
            ... # WIP 
        elif choice == "m":
            print("\nThanks for creating a virtual garden!\n")
            break
        elif choice == "a":
            continue
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            if ask_retry():
                continue
            else:
                break
    return plants

def plants_subMenu():
    while True:
        console = Console()
        print("")
        console.rule("[bold red]GARDEN MENU", align="left")
        print("\n [I] Display care information")
        print(" [A] Add more plants")
        print(" [M] Main Menu")
        choice = input("➤ ").lower().strip()
        valid_choices = ["i", "a", "m"]
        if choice in valid_choices:
            return choice
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            continue
        
def prompt_location():
        for _ in range(3):
            try:
                print("")
                location = input("Please, type your location here (e.g., Paris, France): ").title().strip()
                location = validate_input(location)
                return location
            except ValueError:
                print("Input not recognized. Try please format 'City, Country' (e.g., Paris, France).")
                continue
            except HTTPError:
                print("Sorry, data for that region isn't available right now.")
                continue
        print("\nNo worries! Skipping your location forecast for now...")
        return


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

RESTRICTED_LOCATIONS = {
    # Countries
    "China", "Cuba", "Iran", "Japan", "North Korea", "Korea", "South Korea", "Syria", "Vietnam",
    # China: 34 Divisions
    "Anhui", "Fujian", "Gansu", "Guangdong", "Guizhou", "Hainan", "Hebei", "Heilongjiang", "Henan", 
    "Hubei", "Hunan", "Jiangsu", "Jiangxi", "Jilin", "Liaoning", "Qinghai", "Shaanxi", "Shandong", 
    "Shanxi", "Sichuan", "Yunnan", "Zhejiang", "Beijing", "Chongqing", "Shanghai", "Tianjin", "Guangxi", 
    "Inner Mongolia", "Ningxia", "Tibet", "Xinjiang",
    # Cuba: 15 Provinces + 1 Special Municipality
    "Pinar del Río", "Artemisa", "Mayabeque", "Havana", "Habana", "Matanzas", "Cienfuegos", "Villa Clara", 
    "Sancti Spíritus", "Ciego de Ávila", "Camagüey", "Las Tunas", "Granma", "Holguín", "Santiago de Cuba", 
    "Guantánamo", "Isla de la Juventud",
    # Iran — 31 Provinces 
    "Alborz", "Ardabil", "Bushehr", "Chaharmahal and Bakhtiari", "East Azerbaijan", "Fars", "Gilan", "Golestan", 
    "Hamadan", "Hormozgan", "Ilam", "Isfahan", "Kerman", "Kermanshah", "Khuzestan", "Kohgiluyeh and Boyer-Ahmad", 
    "Kurdistan", "Lorestan", "Markazi", "Mazandaran", "North Khorasan", "Qazvin", "Qom", "Razavi Khorasan", 
    "Semnan", "Sistan and Baluchestan", "South Khorasan", "Tehran", "West Azerbaijan", "Yazd", "Zanjan",
    # Japan: 47 Prefectures
    "Aichi", "Akita", "Aomori", "Chiba", "Ehime", "Fukui", "Fukuoka", "Fukushima", "Gifu", "Gunma", "Hiroshima", 
    "Hokkaido", "Hyogo", "Ibaraki", "Ishikawa", "Iwate", "Kagawa", "Kagoshima", "Kanagawa", "Kochi", "Kumamoto", 
    "Kyoto", "Mie", "Miyagi", "Miyazaki", "Nagano", "Nagasaki", "Nara", "Niigata", "Oita", "Okayama", "Okinawa", 
    "Osaka", "Saga", "Saitama", "Shiga", "Shimane", "Shizuoka", "Tochigi", "Tokushima", "Tokyo", "Tottori", "Toyama", 
    "Wakayama", "Yamagata", "Yamaguchi", "Yamanashi",
    # North Korea: 9 Provinces + 3 Cities
    "Chagang", "North Hamgyong", "South Hamgyong", "North Hwanghae", "South Hwanghae", "Kangwon", "North Pyongan", 
    "South Pyongan", "Ryanggang", "Pyongyang", "Nampo", "Rason",
    # South Korea: 9 Provinces + 7 Cities
    "Gyeonggi", "Gangwon", "North Chungcheong", "South Chungcheong", "North Jeolla", "South Jeolla", "North Gyeongsang", 
    "South Gyeongsang", "Jeju", "Seoul", "Busan", "Daegu", "Incheon", "Gwangju", "Daejeon", "Ulsan",
    # Syria: 14 Governorates
    "Aleppo", "Damascus", "Daraa", "Deir ez-Zor", "Hama", "Al-Hasakah", "Homs", "Idlib", "Latakia", "Quneitra", "Raqqa", 
    "Rif Dimashq", "As-Suwayda", "Tartus",
    # Vietnam: 58 Provinces + 5 Municipalities
    "Hanoi", "Ho Chi Minh City", "Da Nang", "Hai Phong", "Can Tho", "An Giang", "Bac Giang", "Bac Kan", "Bac Lieu", 
    "Bac Ninh", "Ben Tre", "Binh Dinh", "Binh Duong", "Binh Phuoc", "Binh Thuan", "Ca Mau", "Cao Bang", "Dak Lak", 
    "Dak Nong", "Dien Bien", "Dong Nai", "Dong Thap", "Gia Lai", "Ha Giang", "Ha Nam", "Ha Tinh", "Hai Duong", 
    "Hau Giang", "Hoa Binh", "Hung Yen", "Khanh Hoa", "Kien Giang", "Kon Tum", "Lai Chau", "Lam Dong", "Lang Son", 
    "Lao Cai", "Long An", "Nam Dinh", "Nghe An", "Ninh Binh", "Ninh Thuan", "Phu Tho", "Phu Yen", "Quang Binh", 
    "Quang Nam", "Quang Ngai", "Quang Ninh", "Quang Tri", "Soc Trang", "Son La", "Tay Ninh", "Thai Binh", "Thai Nguyen", 
    "Thanh Hoa", "Thua Thien-Hue", "Tien Giang", "Tra Vinh", "Tuyen Quang", "Vinh Long", "Vinh Phuc", "Yen Bai",
}

# Future-proofing title case for effective comparison
RESTRICTED_SET = {location.title() for location in RESTRICTED_LOCATIONS}

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

def welcome(description):
    console = Console()
    print("")
    print("")
    console.rule("[bold red]WELCOME TO BLOOM & SKY APP", align="left")
    print(description)
    time.sleep(1)