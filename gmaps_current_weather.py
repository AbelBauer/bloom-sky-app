#Script to get current weather forecast from Google Maps Weather API.

import requests, json

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


    return is_day, round(temp), description.lower(), round(humidity), round(rain_prob)

    #with open("today.json", "w", encoding="utf-8") as f:
     #      json.dump(content, f, indent=4, ensure_ascii=False)

#get_current_weather(52.0945228, 4.279590499999999)