import googlemaps, requests, json #type: ignore
from googlemaps.exceptions import HTTPError
from rich.console import Console #type: ignore
from rich.table import Table #type: ignore

#Script to request a location geocode data(lat and long) from Google Maps Geocoding API

def get_geocode(location) -> tuple:

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"
    gmaps = googlemaps.Client(key=API_key)

    try:
        # Location geocoding
        geocode_result = gmaps.geocode(location) # implement 'statenkwartier, zuid holland.' by default

        lat, long = tuple(geocode_result[0]["geometry"]["location"].values())

        return lat, long
    except (IndexError, HTTPError):
        raise

#with open("default_location.json", "w", encoding="utf-8") as f:
#    json.dump(default, f, indent=4, ensure_ascii=False)


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


#Script to get current weather forecast from Google Maps Weather API.

def get_current_weather(lat, long):

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"
        
    url = f"https://weather.googleapis.com/v1/currentConditions:lookup?key={API_key}&location.latitude={lat}&location.longitude={long}"

    response = requests.get(url)

    try:        
        content = response.json()

        is_day = content.get("isDaytime", "Unknown")
        temp = content.get("temperature", {}).get("degrees", "Unknown")
        description = content.get("weatherCondition", {}).get("description", {}).get("text", "Unknown")
        humidity = content.get("relativeHumidity", "Unknown")
        rain_prob = content.get("precipitation", {}).get("probability", {}).get("percent", "Unknown")

        #with open("today.json", "w", encoding="utf-8") as f:
        #      json.dump(content, f, indent=4, ensure_ascii=False)

        return bool(is_day), int(temp), str(description.title()), int(humidity), int(rain_prob)
        #print(get_current_weather(52.0945228, 4.279590499999999))
    
    except (TypeError, ValueError, googlemaps.exceptions.HTTPError) as e:
        print(f"Error fetching current weather data: {e}")
        return "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"


#Script to get weather forecast (today and tomorrow) from Google Maps Weather API.

def get_extended_forecast(location, lat, long):
    
    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"

    url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_key}&location.latitude={lat}&location.longitude={long}&days=2"

    response = requests.get(url)
    content = response.json()

    try:

        forecast = content.get('forecastDays', [])
        if len(forecast) < 2:
            return "Error fetching weather forecast data"
        
        # today's forecast variables
        td_day_descrip, td_day_rain, td_day_humidity, td_night_descrip, td_night_humidity, td_night_rain, td_min_temp, td_max_temp  = extract_forecast(forecast[0])
        #tomorrow's forecast variables
        tm_day_descrip, tm_day_rain, tm_day_humidity, tm_night_descrip, tm_night_humidity, tm_night_rain, tm_min_temp, tm_max_temp = extract_forecast(forecast[1])

   
    
        console = Console()
        #Tables for today's weather forecast
        td_table_day = Table(title=f"\n{location} ➜  Today's Forecast:\n", title_style="bold on yellow", header_style="bold red")
        td_table_temps = Table(title="Temperatures", header_style="bold red", title_style="bold")

        td_table_temps.add_column("Min. 🌡", justify="center")
        td_table_temps.add_column("Max. 🌡", justify="center")
        td_table_temps.add_row(f"{str(td_min_temp)}°C", f"{str(td_max_temp)}°C")

        td_table_day.add_column("🕓", justify="center")
        td_table_day.add_column("📝", justify="center")
        td_table_day.add_column("Rain Prob. 🌦️ ", justify="center")
        td_table_day.add_column("Humidity 💧", justify="center")

        td_table_day.add_row("Day Time", str(td_day_descrip), f"{str(td_day_rain)} %", f"{str(td_day_humidity)} %")
        td_table_day.add_row("Night Time", str(td_night_descrip), f"{str(td_night_rain)} %", f"{str(td_night_humidity)} %")

        #Tables for tomorrow's weather forecast
        tm_table_day = Table(title=f"\n{location} ➜  Tomorrow's Forecast:\n", title_style="bold on yellow", header_style="bold red")
        tm_table_temps = Table(title="Temperatures", header_style="bold red", title_style="bold")

        tm_table_temps.add_column("Min. 🌡", justify="center")
        tm_table_temps.add_column("Max. 🌡", justify="center")
        tm_table_temps.add_row(f"{str(tm_min_temp)}°C", f"{str(tm_max_temp)}°C")

        tm_table_day.add_column("🕓", justify="center")
        tm_table_day.add_column("📝", justify="center")
        tm_table_day.add_column("Rain Prob. 🌦️ ", justify="center")
        tm_table_day.add_column("Humidity 💧", justify="center")

        tm_table_day.add_row("Day Time", str(tm_day_descrip),f"{str(tm_day_rain)} %", f"{str(tm_day_humidity)} %")
        tm_table_day.add_row(f"Night Time", str(tm_night_descrip), f"{str(tm_night_rain)} %", f"{str(tm_night_humidity)} %")

        return console.print(td_table_day), console.print(td_table_temps), console.print(tm_table_day), console.print(tm_table_temps)

    except (requests.RequestException, googlemaps.exceptions.HTTPError) as r:
        print(f"Error fetching extended forecast: {r}")
    except KeyError as k:
        print(f"Error fetching extended forecast: {k}")
        
