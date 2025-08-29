from difflib import get_close_matches
import requests

API_KEY = "sk-194o68a8aecdc9f6411611"

def get_fuzzy_plant_id(name, data, cutoff=0.7):
    name = name.lower()
    candidates = []
    
    for plant in data.get("data", []):
        candidates.append(plant.get("common_name", "").lower())
        candidates.extend([s.lower() for s in plant.get("scientific_name", [])])
        candidates.extend([o.lower() for o in plant.get("other_name", [])])
    matches = get_close_matches(name, candidates, n=3, cutoff=cutoff)
    if matches:
        print(f"⚠️ Did you mean '{matches[0]}' instead of '{name}'?")
        return matches
    for candidate in candidates:
        if name in candidate:
            print(f"🔍 Partial match found: '{name}' in '{candidate}'")
            return candidate
    print(f"❌ No match found for '{name}'")
    return None


name = "white fir"
url = f"https://perenual.com/api/v2/species-list?q={name}&key={API_KEY}"

response = requests.get(url)
response.raise_for_status()
content = response.json()

print(get_fuzzy_plant_id(name="white firr", data=content))
