#Script to request pollen data from Google Maps Pollen API. It returns grass, weed and trees risk levels from a given location.
import requests, os
from garden_care_guide import load_cache, save_cache
from gmaps_package import get_geocode
from Api_limiter_class import ApiLimiter

POLLEN = "pollen_cache.json"
limiter = ApiLimiter(max_calls=5000, daily_max_calls=100, filepath="pollen_calls.json")

@limiter.guard(error_message="Gmaps Pollen API quota reached!")
def get_pollen(lat, lon):
    cache = load_cache(POLLEN)
    key = f"{float(lat):.7f}, {float(lon):.7f}"
    if key in cache:
        return tuple(cache[key])

    try:
        API_key = os.getenv("GMAPS_API_KEY")
        url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_key}&location.longitude={lon}&location.latitude={lat}&days=1"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        daily = data.get("dailyInfo", [{}])[0]
        limiter.record_call()

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
        save_cache(POLLEN, {key: result})

        return result

    except (TypeError, ValueError):
        raise
    except (requests.RequestException, requests.HTTPError):
        return "N/A", "N/A", "N/A"
    
def default_pollen():
    return get_pollen(lat="52.0945228",lon="4.2795905")

def main():
    import sys
    try:
        lat, lon = get_geocode("caracas, venezuela") # This will trigger 400 Client Error: Bad Request
        print(get_pollen(lat, lon))  # lat=51.5074, lon=-0.1278 for London
    except requests.exceptions.HTTPError:
        print("Google Maps Pollen data currently unavailable for this location.")
        sys.exit(1)
if __name__ == "__main__":
    main()
