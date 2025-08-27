# Module that fetch, extract and display a garden care guide for a given list of plants. All the data is gotten from Perenual API
import requests, json, os, time
from difflib import get_close_matches
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from plants_recomm_templates import generate_plant_recommendation
from dotenv import load_dotenv

# Constants
CACHE_FILE = "plants_cache.json"
CACHE_FILE_DESCRIP = "plant_care_description.json"
API_KEY = os.getenv("perenual_api")

# Plant list
plants_list = [
    "Ficus elastica", "Dracaena fragrans", "Lady Fern", "weeping cedar of lebanon", "japanese hornbeam",
]

# Load and save cache
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def load_description_cache():
    if os.path.exists(CACHE_FILE_DESCRIP):
        with open(CACHE_FILE_DESCRIP, "r") as f:
            return json.load(f)
    return {}

def save_cache(data):
    cache = load_cache()
    cache.update(data)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def save_description_cache(data):
    cache = load_description_cache()
    cache.update(data)
    with open(CACHE_FILE_DESCRIP, "w") as f:
        json.dump(cache, f, indent=2)

# Load caches
LOADED_CACHE_CARE_INFO = load_cache()
LOADED_CACHE_DESCRIPTION = load_description_cache()

# Extract care info
def extract_care_info(data):
    try:
        return (
            data.get('common_name', 'Unknown'),
            data.get('scientific_name', ['Unknown'])[0],
            data.get('watering', 'Unknown').lower(),
            data.get('watering_general_benchmark', {}).get("value", "Unknown").strip('"').strip("'"),
            ', '.join(data.get('sunlight', ['Unknown']))
        )
    except Exception as e:
        print(f"⚠️ Error extracting care info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

# Extract care descriptions
def extract_care_descriptions(data):
    try:
        sections = data["data"][0]["section"]
        guide = {s["type"]: s["description"].strip() for s in sections if s.get("type") and s.get("description")}
        return guide.get("watering", ""), guide.get("sunlight", ""), guide.get("pruning", "")
    except Exception as e:
        print(f"⚠️ Error extracting care descriptions: {e}")
        return "", "", ""

# Fuzzy matching
def fuzzy_plant_name(name, data, cutoff=0.75):
    name = name.lower()
    candidates = []
    for plant in data.get("data", []):
        candidates.append(plant.get("common_name", "").lower())
        candidates.extend([s.lower() for s in plant.get("scientific_name", [])])
        candidates.extend([o.lower() for o in plant.get("other_name", [])])
    matches = get_close_matches(name, candidates, n=1, cutoff=cutoff)
    if matches:
        #print(f"⚠️ By '{name}' you mean '{matches[0]}'?")
        return matches[0]
    for candidate in candidates:
        if name in candidate:
            print(f"🔍 Partial match found: '{name}' in '{candidate}'")
            return candidate
    print(f"❌ No match found for '{name}'")
    return None

# Fetch plant ID
def fetch_plant_id(name: str, cache: json) -> tuple:
    normalized = name.lower()
    if normalized in cache:
        return cache[normalized]["id"], normalized
    fuzzy_name = fuzzy_plant_name(name, {"data": list(cache.values())})
    if fuzzy_name:
        for key, plant in cache.items():
            names = [plant.get("common_name", "").lower()] + \
                    [s.lower() for s in plant.get("scientific_name", [])] + \
                    [o.lower() for o in plant.get("other_name", [])]
            if fuzzy_name in names:
                return plant["id"], key.lower()
    # Fallback to API
    url = f"https://perenual.com/api/v2/species-list?q={name}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        fuzzy_name_api = fuzzy_plant_name(name, content)
        if fuzzy_name_api:
            for plant in content["data"]:
                names = [plant.get("common_name", "").lower()] + \
                        [s.lower() for s in plant.get("scientific_name", [])] + \
                        [o.lower() for o in plant.get("other_name", [])]
                if fuzzy_name_api in names:
                    return plant["id"], fuzzy_name_api.lower()
    except Exception as e:
        print(f"Error fetching plant ID: {e}")
    return None, None

# Fetch care info
def fetch_care_info(plant_id: int, plant_name: str, cache: json) -> tuple:
    normalized = plant_name.lower()
    if normalized in cache:
        print("✴️  Care data from cache.")
        return extract_care_info(cache[normalized])
    url = f"https://perenual.com/api/v2/species/details/{plant_id}?key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        save_cache({normalized: content})
        print("❇️  Care data from Perenual API.")
        return extract_care_info(content)
    except Exception as e:
        print(f"Error fetching care info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

# Fetch description
def fetch_description(plant_id: int, plant_name: str, cache: json) -> tuple:
    normalized = plant_name.lower()
    if normalized in cache:
        print("✴️  Description from cache.")
        return extract_care_descriptions(cache[normalized])
    url = f"https://perenual.com/api/species-care-guide-list?species_id={plant_id}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        save_description_cache({normalized: content})
        print("❇️  Description from Perenual API.")
        return extract_care_descriptions(content)
    except requests.exceptions.HTTPError:
        if response.status_code == 429:
            print(f"API rate limit reached! Please, try again tomorrow.")
            return "Unavailable", "Unavailable", "Unavailable"
    except requests.RequestException as e:
         print(f"Error fetching description: {e}")
         return "Unavailable", "Unavailable", "Unavailable"

# Display panels
def display_plants_description(water: str, sun: str, prun: str) -> str:
    return Panel.fit(water), Panel.fit(sun), Panel.fit(prun)

#--------------------------------------------------------------------------------------------------------

def display_care_info(plant: str, soil: str, growth: str) -> dict:
    #Displays a table of basic care info for each plant in the list.
    #Returns a dictionary mapping plant names to (plant_id, normalized_name).
    console = Console()
    plant_data = {}
    plant_id, plant_name = fetch_plant_id(plant, LOADED_CACHE_CARE_INFO)
    if plant_id:
        vernacular, scientific, watering, frequency, sunlight = fetch_care_info(plant_id, plant_name, LOADED_CACHE_CARE_INFO)

        table = Table(title="🌿 Virtual Garden Care Guide", title_style="bold on white", show_lines=True, header_style="bold")
        table.add_column("Vernacular Name", style="bold green")
        table.add_column("Scientific Name", style="cyan")
        table.add_column("Watering", style="magenta")
        #table.add_column("Frequency", style="yellow")
        table.add_column("Sunlight", style="yellow")
        table.add_row(vernacular.title(), scientific.title(), watering.title(), sunlight.title())
        console.print(table)

        recommendations = (generate_plant_recommendation(plant_name=plant.title(), watering_level=watering, watering_frequency=f"{frequency} days", sunlight_level="full sun", growth_stage=growth, soil_type=soil))
        console.print(Panel.fit(recommendations))

        plant_data[plant] = (plant_id, plant_name)
        print("")
    
    return plant_data, plant_name

    '''
    plant_data = {} # Snippet to print out in one table the whole plants list
    for plant in plants_list:
        plant_id, plant_name = fetch_plant_id(plant, LOADED_CACHE_CARE_INFO)
        if plant_id:
            vernacular, scientific, watering, frequency, sunlight = fetch_care_info(plant_id, plant_name, LOADED_CACHE_CARE_INFO)
            recommendations = (generate_plant_recommendation(plant_name=plant.title(), growth_stage="young", watering_level=watering.lower(), watering_frequency=f"{frequency} Days", sunlight_level="full sun"))
            console.print(Panel.fit(recommendations))
            table.add_row(vernacular.title(), scientific.title(), watering.title(), sunlight.title())
            plant_data[plant] = (plant_id, plant_name)
    
    print("")
    console.print(table)
    return plant_data '''

def display_care_description(plant_data: dict, plant: str):
    #Displays detailed care descriptions (watering, sunlight, pruning) for each plant.
    console = Console()
    plant_id, plant_name = plant_data.get(plant, (None, None))
    if plant_id:
        water, sun, prun = fetch_description(plant_id, plant_name, LOADED_CACHE_DESCRIPTION)
        w, s, p = display_plants_description(water, sun, prun)
        console.rule(f"[bold yellow]{plant_name.upper()}", align="left")
        console.print(w)
        console.print(s)
        console.print(p)
        print("")
        time.sleep(2)

def normalize_plants_names(plants_list: list) -> list: # Deprecated! 
    return [plant.lower() for plant in plants_list if plant] 
#Catch later on "AttributeError: 'int' object has no attribute 'lower'" with a try/except block. KeyError and TypeError too.


def run_garden_guide(plants_list: list):
    #Runs the full garden care guide: basic info + detailed descriptions.
    plants_list = normalize_plants_names(plants_list)
    print("")
    plant_data = display_care_info(plants_list)
    print("")
    display_care_description(plant_data, plants_list)

#run_garden_guide(plants_list)