import requests #type: ignore  
import sys
import json

api = 'RfHDxxJMH-59cRk_k7W7dQeX40OBAFZN95avMQtEZEI'

url = 'https://trefle.io/api/v1/plants?token=RfHDxxJMH-59cRk_k7W7dQeX40OBAFZN95avMQtEZEI'
page = 1
plant_entries = []

try:
    while True:
        response = requests.get(f"{url}&page={page}")
        content = response.json()
        #plants_data = [plant.get("common_name") for plant in content["data"]] # Extract data to a list from JSON response
        if "data" not in content or not content["data"]:
            break
        #total_plants.extend(content["data"])
        #plants_name = [plant["common_name"] for plant in total_plants]
        #plants_name = sorted(plants_name)

        for plant in content["data"]: # to search base on the slug 
            slug = plant.get("slug")
            if not slug:
                continue
        
            detail_url = f'https://trefle.io/api/v1/plants/{slug}?token={api}'
            detail_response = requests.get(detail_url)
            detail_response.raise_for_status()
            details = detail_response.json().get("data", {})

            species = details.get("main_species", {})
            growth = species.get("growth", {})

            entry = {
                "common_name": plant.get("common_name", "N/A"),
                "scientific_name": plant.get("scientific_name", "N/A"),
                "description": species.get("description", "N/A"),
            }

            plant_entries.append(entry)

        page += 1
        
        if page == 50:
            break


except requests.RequestException:
    print("Error fetching plants data")
    sys.exit(1)

#for name in plants_name:
#    print(f"🌱 {name}.")
#    print('=========================')

with open("garden_plants.json", "w") as file:
    json.dump(plant_entries, file, indent=2)


#for plant in plant_entries:
#    print(plant['common_name'])