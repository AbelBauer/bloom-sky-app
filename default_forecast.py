from pollen import get_pollen
from display_weather_table import print_table
from helpers import get_recommendation
from gmaps_package import get_current_weather
import time
from rich.console import Console
from rich import print
from rich.panel import Panel

def get_default_forecast(lat, long): # lat="52.094523",long= "4.279590" for default location
    console = Console()
    print("")
    print("")
    console.rule("[bold red]WELCOME TO BLOOM & SKY APP", align="left")
    print("")
    print("""
===============================================================
===============================================================

    A Python application for gardening, outfit and health 
        recommendations based on the weather forecast.
          
===============================================================
===============================================================
""")
    
    time.sleep(1)
    is_day, temp, description, humidity, rain_prob = get_current_weather(lat,long) # Forecast for home (Statenkwartier, Zuid Holland, NL)
    
    return is_day, temp, description, humidity, rain_prob