# Print today's compact weather forecast for chosen location. Table nicely formatted using 'rich' package.

from rich.console import Console #type: ignore
from rich.table import Table #type: ignore

def time_to_emoji(value): # Convert is_day to emoji
    if value == False:
        return "🌘"
    else:
        return "🌞"

def print_table(location, is_day, temp, description, rain_prob, humidity):

    console = Console()
    table = Table(title=f"\n{location} ➜  Now:\n", title_style="bold on green", header_style="bold red")

    table.add_column("Time of Day", justify="center")
    table.add_column("📝", justify="center")
    table.add_column("Temp. 🌡", justify="center")
    table.add_column("Rain prob. 🌦️ ", justify="center")
    table.add_column("Humidity 💧", justify="center")

    table.add_row(time_to_emoji(is_day), str(description), f"{str(temp)}°C",
                f"{str(rain_prob)} %", f"{str(humidity)} %")

    return console.print(table)