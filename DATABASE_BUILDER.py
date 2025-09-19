"""
Plant Care Database Builder

This script builds two local JSON databases by retrieving plant data from the Perenual API:

1. Basic Plant Info Database (`plants_main_info_DATABASE.json`)
   - Uses plant species IDs to fetch full plant details.
   - Stores each entry using a normalized version of the plant's common name as the key.
   - Skips entries already cached or missing a common name.
   - Logs any failed requests to `error_log.txt`.

2. Plant Care Guide Database (`plants_care_description_DATABASE.json`)
   - Uses a curated list of scientific names to fetch care guide descriptions.
   - Relies on fuzzy matching to resolve names to valid species IDs.
   - Stores care guide data using normalized common names as keys.
   - Skips duplicates and logs any errors encountered.

Utilities:
- `load_cache(path)`: Loads existing cache from disk.
- `save_cache(path, data)`: Merges new data into cache and saves to disk.
- `normalize_name(name)`: Converts names to lowercase and replaces spaces with underscores.
- `save_to_disk(plant, error)`: Appends error messages to a local log file for future actions.
- `clean_list(names)`: Sorts and returns a cleaned list of plant names.
- `load_plants_names(file_path)`: Loads a comma-separated `.txt` file of scientific names from disk, strips quotes and whitespace, and returns a sorted list.

Dependencies:
- `requests`, `json`, `time`, `os`
- External module: `fuzzy_match` (must provide `fetch_description` and `get_name_and_id`)

Usage:
- Configure `API_KEY` with your Perenual API key.
- Adjust `plants_idX` ranges or `plants` list as needed.
- To build the care guide database, provide a `.txt` file containing scientific names (e.g. `"plants_list.txt"`).
- Run the script to populate both databases incrementally.

Note:
- The script includes built-in rate limiting (`time.sleep`) to avoid overwhelming the API.
- Error handling ensures resilience against network failures or malformed responses.
"""


import requests
import time
import os
import json
from dotenv import load_dotenv
from Api_limiter_class import ApiLimiter

BASE_DETAILS_URL = "https://perenual.com/api/v2/species/details/"
BASIC_CACHE_PATH = "plants_main_info_DATABASE.json"
SPECIES_CACHE = "plants_Dataset_cache.json"

load_dotenv()
API_KEY=os.getenv("GMAPS_API_KEY")
CARE_CACHE_PATH="plants_care_description_DATABASE.json"
limiter = ApiLimiter(filepath="database_builder_calls.json")

def load_cache(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(path, data):
    cache = load_cache(path)
    cache.update(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=True, indent=2)


def normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")

def save_to_disk(plant, error):
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"Error fetching plant {plant}: {error}.\n")
    
def load_plants_names(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        # split by comma, strip quotes and whitespace
        return sorted([name.strip().strip('"') for name in content.split(",") if name.strip()])

def build_basic_care_cache(plant_ids):
    cache = load_cache(BASIC_CACHE_PATH)
    counter = 1

    for plant_id in plant_ids:
        try:
            url = f"{BASE_DETAILS_URL}{plant_id}?key={API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                common_name = data.get("common_name")

                if not common_name:
                    print(f"⚠️ Skipping plant {plant_id}: No common name found.")
                    continue

                key = normalize_name(common_name)
                if key in cache:
                    continue  # Already cached by name

                save_cache(BASIC_CACHE_PATH, {key: data})
                print(f"❇️ Data successfully retrieved! - {counter} - {common_name}")
                counter += 1

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching plant {plant_id}: {e}")
            continue

plants_id1 = range(1,100)
plants_id2 = range(2001,4000)
plants_id3 = range(4001,6000)
plants_id4 = range(6001,8000)
plants_id5 = range(8001,10000)

#-------------------------------------------------------------------

from garden_care_guide import fetch_description, get_name_and_id

def clean_list(names):
    return sorted(names)

plants_list = load_plants_names("plants_list.txt") # File path of the plants list.
#Go there to update with new plants names.

# Execution.
counter = 1
for plant in plants_list:
    try:
        report, name, id = get_name_and_id(plant.lower())
        result = fetch_description(id, name)
        if result == "Skipping.":
            continue
        print(f"❇️ Succesfully saved - {plant} - {counter}")
        print("")
        counter = counter + 1
        time.sleep(1)
    except Exception as e:
        print(f"🚩 Error: {e} - {plant}")
        save_to_disk(plant, e)
        continue

print("All done!")
