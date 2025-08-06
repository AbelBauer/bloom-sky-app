"""
Location-to-Coordinates Converter

This script prompts the user to input a location name (e.g., "The Hague, Netherlands") 
and uses the OpenCage Geocoder API to convert that location into geographic coordinates 
(latitude and longitude). These coordinates can then be used for geospatial applications, 
such as fetching weather data from Open-Meteo.

Modules used:
- opencage.geocoder: for geocoding
- input(): for location prompt

Usage:
1. User runs the script.
2. A prompt appears asking for the desired location.
3. The script returns the latitude and longitude for that location.

Make sure to obtained a free API key from https://opencagedata.com/api and added it to the KEY variable.

"""

from opencage.geocoder import OpenCageGeocode #type: ignore

KEY = "257ab0d577e44f709441cd292c300a20"  # API key

def get_coordinates(city) -> tuple:
    try:
        geocoder = OpenCageGeocode(KEY)
        results = geocoder.geocode(city)
        if results:
            latitud = results[0]['geometry']['lat']
            longitud = results[0]['geometry']['lng']
            return latitud, longitud
        else:
            raise ValueError("Location not found.")
    except Exception as e:
        print(f"\n⚠️ Geocoding error for ➱ '{city}': {e}")
        return None, None
