import googlemaps, requests  # type: ignore
from googlemaps.exceptions import HTTPError
from rich.console import Console  # type: ignore
from rich.table import Table  # type: ignore
from diskcache import Cache
from difflib import get_close_matches
from dotenv import load_dotenv
import os

# Initialize local cache for geocoding
cache = Cache("gmaps_module_cache")

# Get geocode (lat, long) for a location, with persistent caching
def get_geocode(location: str):
    if location in cache:
        lat, long = cache[location]
        return lat, long

    load_dotenv()
    API_key = os.getenv("GMAPS_API_KEY")
    gmaps = googlemaps.Client(key=API_key)

    try:
        geocode_result = gmaps.geocode(location)
        lat, long = tuple(geocode_result[0]["geometry"]["location"].values())
        cache[location] = (lat, long)
        return lat, long
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
def get_current_weather(lat: float, long: float) -> tuple[bool, int, str, int, int]:
    load_dotenv()
    API_key = os.getenv("GMAPS_API_KEY")
    url = f"https://weather.googleapis.com/v1/currentConditions:lookup?key={API_key}&location.latitude={lat}&location.longitude={long}"
    key = (lat, long)
    if key in cache:
        return cache[key]
    
    response = requests.get(url)

    try:
        content = response.json()
        is_day = content.get("isDaytime", "Unknown")
        temp = content.get("temperature", {}).get("degrees", "Unknown")
        description = content.get("weatherCondition", {}).get("description", {}).get("text", "Unknown")
        humidity = content.get("relativeHumidity", "Unknown")
        rain_prob = content.get("precipitation", {}).get("probability", {}).get("percent", "Unknown")

        result = (bool(is_day), int(temp), str(description.title()), int(humidity), int(rain_prob))
        cache[key] = result
        return result

    except (TypeError, ValueError, googlemaps.exceptions.HTTPError) as e:
        print(f"Error fetching current weather data: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"

# Get extended forecast (today and tomorrow)
def get_extended_forecast(location: str, lat: float, long: float):
    load_dotenv()
    API_key = os.getenv("GMAPS_API_KEY")
    url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_key}&location.latitude={lat}&location.longitude={long}&days=2"

    try:
        
        key = (location.lower(), lat, long)
        if key in cache:
            cached = cache[key]
            td_result = cached["today"]
            tm_result = cached["tomorrow"]
        else:
            response = requests.get(url)
            response.raise_for_status()
            content = response.json()
            forecast = content.get('forecastDays', [])
            if len(forecast) < 2:
                return "Error fetching weather forecast data"

            td_result = extract_forecast(forecast[0])
            tm_result = extract_forecast(forecast[1])
            cache[key] = {"today": td_result, "tomorrow": tm_result}

        # Unpack today's forecast
        td_day_descrip, td_day_rain, td_day_humidity, td_night_descrip, td_night_humidity, td_night_rain, td_min_temp, td_max_temp = td_result
        # Unpack tomorrow's forecast
        tm_day_descrip, tm_day_rain, tm_day_humidity, tm_night_descrip, tm_night_humidity, tm_night_rain, tm_min_temp, tm_max_temp = tm_result

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
        td_table_day.add_row("Day Time", td_day_descrip, f"{td_day_rain} %", f"{td_day_humidity} %")
        td_table_day.add_row("Night Time", td_night_descrip, f"{td_night_rain} %", f"{td_night_humidity} %")

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
        tm_table_day.add_row("Day Time", tm_day_descrip, f"{tm_day_rain} %", f"{tm_day_humidity} %")
        tm_table_day.add_row("Night Time", tm_night_descrip, f"{tm_night_rain} %", f"{tm_night_humidity} %")

        console.print(td_table_day)
        console.print(td_table_temps)
        console.print(tm_table_day)
        console.print(tm_table_temps)

    except (requests.RequestException, HTTPError) as r:
        print(f"Error fetching extended forecast: {r}")
    except KeyError as k:
        print(f"Error processing forecast data: {k}")
