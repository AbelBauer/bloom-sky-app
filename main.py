from helpers import main_menu, get_recommendation
from default_forecast import get_default_forecast
from display_weather_table import print_table
from pollen import get_pollen
import time
from rich.console import Console
from rich import print
from rich.panel import Panel

is_day, temp, description, humidity, rain_prob = get_default_forecast(lat="52.094523",long= "4.279590")
grass, tree, weed = get_pollen(location="Statenkwartier, Zuid Holland")

print_table("Statenkwartier, Zuid Holland (Home).", is_day, temp, description, humidity, rain_prob)
time.sleep(1)
print(Panel(f"\n{get_recommendation(is_day, temp, rain_prob, humidity, grass, tree, weed)}"))

main_menu()
