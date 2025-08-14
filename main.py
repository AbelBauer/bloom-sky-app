from helpers import main_menu, get_recommendation
from default_forecast import get_default_forecast
from display_weather_table import print_table
from gmaps_pollen import get_pollen
from rich import print
from rich.panel import Panel

# Display 'HOME' info as default
is_day, temp, description, humidity, rain_prob = get_default_forecast(lat="52.094523",long= "4.279590")
grass, weed, trees = get_pollen(lat="52.094523",long= "4.279590")

print("")
print_table("Statenkwartier, Zuid Holland (Home).", is_day, temp, description, humidity, rain_prob)
print(Panel.fit(f"{get_recommendation(is_day, temp, rain_prob, humidity, grass, trees, weed)}"))

# Main menu...
main_menu()
