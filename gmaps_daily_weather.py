#Script to get today's weather forecast from Google Maps Weather API.

import requests

def get_todays_forecast(lat, long):

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"

    url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_key}&location.latitude={lat}&location.longitude={long}&days=1"

    response = requests.get(url)
    content = response.json()

    try:

        forecast_today = content.get('forecastDays', [])
        if not forecast_today:
            return 'unknown', 'unknown'
        
        today = forecast_today[0]

        day_time_f = today.get('daytimeForecast', {}).get('weatherCondition', {}).get('description', {}).get('text', 'unknown')
        day_time_humidity = today.get('daytimeForecast', {}).get('relativeHumidity', {})
        day_time_rain = today.get('daytimeForecast', {}).get('precipitation', {}).get('probability', {}).get('percent', {})
        night_time_f = today.get('nighttimeForecast', {}).get('weatherCondition', {}).get('description', {}).get('text', 'unknown')
        night_time_humidity = today.get('nighttimeForecast', {}).get('relativeHumidity', {})
        night_time_rain = today.get('nighttimeForecast', {}).get('precipitation', {}).get('probability', {}).get('percent', {})
        min_temp = today.get('minTemperature', {}).get('degrees', {})
        max_temp = today.get('maxTemperature', {}).get('degrees', {})

        return day_time_f, day_time_rain, day_time_humidity, night_time_f, night_time_humidity, night_time_rain, min_temp, max_temp
    
    except requests.RequestException as r:
        print(f"Error fetching weather data: {r}")

    #with open("today.json", "w", encoding="utf-8") as f:
    #       json.dump(content, f, indent=4, ensure_ascii=False)

#print(get_todays_forecast(52.0945228, 4.279590499999999))