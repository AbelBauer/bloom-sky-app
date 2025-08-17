from gmaps_package import get_current_weather

def get_default_forecast(lat, long): # lat="52.094523",long= "4.279590" for default location 'HOME'
    is_day, temp, description, humidity, rain_prob = get_current_weather(lat,long) # Forecast for home    
    return is_day, temp, description, humidity, rain_prob