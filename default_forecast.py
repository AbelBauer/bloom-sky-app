from gmaps_package import get_current_weather

def get_default_forecast(lat, long): # lat="52.0945228",long="4.2795905" for default location 'HOME'
    is_day, temp, description, humidity, rain_prob = get_current_weather(lat,long) # get weather forecast for home
    return is_day, temp, description, humidity, rain_prob