from openmeteo_api import hourly_dataframe, daily_dataframe

# Save hourly forecast to JSON
hourly_dataframe.to_json("hourly_forecast.json", orient="records", date_format="iso", indent=2)

# Save daily forecast to JSON
daily_dataframe.to_json("daily_forecast.json", orient="records", date_format="iso", indent=2)
