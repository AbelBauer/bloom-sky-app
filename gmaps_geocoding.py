#Script to request a location geocode data(lat and long) from Google Maps Geocoding API
import googlemaps #type: ignore

def get_geocode(location) -> tuple:

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"
    gmaps = googlemaps.Client(key=API_key)

    # Location geocoding
    geocode_result = gmaps.geocode(location) # implement 'statenkwartier, zuid holland.' by default

    lat, long = tuple(geocode_result[0]["geometry"]["location"].values())

    return lat, long
   
#with open("default_location.json", "w", encoding="utf-8") as f:
#    json.dump(default, f, indent=4, ensure_ascii=False)