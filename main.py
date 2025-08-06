import time, sys
import requests # type: ignore

from helpers import get_recommendation, prompt_location
from get_weather import get_weather
from pollen import get_pollen
from display_weather_table import print_table

#1 Greetings and App's start.
print("""
===============================================================
===============================================================

	       ⁍ WELCOME TO BLOOM & SKY APP ⁌

    A Python application for gardening, outfit and health 
        recommendations based on forecasted weather.
          
===============================================================
===============================================================
""")
location, latitude, longitude = prompt_location()
        
#2 fetch data from open-meteo.com API

is_day, temp, rain_prob, humidity = get_weather(latitude, longitude)

#3 Fetch pollen data from getambee.com API

grass, tree, weed = get_pollen(location)

#4 Display today's forecast for chosen location.

print_table(location, is_day, temp, rain_prob, humidity)

#5 Display recommendations

print(get_recommendation(is_day, temp, rain_prob, humidity, grass, tree, weed))

# Tomorrow info
#daily = response.Daily()
#tomorrow_max_temp = daily.Variables(0).Values()[1]  # Index 1 = tomorrow
#tomorrow_min_temp = daily.Variables(1).Values()[1]
#tomorrow_precip_chance = daily.Variables(2).Values()[1]