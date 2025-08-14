from gmaps_package import get_current_weather
import time
from rich.console import Console
from rich import print

def get_default_forecast(lat, long): # lat="52.094523",long= "4.279590" for default location 'HOME'
    console = Console()
    print("")
    print("")
    console.rule("[bold red]WELCOME TO BLOOM & SKY APP", align="left")
    print("A Python application for gardening and health recommendations based on the weather forecast.\n")
    
    time.sleep(2)
    is_day, temp, description, humidity, rain_prob = get_current_weather(lat,long) # Forecast for home
    
    return is_day, temp, description, humidity, rain_prob