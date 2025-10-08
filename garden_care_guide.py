'''
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
7. **Recommendation Engine**: Integrates with a template module to suggest care routines.

Functions:
----------
- load_cache(path): Loads JSON data from a given cache file.
- save_cache(path, data): Updates and saves data to a cache file.
- extract_care_info(data): Safely extracts common and scientific names, watering, sunlight, and soil data from a plant's API response.
- extract_care_descriptions(data): Retrieves care descriptions (watering, sunlight, pruning) from the API.
- get_fuzzy_plant(name, data, threshold=70): Performs fuzzy matching on cached plant names, returning a list of unique matches.
- api_live_query(name): Queries the Perenual API for a specific species.
- get_name_and_id(name): Resolves a plant name using cache, fuzzy matching, or a live API query.
- fetch_care_info(plant_id, plant_name): Retrieves basic care information from cache or API.
- fetch_description(plant_id, plant_name): Retrieves detailed care descriptions from cache or API.
- display_care_info(plant_name, growth, soil): Displays a care table and generates a recommendation for a given plant.
- display_care_description(plant_id, plant_name): Displays formatted care descriptions.
- run_garden_guide(plant_name): Main entry point to run the full guide for a given plant name.

Dependencies:
-------------
- fuzzywuzzy: For fuzzy string matching.
- requests: For making API calls.
- rich: For styled console output.
- plants_recomm_templates: For care recommendation generation.
- dotenv: To load the API key from a .env file.
- Local cache files (defined by constants): CARE_CACHE_FILE, FILE_DESCRIP_CACHE, SPECIES_CACHE

Usage:
------
Call 'run_garden_guide("white fir")' to resolve a plant name, display care info, and show care descriptions.

Notes:
------
- Ensure all cache files are present and properly formatted.
- The PERENUAL_API_KEY must be set in a '.env' file for live queries.
- The 'rich' library is used for enhanced console readability.

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project

'''

import os, json, time, requests, re
from fuzzywuzzy import process
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from plants_recommendations import generate_plant_recommendation
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List, Optional
from Api_limiter_class import ApiLimiter

CARE_CACHE_FILE = "plants_main_info_DATABASE.json"
FILE_DESCRIP_CACHE = "plants_care_description_DATABASE.json"
SPECIES_CACHE = "plants_Dataset_cache.json"

load_dotenv()
API_KEY = os.getenv("PERENUAL_API_KEY")
limiter = ApiLimiter(max_calls=5000, daily_max_calls=1000, filepath="garden_calls.json")

def load_cache(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ Error leyendo caché en {path}: {e}")
            return {}
    return {}

def save_cache(path, data):
    cache = load_cache(path)
    cache.update(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=True, indent=2)

def clear_cache():
    console = Console()
    cache_files = ["pollen_cache.json", "extended_weather_cache.json"]
    for path in cache_files:
        try:
            if os.path.exists(path):
                os.remove(path)
                console.print(f"🧹 Cache successfully cleared: [bold red]'{path}'[/bold red].")
                time.sleep(0.3)
        except Exception as e:
            print(f"Error clearing cache [bold red]'{path}'[/bold red]: {e}.")

def sanitize(url: str):
    # Hide api key in urls when showing errors in CLI.
    api_key = os.getenv("GMAPS_API_KEY", "")
    if api_key:
        url = url.replace(api_key, "[API_KEY]")

    url = re.sub(r'key=[^&]+', 'key=[API_KEY]', url)
    return url

def extract_care_info(data) -> tuple:
    try:
        return (
            data.get('common_name', 'Unknown'),
            data.get('scientific_name', ['Unknown'])[0],
            data.get('watering', 'Unknown').lower(),
            data.get('watering_general_benchmark', {}).get("value", "Unknown"),
            ', '.join(data.get('sunlight', ['Unknown'])),
            data.get('soil', 'Unknown'), # New addition! 'Best Soil' variable to show on table and to pass on.
        )
    except Exception as e:
        print(f"⚠️ Error extracting care info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

def extract_care_descriptions(data) -> tuple:
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
    console = Console()
    time.sleep(0.3)
    console.print(f"\nSearching for ➜ [bold red]'{name}'...[/bold red]")
    time.sleep(0.3)
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

    best_result = process.extractOne(name, candidates)
    total_matches = process.extract(name, candidates, limit=20)

    total_plants = set()

    console.print(f"\n[bold green]Found in local cache... ")
    index = 1
    for match, score in total_matches:
        plant = plant_map.get(match)
        if plant:
            common_name = plant.get("common_name", "N/A")
            scientific_name = plant.get("scientific_name", [""])[0]
            plant_tuple = (common_name, scientific_name)
            if plant_tuple not in total_plants:
                console.print(f"{index}. 🌱 [red]{common_name.title()}[/red] [bold yellow]({scientific_name.title()})[/bold yellow]") # - Match Score: {score}
                time.sleep(0.2)
                total_plants.add(plant_tuple)
                index += 1

    print("")
    time.sleep(1)

    if best_result is None:
        print(f"\n ⚠️ No fuzzy match found.")
        return None, None, None

    match, score = best_result
    if score >= threshold:
        return "fuzzy", match, plant_map[match]["id"]

    print(f"\n ⚠️ Match score too low: {score}")
    return None, None, None

@limiter.guard(error_message="Perenual API quota reached!")
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
            limiter.record_call()
            return "api", plant.get("common_name", name), plant["id"] #....debugging
    except Exception as e:
        print(f"🚫 API error: {e}")
    return None, None, None

def get_best_name_and_id(name):
    normalized = name.strip().lower()
    species_cache = load_cache(SPECIES_CACHE)

    if normalized in species_cache: # Name located in cache
        plant = species_cache[normalized]
        print("✴️  Name found in cache.")
        return "cached", plant.get("common_name", name), plant.get("id")
    
    match_type, plant_name, plant_id = get_fuzzy_plant(name, species_cache) # Fuzzy match to resolve user's typo.
    if match_type:
        print(f"✴️  Resolved from cache. Found '{plant_name}' via {match_type} match.")
        return match_type, plant_name, plant_id

    return api_live_query(name) # Otherwise call API and try to find a match.

@limiter.guard(error_message="Perenual API quota reached!")
def fetch_care_info(plant_id, plant_name): 
    normalized = plant_name.lower()
    cache = load_cache(CARE_CACHE_FILE)

    if normalized in cache:
        print(f"✴️  Care data from cache.\n")
        return extract_care_info(cache[normalized])
    
    url = f"https://perenual.com/api/v2/species/details/{plant_id}?key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        limiter.record_call()
        save_cache(CARE_CACHE_FILE, {normalized: content})
        print(f"❇️  Care data from API.\n")
        return extract_care_info(content)
    except Exception as e:
        print(f"🚫 Error fetching care info: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

@limiter.guard(error_message="Perenual API quota reached!")
def fetch_description(plant_id, plant_name):
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
        limiter.record_call()
        save_cache(FILE_DESCRIP_CACHE, {normalized: content})
        print("❇️  Description from API.")
        return extract_care_descriptions(content) # Disable this line to use in DATABASE_BUILDER.py
    except Exception as e:
        print(f"🚫 Error fetching description: {e}")
        return "Unavailable data.", "Unavailable data.", "Unavailable data."

def care_description_table(water, sun, prun):
    return Panel.fit(water.strip(), title="[bold yellow]Watering[/bold yellow]", title_align="left"), Panel.fit(sun.strip(), title="[bold yellow]Sunlight[/bold yellow]", title_align="left"), Panel.fit(prun.strip(), title="[bold yellow]Pruning[/bold yellow]", title_align="left")

def display_care_info(plant, growth, soil): 
    console = Console()
    plant_data = {}

    match_type, plant_name, plant_id = get_best_name_and_id(plant)

    if not plant_id:
        print("❌ Could not identify plant.")
        return plant_data, None

    vernacular, scientific, watering, frequency, sunlight, plant_soil = fetch_care_info(plant_id, plant_name)

    if frequency:
        frequency = f"{frequency.strip('"')} days"
    else:
        frequency = "N/A"

    best_soil_cleaned_list = []
    for s in plant_soil:
        cleaned_s = s.strip().strip("'").strip('"')
        best_soil_cleaned_list.append(cleaned_s)

    best_soil = str(best_soil_cleaned_list).strip("[]")
    if best_soil == "":
        best_soil = "N/A"

    table = Table(title="🌿 Virtual Garden Care Guide", show_lines=True, header_style="bold", title_style="bold on white")
    table.add_column("Vernacular Name", style="red")
    table.add_column("Scientific Name", style="cyan")
    table.add_column("Watering", style="magenta")
    table.add_column("Sunlight", style="yellow")
    table.add_column("Best Soil", style="green")
    table.add_row(vernacular.title(), scientific.title(), watering.title(), sunlight.title(), best_soil.title())
    console.print(table)

    recommendations = (generate_plant_recommendation(plant_name=plant_name.title(), watering_level=watering, watering_frequency=frequency, sunlight_level=sunlight.lower(), growth_stage=growth, soil_type=soil))
    console.print(Panel.fit(recommendations))

    if "," in sunlight:
        sunlight_care = sunlight.split(", ")
        sunlight = sunlight_care[0] # Decide what to do with the second [1] sunlight need parameter from perenual.com

    return plant_name, plant_id, watering.lower().strip(), sunlight.lower().strip()

def display_care_description(plant_id, plant_name):
    console = Console()
    water, sun, prun = fetch_description(plant_id, plant_name)
    w, s, p = care_description_table(water, sun, prun)
    console.rule(f"[bold yellow]{plant_name.upper()}", align="left")
    print("")
    console.print(w)
    console.print(s)
    console.print(p)
    time.sleep(1)

@dataclass # New thingy to automate classes that primarily store data. It controls data via fields (location, user_id and history)
class AppState:
    location:str = "Statenkwartier, Den Haag"
    user_id: Optional[str] = None # If in the future the app supports multi-user functionality...
    history: List[str] = field(default_factory=list)

    def update_location(self, new_location:str):
        cleaned = new_location.strip().lower()
        if cleaned and cleaned != self.location:
            self.history.append(cleaned)
            self.location = cleaned

    def __post_init__(self):
        self.location = self.location.strip()


#-----------------------------------------------------------------------------
# Function for module testing purpose only! 
def run_garden_guide(plant_name):
    plant_name = plant_name.lower()
    print("")
    name, id, watering, sunlight = display_care_info(plant=plant_name, growth="adult", soil="loam")
    display_care_description(id, name)

def main():
    # Example usage
    run_garden_guide("coconut palm")

if __name__ == "__main__":
    main()
