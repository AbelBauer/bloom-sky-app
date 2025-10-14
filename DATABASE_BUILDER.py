'''
Plant Database Builder Module

This module constructs and updates a local plant care database by retrieving species details and care descriptions
from the Perenual API. It supports persistent caching, error logging, and API quota management to ensure efficient
and reliable data collection.

Core Responsibilities:
----------------------
- Load and normalize plant names from a local text file
- Fetch plant metadata and care descriptions using plant IDs and fuzzy name matching
- Store structured data in JSON cache files for later use by recommendation and care modules
- Log errors and skipped entries for review and debugging

Key Functions:
--------------
- load_cache(path): Loads existing JSON cache from disk
- save_cache(path, data): Updates and writes cache data to disk
- normalize_name(name): Converts plant names to lowercase, underscore-separated keys
- save_to_disk(plant, error): Logs failed API fetch attempts to 'error_log.txt'
- load_plants_names(file_path): Parses a comma-separated list of plant names from a text file
- build_basic_care_cache(plant_ids): Fetches and stores basic plant metadata using numeric IDs
- clean_list(names): Sorts and returns a cleaned list of plant names

Execution Flow:
---------------
- Loads plant names from 'plants_list.txt'
- For each plant:
    - Uses fuzzy matching to find the best name and ID
    - Fetches care description via Perenual API
    - Saves result to disk if successful
    - Logs errors if any occur

Caching:
--------
- BASIC_CACHE_PATH: Stores general plant metadata
- CARE_CACHE_PATH: Stores care descriptions
- SPECIES_CACHE: Optional dataset cache
- API calls are tracked using 'database_builder_calls.json'

Dependencies:
-------------
- requests
- dotenv
- time, os, json
- ApiLimiter (custom quota management class)
- garden_care_guide (custom care description fetcher)

Environment:
------------
- Requires 'PERENUAL_API_KEY' in a .env file for API access

Note:
-----
This module is designed for batch execution and may take several minutes depending on the number of plants processed.
Ensure that 'plants_list.txt' is properly formatted and updated with desired plant names.

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project

'''


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
API_KEY=os.getenv("PERENUAL_API_KEY")
CARE_CACHE_PATH="/Users/abelrodriguez/Documents/CS/Bloom & Sky/plants_care_description_DATABASE.json"
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
    return name.strip().lower()

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

plants_id1 = range(1,2000)
plants_id2 = range(2001,4000)
plants_id3 = range(4001,6000)
plants_id4 = range(6001,8000)
plants_id5 = range(8001,10000)
plants_id6 = range(10001, 11000)

#-------------------------------------------------------------------

from garden_care_guide import fetch_description, get_best_name_and_id

def clean_list(names):
    return sorted(names)

plants_list = load_plants_names("plants_list.txt") # File path of the plants list.
#Go there to update with new plants names.

# Execution.
'''counter = 1
for plant in plants_list:
    try:
        report, name, id = get_best_name_and_id(plant.lower())
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

print("All done!") '''


def description_database(plant_ids):
    cache = load_cache(CARE_CACHE_PATH)
    counter = 1

    for plant_id in plant_ids:
        url = f"https://perenual.com/api/species-care-guide-list?page=1&species_id={plant_id}&key={API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                care_list = data.get("data", [])

                if not care_list:
                    print(f"⚠️ Skipping plant {plant_id}: No care data found.")
                    continue

                common_name = care_list[0].get("common_name")
                if not common_name:
                    print(f"⚠️ Skipping plant {plant_id}: No common name found.")
                    continue

                key = normalize_name(common_name)
                if key in cache:
                    print(f"Plant '{common_name}' already in cache.")
                    continue

                cache[key] = data
                save_cache(CARE_CACHE_PATH, cache)
                print(f"❇️ Data successfully retrieved! - {counter} - {common_name}")
                counter += 1

            time.sleep(1)

        except Exception as e:
            print(f"Error fetching plant {plant_id}: {e}")
            continue



def main():
    description_database(plants_id6)
    print("Done!")
if __name__ == "__main__":
    main()