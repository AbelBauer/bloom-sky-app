from difflib import get_close_matches
import requests

API_KEY = "sk-194o68a8aecdc9f6411611"

def extract_plants_names(data):
    candidates = []
    plant_map = {}

    for plant in data.get("data", []):
        plant_id = plant.get("id")
        common = plant.get("common_name", "").lower()
        scientific = [s.lower() for s in plant.get("scientific_name", [])]
        other = [o.lower() for o in plant.get("other_name", [])]

        all_names = [common] + scientific + other
        for n in all_names:
            candidates.append(n)
            plant_map[n] = {
                "matched_name": n,
                "plant_id": plant_id,
                "plant_data": plant
            }
    return candidates, plant_map

def find_match(name, candidates_list, plant_dict):
    # 1. Exact match
    if name in candidates_list:
        print(f"✅ Exact match: '{name}'")
        result = plant_dict[name]
        return result["matched_name"], result["plant_id"], "exact"

    # 2. Close match
    matches = get_close_matches(name, candidates_list, n=1, cutoff=0.75)
    if matches:
        match = matches[0]
        print(f"⚠️ Close match: '{name}' → '{match}'")
        result = plant_dict[match]
        return result["matched_name"], result["plant_id"], "close"

    # 3. Partial match
    for candidate in candidates_list:
        if name in candidate:
            print(f"🔍 Partial match: '{name}' in '{candidate}'")
            result = plant_dict[candidate]
            return result["matched_name"], result["plant_id"], "partial"

    print(f"❌ No match found for '{name}'")
    return None, None, "none"
    



def get_fuzzy_plantID(name, data, cache=None):

    """
    Attempts to match a plant name against a dataset using fuzzy logic.

    Parameters:
        name (str): The user-input plant name (possibly misspelled).
        data (dict): API response containing plant data.
        cache (dict): Local cache of previously fetched plant data to reduce API calls.

    Returns:
        tuple: (matched_name, plant_id, match_type)
            - matched_name (str): The name that was matched.
            - plant_id (int): The ID of the matched plant.
            - match_type (str): One of 'exact', 'close', 'partial', or 'none'.
    """

    candidates, plant_map = extract_plants_names(data=data)
    matched_name, plant_id, match_result = find_match(name, candidates, plant_map)
    return matched_name, plant_id, match_result

plant = "fullmoon"
url = f"https://perenual.com/api/v2/species-list?q={plant}&key={API_KEY}"
response = requests.get(url)
response.raise_for_status()
content = response.json()

matched_name, plant_id, match_type = get_fuzzy_plantID(plant, content)
print(f"Matched Name: {matched_name}")
print(f"Plant ID: {plant_id}")
print(f"Match Type: {match_type}")

































'''

def get_fuzzy_plantID(name, data, cache, cutoff=0.75):
    """ Attempts to match a plant name against a dataset using fuzzy logic.

    Parameters:
        name (str): The user-input plant name (possibly misspelled).
        data (dict): API response containing plant data.
        cutoff (float): Similarity threshold for fuzzy matching (0 to 1).

    Returns:
        tuple: (matched_name, plant_id, match_type)
            - matched_name (str): The name that was matched.
            - plant_id (int): The ID of the matched plant.
            - match_type (str): One of 'exact', 'close', 'partial', or 'none'. """
    
    name = name.lower() # check first if we have a match in cache
    if name in cache:
        return cache[name]["id"], name

    candidates = []
    plant_map = {}

    for plant in data.get("data", []):
        plant_id = plant.get("id")
        common = plant.get("common_name", "").lower()
        scientific = [s.lower() for s in plant.get("scientific_name", [])]
        other = [o.lower() for o in plant.get("other_name", [])]

        all_names = [common] + scientific + other
        for n in all_names:
            candidates.append(n)
            plant_map[n] = {
                "matched_name": n,
                "plant_id": plant_id,
                "plant_data": plant
            }

    # 1. Exact match
    if name in candidates:
        print(f"✅ Exact match: '{name}'")
        result = plant_map[name]
        return result["matched_name"], result["plant_id"], "exact"

    # 2. Close match
    matches = get_close_matches(name, candidates, n=1, cutoff=cutoff)
    if matches:
        match = matches[0]
        print(f"⚠️ Close match: '{name}' → '{match}'")
        result = plant_map[match]
        return result["matched_name"], result["plant_id"], "close"

    # 3. Partial match
    for candidate in candidates:
        if name in candidate:
            print(f"🔍 Partial match: '{name}' in '{candidate}'")
            result = plant_map[candidate]
            return result["matched_name"], result["plant_id"], "partial"

    print(f"❌ No match found for '{name}'")
    return None, None, "none"


plant_name = "fullmoon"
url = f"https://perenual.com/api/v2/species-list?q=fern&key={API_KEY}"
response = requests.get(url)
response.raise_for_status()
content = response.json()

matched_name, plant_id, match_type = get_fuzzy_plantID(plant_name, content)
print(f"Matched Name: {matched_name}")
print(f"Plant ID: {plant_id}")
print(f"Match Type: {match_type}") '''
