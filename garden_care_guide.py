"""
garden_guide.py

Plant Identification and Care Recommendation Utility

This module provides a multi-tiered system for identifying plants and generating care guidance,
leveraging local caches, fuzzy matching, and live API queries from Perenual.com.

Core Features:
--------------
1. **Care Cache Lookup**: Quickly resolves known plant names from a local species cache.
2. **Fuzzy Matching**: Uses approximate string matching to identify species from cached data.
3. **Live API Fallback**: Queries the Perenual API if no local match is found.
4. **Care Info Retrieval**: Fetches watering, sunlight, and scientific details from cache or API.
5. **Care Description Display**: Retrieves and formats pruning, watering, and sunlight guidance.
6. **Rich Console Output**: Displays care tables and recommendations using `rich` formatting.
7. **Recommendation Engine**: Integrates with `generate_plant_recommendation()` to suggest simple care routines.

Functions:
----------
- load_cache(path): Loads JSON data from a given cache file.
- save_cache(path, data): Updates and saves data to a cache file.
- get_fuzzy_plant(name, data, threshold=70): Performs fuzzy matching on cached plant names.
- api_live_query(name): Queries the Perenual API for species data.
- get_name_and_id(name): Resolves a plant name using cache, fuzzy match, or API.
- fetch_care_info(plant_id, plant_name): Retrieves watering and sunlight info.
- fetch_description(plant_id, plant_name): Retrieves pruning, watering, and sunlight descriptions.
- display_care_info(plant, growth, soil): Displays care table and generates recommendations.
- display_care_description(plant_id, plant_name): Displays formatted care descriptions.
- run_garden_guide(plant_name): Main entry point to run the guide for a given plant name.

Dependencies:
-------------
- fuzzywuzzy (for fuzzy string matching)
- requests (for API calls)
- rich (for styled console output)
- plants_recomm_templates (for care recommendation generation)
- Local cache files:
    - CARE_CACHE_FILE
    - FILE_DESCRIP_CACHE
    - SPECIES_CACHE

Usage:
------
Call `run_garden_guide("white fir")` to resolve a plant name, display care info, and show care descriptions.

Notes:
------
- Ensure all cache files are present and properly formatted.
- Define a valid `API_KEY` for live queries to the Perenual API.
- Console output is styled using the `rich` library for enhanced readability.
"""



import os, json, time, requests
from fuzzywuzzy import process
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from plants_recomm_templates import generate_plant_recommendation
from dotenv import load_dotenv

CARE_CACHE_FILE = "plants_main_info_DATABASE.json"
FILE_DESCRIP_CACHE = "plants_care_description_DATABASE.json"
SPECIES_CACHE = "plants_Dataset_cache.json"

load_dotenv()
API_KEY = os.getenv("PERENUAL_API_KEY") # Secure this data!

def load_cache(path): # 1. OK
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(path, data): # OK too
    cache = load_cache(path)
    cache.update(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=True, indent=2)

def extract_care_info(data):
    try:
        return (
            data.get('common_name', 'Unknown'),
            data.get('scientific_name', ['Unknown'])[0],
            data.get('watering', 'Unknown').lower(),
            data.get('watering_general_benchmark', {}).get("value", "Unknown"),
            ', '.join(data.get('sunlight', ['Unknown']))
        )
    except Exception as e:
        print(f"⚠️ Error extracting care info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

def extract_care_descriptions(data):
    try:
        sections = data["data"][0]["section"]
        guide = {s["type"]: s["description"] for s in sections if s.get("type") and s.get("description")}
        return (
            guide.get("watering", "Unavailable data."),
            guide.get("sunlight", "Unavailable data."),
            guide.get("pruning", "Unavailable data.")
        )
    except Exception as e:
        print(f"⚠️ Error extracting care descriptions: {e}")
        return "Unavailable data.", "Unavailable data.", "Unavailable data."

def get_fuzzy_plant(name, data, threshold=70):
    name = name.strip().lower()
    candidates, plant_map = [], {}

    for plant in data.get("data", []):
        names = [plant.get("common_name", "")] + plant.get("scientific_name", []) + plant.get("other_name", [])
        for n in names:
            if n:
                normalized = n.strip().lower()
                candidates.append(normalized)
                plant_map[normalized] = plant

    if not candidates:
        print("⚠️ No candidates available for fuzzy matching.")
        return None, None, None

    result = process.extractOne(name, candidates)
    if result is None:
        print("⚠️ No fuzzy match found.")
        return None, None, None

    match, score = result
    if score >= threshold:
        return "fuzzy", match, plant_map[match]["id"]

    print(f"⚠️ Match score too low: {score}")
    return None, None, None


def api_live_query(name):
    print("🌐 Trying live API...")
    url = f"https://perenual.com/api/v2/species-list?q={name}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        #return data
        if data.get("data"):
            plant = data["data"][0]
            return "api", plant.get("common_name", name), plant["id"] #....debugging
    except Exception as e:
        print(f"🚫 API error: {e}")
    return None, None, None

def get_name_and_id(name): # 2. OK
    normalized = name.strip().lower()
    species_cache = load_cache(SPECIES_CACHE)

    if normalized in species_cache: # Name located in cache
        plant = species_cache[normalized]
        print("✴️  Name resolved from care cache.")
        return "cached", plant.get("common_name", name), plant.get("id")
    
    match_type, plant_name, plant_id = get_fuzzy_plant(name, species_cache) # Fuzzy match to resolve user's typo.
    if match_type:
        print(f"✴️  Resolved from care cache. Found '{plant_name}' via {match_type} match.")
        return match_type, plant_name, plant_id

    return api_live_query(name) # Otherwise call API and try to find a match.

def fetch_care_info(plant_id, plant_name): # 3. OK
    normalized = plant_name.lower()
    cache = load_cache(CARE_CACHE_FILE)

    if normalized in cache:
        print("✴️  Care data from cache.")
        return extract_care_info(cache[normalized])
    
    url = f"https://perenual.com/api/v2/species/details/{plant_id}?key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        save_cache(CARE_CACHE_FILE, {normalized: content})
        print("❇️  Care data from API.")
        return extract_care_info(content)
    except Exception as e:
        print(f"🚫 Error fetching care info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

def fetch_description(plant_id, plant_name): # 6. OK
    normalized = plant_name.lower()
    cache = load_cache(FILE_DESCRIP_CACHE)
    if normalized in cache:
        print("✴️  Description from cache.")
        #return "Skipping." # Enable this line to use the function in DATABASE_BUILDER.py
        return extract_care_descriptions(cache[normalized]) # Disable this line to use in DATABASE_BUILDER.py
    url = f"https://perenual.com/api/species-care-guide-list?species_id={plant_id}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        save_cache(FILE_DESCRIP_CACHE, {normalized: content})
        print("❇️  Description from API.")
        return extract_care_descriptions(content) # Disable this line to use in DATABASE_BUILDER.py
    except Exception as e:
        print(f"🚫 Error fetching description: {e}")
        return "Unavailable data.", "Unavailable data.", "Unavailable data."

def display_plants_description(water, sun, prun): # 7. OK
    return Panel.fit(water.strip()), Panel.fit(sun.strip()), Panel.fit(prun.strip())

def display_care_info(plant, growth, soil): # 4. OK. Fixed typo-ed names passed onto generate_plant_recommendation() function. 
    # Next up: Fix phrases in recommendations template. Some job already done, though. Keep going and focus on the watering phrases.
    console = Console()
    plant_data = {}

    match_type, plant_name, plant_id = get_name_and_id(plant)

    if not plant_id:
        print("❌ Could not identify plant.")
        return plant_data, None
    
    vernacular, scientific, watering, frequency, sunlight = fetch_care_info(plant_id, plant_name)

    table = Table(title="🌿 Virtual Garden Care Guide", show_lines=True, header_style="bold", title_style="bold on white")
    table.add_column("Vernacular Name", style="green")
    table.add_column("Scientific Name", style="cyan")
    table.add_column("Watering", style="magenta")
    table.add_column("Sunlight", style="yellow")
    table.add_row(vernacular.title(), scientific.title(), watering.title(), sunlight.title())
    console.print(table)

    recommendations = (generate_plant_recommendation(plant_name=plant_name.title(), watering_level=watering, watering_frequency=f"{frequency} days", sunlight_level=sunlight.lower(), growth_stage=growth, soil_type=soil))
    console.print(Panel.fit(recommendations))

    return plant_name, plant_id # Enable/Disable for isolated-test this module.

def display_care_description(plant_id, plant_name): # 5. OK
    console = Console()

    water, sun, prun = fetch_description(plant_id, plant_name)
    w, s, p = display_plants_description(water, sun, prun)
    console.rule(f"[bold yellow]{plant_name.upper()}", align="left")
    console.print(w)
    console.print(s)
    console.print(p)
    time.sleep(1)

#-----------------------------------------------------------------------------
# Function for module testing purpose only! 
def run_garden_guide(plant_name):
    plant_name = plant_name.lower()
    print("")
    name, id = display_care_info(plant=plant_name, growth="adult", soil="loam")
    display_care_description(id, name)

# Example usage
#run_garden_guide("tree heath") # Enable/Disable. For module test only.
