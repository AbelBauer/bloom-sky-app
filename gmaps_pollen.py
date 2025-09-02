#Script to request pollen data from Google Maps Pollen API. It returns grass, weed and trees risk levels from a given location.
import requests, json, os
from diskcache import Cache
from dotenv import load_dotenv

def get_pollen(lat, long): # Set up a lat/lon cache in the geocode function. Load it up here.
    #cache = Cache("gmaps_pollen_cache")
    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU" #os.getenv("gmaps.env")
    url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_key}&location.longitude={long}&location.latitude={lat}&days=1"

    #key = (lat, long)
    #if key in cache:
    #    return cache[key]

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
                risk_levels[code] = index_info.get("category")

        result = (risk_levels["GRASS"], risk_levels["WEED"], risk_levels["TREES"])
        #cache[key] = result

        with open("daily.json", "w", encoding="utf-8") as f:
            json.dump(daily, f, indent=4, ensure_ascii=False)
        
        return result       
        
    except (TypeError, ValueError, requests.RequestException):
        raise


#print(get_pollen(lat=51.5074, long=-0.1278))  # London
