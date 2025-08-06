import openmeteo_requests #type: ignore
import requests_cache #type: ignore
import pandas as pd #type: ignore
from datetime import datetime
import requests, sys #type: ignore
from retry_requests import retry #type: ignore
from helpers import daytime_to_bool

def get_weather(latitude, longitud):

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude, # 52.094523 as default for Statenkwartier
        "longitude": longitud, # 4.279590 as default for Statenkwartier
        "daily": ["apparent_temperature_max", "apparent_temperature_min", "precipitation_probability_max", "precipitation_hours"],
        "hourly": ["is_day", "relative_humidity_2m", "precipitation_probability", "temperature_80m", "soil_moisture_1_to_3cm"],
        "current": ["relative_humidity_2m", "apparent_temperature", "is_day", "precipitation"],
        "timezone": "Europe/Berlin",
        "forecast_days": 3,
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    # Check if the request was successful.
    try:
        response = responses[0] 

        # Process current data. The order of variables needs to be the same as requested.
        current = response.Current()
        current_relative_humidity = current.Variables(0).Value() # humidity variable
        current_apparent_temperature = current.Variables(1).Value() # temp variable
        current_is_day = daytime_to_bool(current.Variables(2).Value()) # 'time of the day' variable

        hourly = response.Hourly()
        current_hour_rain_probability = hourly.Variables(2).Values(0) # rain prob for the current hour

        return current_is_day, current_apparent_temperature, current_hour_rain_probability, current_relative_humidity 

    except requests.RequestException:
        print("Error fetching weather data.")
        sys.exit(1)