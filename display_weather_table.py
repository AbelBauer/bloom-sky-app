# Print today's compact weather forecast for chosen location. Table nicely formatted using 'rich' package.

from rich.console import Console #type: ignore
from rich.table import Table #type: ignore
from helpers import time_to_emoji

def print_table(location, is_day, temp, rain_prob, humidity):

    console = Console()
    table = Table(title=f"\n{location} ➱  Today:\n")

    table.add_column("Time of Day", justify="center")
    table.add_column("Temp (°C)", justify="center")
    table.add_column("Rain (%)", justify="center")
    table.add_column("Humidity (%)", justify="center")

    table.add_row(time_to_emoji(is_day), str(round(temp)),
                str(round(rain_prob)), str(round(humidity)))

    return console.print(table)