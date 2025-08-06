import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.0931,
	"longitude": 4.2758,
	"daily": ["apparent_temperature_max", "apparent_temperature_min", "precipitation_probability_max", "precipitation_hours"],
	"hourly": ["is_day", "relative_humidity_2m", "precipitation_probability", "temperature_80m", "soil_moisture_1_to_3cm"],
	"current": ["relative_humidity_2m", "apparent_temperature", "is_day", "precipitation"],
	"timezone": "Europe/Berlin",
	"forecast_days": 3,
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_relative_humidity_2m = current.Variables(0).Value()
current_apparent_temperature = current.Variables(1).Value()
current_is_day = current.Variables(2).Value()
current_precipitation = current.Variables(3).Value()

print(f"\nCurrent time: {current.Time()}")
print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
print(f"Current apparent_temperature: {current_apparent_temperature}")
print(f"Current is_day: {current_is_day}")
print(f"Current precipitation: {current_precipitation}")

daily = response.Daily()
daily_precipitation_probability_max = daily.Variables(2).Values(0) # Today's max rain prob

print(daily_precipitation_probability_max)

'''
# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_is_day = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
hourly_temperature_80m = hourly.Variables(3).ValuesAsNumpy()
hourly_soil_moisture_1_to_3cm = hourly.Variables(4).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["is_day"] = hourly_is_day
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["temperature_80m"] = hourly_temperature_80m
hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_apparent_temperature_max = daily.Variables(0).ValuesAsNumpy()
daily_apparent_temperature_min = daily.Variables(1).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(2).ValuesAsNumpy() # rain probability here!
daily_precipitation_hours = daily.Variables(3).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
daily_data["precipitation_hours"] = daily_precipitation_hours

daily_dataframe = pd.DataFrame(data = daily_data)
print("\nDaily data\n", daily_dataframe)
'''