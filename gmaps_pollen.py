#Script to request pollen data from Google Maps Pollen API. It returns grass, weed and trees risk levels from a given location.

import requests

def get_pollen(lat, long):

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"

    url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_key}&location.longitude={long}&location.latitude={lat}&days=1"

    response = requests.get(url)

    try:
        data = response.json()
        
        daily = data.get("dailyInfo", [{}])[0]
      
        risk_levels = {
        "GRASS": "Unknown",
        "WEED": "Unknown",
        "TREES": "Unknown"
        }

        # Search in pollenTypeInfo
        for item in daily.get("pollenTypeInfo", []):
            code = item.get("code")
            index_info = item.get("indexInfo")
            if code in risk_levels and index_info:
                risk_levels[code] = index_info.get("category", "Unknown")

        return risk_levels["GRASS"], risk_levels["WEED"], risk_levels["TREES"]
        
        #with open("daily.json", "w", encoding="utf-8") as f:
            #json.dump(daily, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error fetching pollen data: {e}.")
        return "Unknown", "Unknown", "Unknown"


#print(get_pollen(lat=52.0945228, long=4.2795904999))