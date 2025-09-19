"""
Weather Forecast Module - Bloom and Sky

This module provides geolocation and weather forecasting capabilities using the Google Maps and Google Weather APIs.
It includes persistent caching, quota-aware API limiting, and rich terminal output for daily and extended forecasts.

Designed for personal use, the system integrates with Gmail to send usage alerts once API consumption reaches critical thresholds.
All API calls are tracked and throttled using the `ApiLimiter` class to avoid exceeding monthly quotas.

Features:
---------
- Geocoding: Converts location names to latitude/longitude using Google Maps API, with persistent caching.
- Current Weather: Retrieves real-time conditions including temperature, humidity, rain probability, and daylight status.
- Extended Forecast: Displays today and tomorrow's weather with daytime/nighttime breakdowns.
- Rich Output: Uses 'rich' tables for colorful, readable CLI presentation.
- Caching: Stores geocode and forecast data locally to reduce redundant API calls.
- API Limiting: Enforces monthly quota and triggers alerts via Gmail when usage exceeds 50%.
- Alerting: Begins sending daily usage summaries once quota crosses 50%, using Gmail SMTP.

Functions:
----------
get_geocode(location: str) → tuple[float, float]
    Returns latitude and longitude for a given location, using cache if available.

get_current_weather(lat: float, lon: float) → tuple[bool, int, str, int, int]
    Returns current weather conditions including daylight status, temperature, description, humidity, and rain probability.

get_extended_forecast(location: str, lat: float, lon: float) → None
    Displays today and tomorrow's forecast in the terminal using rich tables.

extract_forecast(api_data: dict) → tuple
    Parses forecast data from API response and returns structured weather metrics.

sort_json() → None
    Alphabetically sorts the geocode cache file for efficient lookup.

Email Provider Compatibility:
-----------------------------
This module is currently designed to work **exclusively with Gmail**, using Gmail's SMTP server and app-specific passwords.
No other email providers are supported at this time.

If the project scales up, future versions may include support for other popular providers such as Outlook, Yahoo, and custom domains.

Requirements:
-------------
- Python 3.8+
- Google Maps and Weather API access
- Gmail account with app-specific password
- .env file containing GMAPS_API_KEY
- Packages: 'googlemaps', 'requests', 'rich', 'python-dotenv'

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project
"""



import googlemaps, requests
from googlemaps.exceptions import HTTPError
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
import os, json
from garden_care_guide import load_cache, save_cache, sanitize
from Api_limiter_class import ApiLimiter

GEOCODE = "geocode_cache.json"
EXTENDED_WEATHER = "extended_weather_cache.json"
API_KEY=os.getenv("GMAPS_API_KEY")

limiter = ApiLimiter(max_calls=5000, daily_max_calls=1000, filepath="gmaps_calls.json")

# Get geocode (lat, long) for location, with persistent caching
@limiter.guard(fallback="Gmaps Geocode API quota reached!")
def get_geocode(location: str):
    cache = load_cache(GEOCODE)
    if location is not None:
        key = location.lower().strip()
        if key in cache:
            lat, long = cache[key]
            return f"{lat:.7f}", f"{long:.7f}"
    else:
        raise AttributeError

    try:
        load_dotenv()
        gmaps = googlemaps.Client(key=API_KEY)
        geocode_result = gmaps.geocode(location.strip().lower())
        lat, long = tuple(geocode_result[0]["geometry"]["location"].values())
        # Log call if the function calls API.
        limiter.record_call()
        save_cache(GEOCODE, {key: [lat, long]})
        return f"{lat:.7f}", f"{long:.7f}"
    except (IndexError, HTTPError):
        raise

# Extract forecast data from API response
def extract_forecast(api_data):
    day_forecast = api_data.get('daytimeForecast', {}).get('weatherCondition', {}).get('description', {}).get('text', 'unknown')
    day_humidity = api_data.get('daytimeForecast', {}).get('relativeHumidity', {})
    day_rain = api_data.get('daytimeForecast', {}).get('precipitation', {}).get('probability', {}).get('percent', {})
    night_forecast = api_data.get('nighttimeForecast', {}).get('weatherCondition', {}).get('description', {}).get('text', 'unknown')
    night_humidity = api_data.get('nighttimeForecast', {}).get('relativeHumidity', {})
    night_rain = api_data.get('nighttimeForecast', {}).get('precipitation', {}).get('probability', {}).get('percent', {})
    min_temp = api_data.get('minTemperature', {}).get('degrees', {})
    max_temp = api_data.get('maxTemperature', {}).get('degrees', {})

    return day_forecast, day_humidity, day_rain, night_forecast, night_humidity, night_rain, min_temp, max_temp

# Get current weather conditions
@limiter.guard(error_message="Gmaps Weather API quota reached!")
def get_current_weather(lat: float, lon: float) -> tuple[bool, int, str, int, int]:

    # 1. Call API
    try:
        url = f"https://weather.googleapis.com/v1/currentConditions:lookup?key={API_KEY}&location.latitude={lat}&location.longitude={lon}"
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
    #2. Parse data
        is_day = content.get("isDaytime", False)
        temp = content.get("temperature", {}).get("degrees") or 0
        description = content.get("weatherCondition", {}).get("description", {}).get("text", "N/A")
        rain_prob = content.get("precipitation", {}).get("probability", {}).get("percent") or 0
        humidity = content.get("relativeHumidity") or 0
        
        try:
            result = bool(is_day), int(temp), str(description.title()), int(rain_prob), int(humidity)
            return result
        except ValueError:
            raise
    except TypeError:
        raise

    except (HTTPError, requests.RequestException):
        raise

# Get extended forecast (today and tomorrow)
@limiter.guard(error_message="Gmaps Weather API quota reached!")
def get_extended_forecast(location: str, lat: float, lon: float): 
    cache = load_cache(EXTENDED_WEATHER)
    key = f"{float(lat):.7f}, {float(lon):.7f}"
    if key in cache:
        today, tomorrow = cache[key]
    else:
        try:
            url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_KEY}&location.latitude={lat}&location.longitude={lon}&days=2"
            response = requests.get(url)
            response.raise_for_status()
            content = response.json()
            forecast = content.get('forecastDays', [])
            if len(forecast) < 2:
                return "Error fetching weather forecast data"

            today = extract_forecast(forecast[0])
            tomorrow = extract_forecast(forecast[1])
            # Log call if the function calls API
            limiter.record_call()
            save_cache(EXTENDED_WEATHER, {key: [today, tomorrow]})

        except (requests.RequestException, HTTPError) as r:
            print(f"Error fetching extended forecast: {r}")
        except KeyError as k:
            print(f"Error processing forecast data: {k}")

    # Unpack today's forecast
    td_day_descrip, td_day_humidity, td_day_rain, td_night_descrip, td_night_humidity, td_night_rain, td_min_temp, td_max_temp = today
    # Unpack tomorrow's forecast
    tm_day_descrip, tm_day_humidity, tm_day_rain, tm_night_descrip, tm_night_humidity, tm_night_rain, tm_min_temp, tm_max_temp = tomorrow

    console = Console()

    # Today's Forecast Table
    td_table_day = Table(title=f"\n{location} ➜  Today's Forecast:\n", title_style="bold on yellow", header_style="bold red")
    td_table_temps = Table(title="Temperatures", header_style="bold red", title_style="bold")
    td_table_temps.add_column("Min. 🌡", justify="center")
    td_table_temps.add_column("Max. 🌡", justify="center")
    td_table_temps.add_row(f"{td_min_temp}°C", f"{td_max_temp}°C")
    td_table_day.add_column("🕓", justify="center")
    td_table_day.add_column("📝", justify="center")
    td_table_day.add_column("Rain Prob. 🌦️", justify="center")
    td_table_day.add_column("Humidity 💧", justify="center")
    td_table_day.add_row("🌞", td_day_descrip, f"{td_day_rain} %", f"{td_day_humidity} %")
    td_table_day.add_row("🌘", td_night_descrip, f"{td_night_rain} %", f"{td_night_humidity} %")

    # Tomorrow's Forecast Table
    tm_table_day = Table(title=f"\n{location} ➜  Tomorrow's Forecast:\n", title_style="bold on yellow", header_style="bold red")
    tm_table_temps = Table(title="Temperatures", header_style="bold red", title_style="bold")
    tm_table_temps.add_column("Min. 🌡", justify="center")
    tm_table_temps.add_column("Max. 🌡", justify="center")
    tm_table_temps.add_row(f"{tm_min_temp}°C", f"{tm_max_temp}°C")
    tm_table_day.add_column("🕓", justify="center")
    tm_table_day.add_column("📝", justify="center")
    tm_table_day.add_column("Rain Prob. 🌦️", justify="center")
    tm_table_day.add_column("Humidity 💧", justify="center")
    tm_table_day.add_row("🌞", tm_day_descrip, f"{tm_day_rain} %", f"{tm_day_humidity} %")
    tm_table_day.add_row("🌘", tm_night_descrip, f"{tm_night_rain} %", f"{tm_night_humidity} %")

    console.print(td_table_day)
    console.print(td_table_temps)
    console.print(tm_table_day)
    console.print(tm_table_temps)

# Sort alphabetically geocode_cache.json file for efficient usage.
def sort_json():
    with open(GEOCODE, "r", encoding="utf-8") as f:
        data = json.load(f)
        sorted_data = dict(sorted(data.items()))
        with open(GEOCODE, "w", encoding="utf-8") as f:
                json.dump(sorted_data, f, indent=2, ensure_ascii=False)
        print("JSON successfuly sorted!")


def main():
    import inspect
    try:
        location = "cali, colombia"
        lat, lon = get_geocode(location.strip().lower())
        print(f"{get_current_weather(lat, lon)}".strip("()"))
    except (ValueError, IndexError, TypeError, HTTPError, requests.RequestException) as e:
        func_name = inspect.currentframe().f_code.co_name
        print(f"Error processing data for '{location}': {e} in {func_name}()")
if __name__ == "__main__":
    main()