from gmaps_package import get_current_weather
from Api_limiter_class import ApiLimiter

limiter = ApiLimiter()

@limiter.guard()
def get_default_forecast():
    # Get and unpack weather forecast variables for home location.
    lat, lon = 52.0945228, 4.2795905 # coordinates for 'HOME' location(default) 
    is_day, temp, description, rain_prob, humidity = get_current_weather(lat, lon)
    return is_day, temp, description, rain_prob, humidity