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

# HELPERS

def ask_retry():
    choice = input("\nWould you like to try again? yes [Y], or no [N]?  ➤  ").lower()
    return choice == "y"

def add_more_plants():
    choice  = input("\nWould you like to list more plants? yes [Y], or no [N]?  ➤ ").lower().strip()
    return choice == "y"

def ask_retry_careInfo():
    while True:
        user_choice = input("\nWould you like to see detailed care information?: yes [Y], no [N], exit the garden [E]?  ➤  ").lower().strip()
        valid_choices = ["y", "n", "e"]
        if user_choice in valid_choices:
            return user_choice
        else:
            print("Invalid choice. Please, try again.")
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
        console.print("\n  [bold cyan][E][/bold cyan] Check extended forecast for 'HOME' location.")
        console.print("  [bold cyan][L][/bold cyan] Type in custom location.")
        console.print("  [bold cyan][G][/bold cyan] Enter virtual garden.")
        console.print("  [bold cyan][Q][/bold cyan] Quit.")
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
    console = Console()
    while True:
        console.print("\n  [bold cyan][E][/bold cyan] - Check this location extended forecast")
        console.print("  [bold cyan][M][/bold cyan] - Main Menu")
        choice = input("➤  ").strip().lower()
        valid_choice = ["e", "m"]
        if choice in valid_choice:
            return choice
        else:
            print("\nInvalid option")
            time.sleep(0.5)
            continue

def prompt_plants():
    soil_choice = prompt_soilType() # Prompt user for soil type. This is a global garden parameter.  
    while True:
        user_plant= input("\nType in here the name of a plant and/or tree in your garden. Use vernacular, common or scientific name: ➤  ").lower().strip() # Ask the user for plant name.         
        intro_plantGrowth() # Introduce soil choice to user.
        growth_stage = prompt_growthStage() # Ask the user for the plant growth stage.
        plant_data, plant_name = display_care_info(user_plant, soil_choice, growth_stage) # Display table and recommendations.
        choice = ask_retry_careInfo()
        print("")
        if choice == "y":
            display_care_description(plant_data, plant_name) # Display detailed care information from perenual.com.
            while True:
                if add_more_plants(): # Ask if the user wants to add more plants or not.
                    continue
                elif add_more_plants() == False:
                    break 
                else:
                    print("Invalid choice. Please, try again.")
                    continue
        elif choice == "n":
            continue
        elif choice == "e":
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
            print("Invalid option. Please, try again.")
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
            print("Invalid option. Please, try again.")
            continue


def plants_subMenu():
    while True:
        console = Console()
        print("")
        console.rule("[bold red]GARDEN MENU", align="left")
        console.print("\n [bold cyan][I][/bold cyan] - Display care information")
        console.print(" [bold cyan][A][/bold cyan] - Add more plants")
        console.print(" [bold cyan][M][/bold cyan] - Main Menu")
        choice = input("➤ ").lower().strip()
        print("")
        valid_choices = ["i", "a", "m", "d"]
        if choice in valid_choices:
            return choice
        else:
            print("\nInvalid option. Please, try again.")
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