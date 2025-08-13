import googlemaps, requests, json #type: ignore
from rich.console import Console #type: ignore
from rich.table import Table #type: ignore

#Script to request a location geocode data(lat and long) from Google Maps Geocoding API

def get_geocode(location) -> tuple:

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"
    gmaps = googlemaps.Client(key=API_key)

    # Location geocoding
    geocode_result = gmaps.geocode(location) # implement 'statenkwartier, zuid holland.' by default

    lat, long = tuple(geocode_result[0]["geometry"]["location"].values())

    return lat, long
   
#with open("default_location.json", "w", encoding="utf-8") as f:
#    json.dump(default, f, indent=4, ensure_ascii=False)

#Script to request pollen data from Google Maps Pollen API. It returns grass, weed and trees risk levels in a given location.

def get_pollen(lat, long):

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"

    url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_key}&location.longitude={long}&location.latitude={lat}&days=1"

    response = requests.get(url)

    try:
        data = response.json()
        
        daily = data["dailyInfo"][0]

        
        risk_levels = {
        'GRASS': 'unknown',
        'WEED': 'unknown',
        'TREE': 'unknown'
        }

        # Search in pollenTypeInfo
        for item in daily.get('pollenTypeInfo', []):
            code = item.get('code')
            index_info = item.get('indexInfo')
            if code in risk_levels and index_info:
                risk_levels[code] = index_info.get('category', 'unknown')

        return risk_levels['GRASS'], risk_levels['WEED'], risk_levels['TREE']
        
        #with open("daily.json", "w", encoding="utf-8") as f:
            #json.dump(daily, f, indent=4, ensure_ascii=False)
    except requests.RequestException as r:
        print(f"Error fetching pollen data: {r}.")

#print(get_pollen(location="den haag, nl"))

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
    content = response.json()

    is_day = content["isDaytime"]
    temp = content["temperature"].get("degrees", {})
    description = content["weatherCondition"].get("description", {}).get("text", {})
    humidity = content["relativeHumidity"]
    rain_prob = content["precipitation"].get("probability", {}).get("percent", {})

    #with open("today.json", "w", encoding="utf-8") as f:
     #      json.dump(content, f, indent=4, ensure_ascii=False)

    #get_current_weather(52.0945228, 4.279590499999999)

    return is_day, round(temp), description.title(), round(humidity), round(rain_prob)


#Script to get weather forecast (today and tomorrow) from Google Maps Weather API.

def extended_forecast(location, lat, long):
    
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
        td_table_temps = Table(title="Temperatures", header_style="bold red")

        td_table_temps.add_column("Min. 🌡 (°C)", justify="center")
        td_table_temps.add_column("Max. 🌡 (°C)", justify="center")
        td_table_temps.add_row(str(td_min_temp), str(td_max_temp))

        td_table_day.add_column("🕓", justify="center")
        td_table_day.add_column("📢", justify="center")
        td_table_day.add_column("💧(%)", justify="center")
        td_table_day.add_column("Humidity (%)", justify="center")

        td_table_day.add_row("Day Time", str(td_day_descrip), str(td_day_rain), str(td_day_humidity))
        td_table_day.add_row("Night Time", str(td_night_descrip), str(td_night_rain), str(td_night_humidity))

        #Tables for tomorrow's weather forecast
        tm_table_day = Table(title=f"\n{location} ➜  Tomorrow's Forecast:\n", title_style="bold on yellow", header_style="bold red")
        tm_table_temps = Table(title="Temperatures", header_style="bold red", title_style="bold")

        tm_table_temps.add_column("Min. 🌡 (°C)", justify="center")
        tm_table_temps.add_column("Max. 🌡 (°C)", justify="center")
        tm_table_temps.add_row(str(tm_min_temp), str(tm_max_temp))

        tm_table_day.add_column("🕓", justify="center")
        tm_table_day.add_column("📢", justify="center")
        tm_table_day.add_column("💧(%)", justify="center")
        tm_table_day.add_column("Humidity (%)", justify="center")

        tm_table_day.add_row("Day Time", str(tm_day_descrip), str(tm_day_rain), str(tm_day_humidity))
        tm_table_day.add_row("Night Time", str(tm_night_descrip), str(tm_night_rain), str(tm_night_humidity))

        return console.print(td_table_day), console.print(td_table_temps), console.print(tm_table_day), console.print(tm_table_temps)

    except requests.RequestException as r:
            print(f"Error fetching weather data: {r}")
        
