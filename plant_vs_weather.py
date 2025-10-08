'''
Bloom and Sky - Gardening Forecast & Plant Care Advisor

This module is the heart of Bloom and Sky's garden care intelligence. It blends real-time weather data with expressive plant care logic to help users 
make informed decisions about watering, placement, and protection. With support for diverse sunlight profiles and nuanced forecast parsing, it delivers 
personalized advice that feels both practical and conversational.

Overview:
---------
- Retrieves 2-day weather forecasts using the Google Weather API.
- Extracts and normalizes forecast data for analysis.
- Generates watering recommendations based on short-term humidity and precipitation trends.
- Evaluates sky conditions against plant sunlight preferences for today and tomorrow.
- Combines all insights into a conversational care advisory.
- Implements persistent caching to reduce API usage and improve performance.

Functions:
----------
get_forecast(location: str) → tuple  
    Retrieves today's and tomorrow's forecast data for the specified location. Uses caching to avoid redundant API calls.

extract(TODAY_data: list, TMW_data: list) → tuple  
    Unpacks and normalizes forecast data for both days. Converts strings to lowercase and returns key metrics for analysis.

recommend_watering(watering: str, TODAY_day_rain: int, TODAY_day_humidity: int, TODAY_night_rain: int, TODAY_night_humidity: int, 
                   TMW_day_rain: int, TMW_day_humidity: int, TMW_night_rain: int, TMW_night_humidity: int) → str  
    Returns a personalized watering recommendation based on short-term rain and humidity trends. 
    Considers both today's and tomorrow's conditions and adapts advice to the plant's watering profile ('minimum', 'average', 'frequent').

recommend_today_sunlight(sunlight: str, TODAY_day_sky: str) → str  
    Evaluates today's sky conditions against the plant's sunlight needs. 
    Returns a descriptive recommendation for placement and care based on light exposure compatibility.

recommend_tmw_sunlight(sunlight: str, TMW_day_sky: str) → str  
    Returns a descriptive recommendation for plant placement based on tomorrow's forecasted sky conditions. 
    Supports the same sunlight profiles as 'recommend_today_sunlight' and adapts advice to expected light availability.

recommend(watering: str, sunlight_today: str, sunlight_tomorrow: str) → str  
    Combines watering and sunlight recommendations into a single formatted string.

plant_weather_advisor(location: str, watering: str, sunlight: str) → str  
    Main advisory function. Retrieves forecast data, analyzes weather and light conditions, and returns a full care recommendation.

main() → None  
    CLI entry point for testing. Prompts the user for a location and prints the full plant care advisory.

gmaps_API_descr : list[str]  
    A reference list of supported weather descriptors used for matching forecast data to care logic.

Supported Sunlight Profiles:
----------------------------
- 'full sun', 'sun', 'full sun partial sun'
- 'full sun only if soil kept moist'
- 'part sun', 'part shade', 'partial shade'
- 'shade', 'full shade', 'deep shade'
- 'filtered shade'
- 'part sun/part shade', 'partial sun shade'
- 'deciduous shade (spring sun)'
- 'full sun partial sun shade'

Design Notes:
-------------
- Forecast data includes daytime and nighttime breakdowns for rain probability, humidity, and sky conditions.
- Watering logic aggregates values across both days to assess total moisture exposure.
- Sunlight recommendations are tailored to specific plant light profiles and matched against curated weather descriptors.
- Recommendations are phrased conversationally to enhance user engagement and readability.
- Caching is handled via 'extended_weather_cache.json' using helper functions from 'garden_care_guide'.

Limitations:
------------
- Assumes forecast data is complete and well-formed; missing keys may trigger fallback behavior.
- Sunlight compatibility logic is static and does not account for seasonal variation or indoor lighting conditions.
- Watering advice is generalized and may not suit all plant species or microclimates.
- Unexpected or unsupported weather descriptors may trigger fallback messaging.

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project
'''

import requests, os
from googlemaps.exceptions import HTTPError
from dotenv import load_dotenv
from gmaps_package import extract_forecast, get_geocode
from helper_functions import get_geocode
from garden_care_guide import load_cache, save_cache
from Api_limiter_class import ApiLimiter

EXTENDED_WEATHER = "extended_weather_cache.json"
limiter=ApiLimiter(daily_max_calls=100, filepath="gmaps_weather&plants_calls.json")

@limiter.guard(error_message="Gmaps Weather API quota reached!")
def get_forecast(location): # Get forecast for location. (get_extended_forecast variant for gardening section)

    # Get coordinates from location. Cache already implemented inside function.
    lat, lon = get_geocode(location) 

    cache = load_cache(EXTENDED_WEATHER)
    key = f"{float(lat):.7f}, {float(lon):.7f}"
    # Check cache first.
    if key in cache:
        today, tomorrow = cache[key]
    # Otherwise call API.
    else:
        try:
            load_dotenv()
            API_key = os.getenv("GMAPS_API_KEY")
            url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_key}&location.latitude={lat}&location.longitude={lon}&days=2"

            response = requests.get(url)
            content = response.json()
            forecast = content.get('forecastDays', [])
            if len(forecast) < 2:
                return "Error fetching weather forecast data"

            today = extract_forecast(forecast[0])
            tomorrow = extract_forecast(forecast[1])

            # Save locations forecast data in cache and log API call.
            limiter.record_call()
            save_cache(EXTENDED_WEATHER, {key: [today, tomorrow]})

        except (requests.RequestException, HTTPError) as r:
            print(f"Error fetching forecast data: {r}")
        except KeyError as k:
            print(f"Error processing forecast data: {k}")

    return today, tomorrow

def extract(TODAY_data, TMW_data):
    # Unpack today's forecast
    (
    TODAY_day_sky,
    TODAY_day_rain,
    TODAY_day_humidity,
    TODAY_night_sky,
    TODAY_night_rain,
    TODAY_night_humidity,
    TODAY_min_temp,
    TODAY_max_temp
 ) = tuple(item.lower() if isinstance(item, str) else item for item in TODAY_data)
    # Unpack tomorrow's forecast
    (TMW_day_sky,
     TMW_day_rain,
     TMW_day_humidity,
     TMW_night_sky,
     TMW_night_rain,
     TMW_night_humidity,
     TMW_min_temp,
     TMW_max_temp
    ) = tuple(item.lower() if isinstance(item, str) else item for item in TMW_data)

    return TODAY_day_sky, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity, TMW_day_sky, TMW_day_rain, TMW_day_humidity,  TMW_night_rain, TMW_night_humidity

def recommend_watering(watering, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity,
    TMW_day_rain, TMW_day_humidity, TMW_night_rain, TMW_night_humidity):

    # Aggregate values
    today_rain_total = TODAY_day_rain + TODAY_night_rain
    today_humidity_total = TODAY_day_humidity + TODAY_night_humidity
    tmw_rain_total = TMW_day_rain + TMW_night_rain
    tmw_humidity_total = TMW_day_humidity + TMW_night_humidity
    combined_rain = today_rain_total + tmw_rain_total
    combined_humidity = today_humidity_total + tmw_humidity_total

    # Heavy rain and high humidity today
    if today_rain_total > 70 and today_humidity_total > 80:
        if watering == "minimum":
            return "No need to lift the watering can. The sky's handling hydration duties today."
        elif watering == "average":
            return "Rain and humidity are teaming up. Let nature take care of your plant."
        elif watering == "frequent":
            return "Even thirsty plants deserve a break. Let the weather do the watering."

    # Dry today, wet tomorrow
    elif tmw_rain_total > 70 and today_rain_total < 30:
        if watering == "minimum":
            return "Dry now, wet later. Your plant can wait for tomorrow's downpour."
        elif watering == "average":
            return "Hold off if you can. Tomorrow's forecast looks promising."
        elif watering == "frequent":
            return "Your plant might be eager, but tomorrow's rain will do the trick."

    # Low humidity and low rain today
    elif today_humidity_total < 40 and today_rain_total < 30:
        if watering == "minimum":
            return "Dry air and dry skies. Your plant might be fine, but keep an eye out."
        elif watering == "average":
            return "Humidity's low and rain's missing. Your plant could use a drink."
        elif watering == "frequent":
            return "Feels like a desert out there. Time to give your plant a good soak."

    # High humidity, low rain today
    elif today_humidity_total > 80 and today_rain_total < 30:
        if watering == "minimum":
            return "Humidity's high, skies are dry. Your plant's probably coasting comfortably."
        elif watering == "average":
            return "Moist air, dry soil. A light misting should be enough."
        elif watering == "frequent":
            return "Your plant's expecting its usual spa day. A gentle mist will keep it happy."

    # Low rain and humidity across both days
    elif combined_rain < 40 and combined_humidity < 160:
        if watering == "minimum":
            return "Low moisture all around. Might be time to break the drought with a splash."
        elif watering == "average":
            return "Your plant's not getting much help from the sky. A solid watering session is in order."
        elif watering == "frequent":
            return "This is your moment. Your plant's craving hydration. Don't hold back!"

    # Dry skies, decent humidity today
    elif today_rain_total < 30 and tmw_rain_total < 30 and today_humidity_total > 70:
        if watering == "minimum":
            return "Dry skies but decent humidity. Your plant's probably fine."
        elif watering == "average":
            return "Humidity's helping, but a light watering wouldn't hurt."
        elif watering == "frequent":
            return "Your plant's expecting its usual pampering. Give it a gentle soak."

    # Rain tomorrow, humidity low both days
    elif tmw_rain_total > 70 and combined_humidity < 120:
        if watering == "minimum":
            return "Low humidity now, but rain's on the way. Your plant can wait."
        elif watering == "average":
            return "Tomorrow looks promising. Hold off the watering unless your plant's looking thirsty."
        elif watering == "frequent":
            return "Your plant's used to VIP hydration, but tomorrow's forecast looks good. Let it wait."

    # High humidity both days, minimal rain
    elif combined_humidity > 180 and combined_rain < 40:
        if watering == "minimum":
            return "Humidity's doing the heavy lifting. Your plant's probably fine without a drink."
        elif watering == "average":
            return "Moist air, dry soil. A light misting should keep your plant smiling."
        elif watering == "frequent":
            return "Feels like a steam room. Give it a mist and let it bask."

    # Mild rain and moderate humidity across both days
    elif 30 < combined_rain < 70 and 120 < combined_humidity < 180:
        if watering == "minimum":
            return "Conditions are mild. Your plant's probably fine, but check the soil just in case."
        elif watering == "average":
            return "Moderate moisture in the air and sky. A light watering should do."
        elif watering == "frequent":
            return "Your plant's used to regular care. A gentle top-up will keep it content."

    # Fallback
    else:
        return "Weather's playing it cool. Check the soil and trust your plant-parent instincts."

# Sunlight recommendations based on plant needs and actual weather
def recommend_today_sunlight(sunlight, TODAY_day_sky):
    if sunlight:
        sunlight = sunlight.lower().strip()
    else:
        return "Sunlight needs unavailable for this plant. For today: monitor your plant and adjust care as needed."

    if TODAY_day_sky:
        TODAY_day_sky = TODAY_day_sky.lower().strip()
    else:
        return "Skies condition unavailable. For today: monitor your plant and adjust care as needed."


    # Today sky conditions for full sun plants
    if sunlight in ["full sun", "sun", "full sun partial sun"]:
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Clear expected: perfect day for sun worship. Your plant's soaking up the rays."
        elif TODAY_day_sky in ["partly cloudy", "mostly cloudy"]:
            today = "Partly cloudy expected: your sun-loving plant might pout today. Keep an eye on leaf behavior."
        elif TODAY_day_sky in ["cloudy", "overcast"]:
            today = "Cloudy expected: not ideal for full sun plants. Ensure the area receives enough ambient light."
        elif TODAY_day_sky in ["light rain", "rain", "heavy rain", "rain showers", "scattered showers", "chance of showers"]:
            today = "Rain expected: your full sun plant might feel gloomy. Monitor for drooping or leaf stress."
        elif TODAY_day_sky in ["thunderstorm", "thundershower", "heavy thunderstorm", "scattered thunderstorms"]:
            today = "Thunderstorm expected: not much light today. Your plant may need extra warmth or support."
        elif TODAY_day_sky in ["hail", "hail showers"]:
            today = "Hail expected: protect your plant from damage and low light conditions."
        elif TODAY_day_sky in ["snow", "light snow", "heavy snow", "snow showers", "scattered snow showers"]:
            today = "Snow expected: your sun-loving plant won't be thrilled. Keep it warm and well-lit indoors."
        else:
            today = "Sky conditions unclear today: check your plant's response and adjust light exposure as needed."

    elif sunlight == "full sun only if soil kept moist":
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Strong sun today: your plant can thrive, but only if the soil stays consistently moist. Don't let it dry out."
        elif TODAY_day_sky in ["partly cloudy", "mostly cloudy"]:
            today = "Filtered light today: good conditions for moisture-sensitive sun lovers. Keep the soil damp."
        elif TODAY_day_sky in ["cloudy", "overcast"]:
            today = "Low light today: your plant won't get full sun, but maintaining soil moisture is still key."
        elif TODAY_day_sky in ["light rain", "rain", "scattered showers", "showers"]:
            today = "Rain incoming: perfect for plants that need moist soil to handle full sun. Let nature do the watering."
        elif TODAY_day_sky in ["snow", "light snow", "flurries"]:
            today = "Cold and snowy: full sun isn't a concern, but moisture retention is still important if indoors."
        elif TODAY_day_sky in ["thunderstorm", "t-storms", "severe thunderstorms"]:
            today = "Stormy weather: keep your plant protected and ensure the soil drains well while staying moist."
        elif TODAY_day_sky in ["fog", "haze", "smoke"]:
            today = "Low visibility and weak sunlight: not ideal for full sun plants, but soil moisture remains crucial."
        else:
            today = "Unusual conditions today: monitor both light and soil moisture closely to keep your plant happy."


    # Today sky conditions for part sun/part shade plants
    elif sunlight in ["part sun", "part shade", "partial shade"]:
        if TODAY_day_sky in ["partly cloudy", "mostly cloudy", "cloudy"]:
            today = "Partly cloudy expected: ideal filtered light today. Your plant's getting a gentle glow."
        elif TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Sunny expected: bright skies ahead. Your plant might need a break from the spotlight."
        elif TODAY_day_sky in ["light rain", "rain", "heavy rain", "rain showers", "scattered showers", "chance of showers"]:
            today = "Rain expected: soft light and moisture. Your plant should be quite content."
        elif TODAY_day_sky in ["thunderstorm", "thundershower", "heavy thunderstorm", "scattered thunderstorms"]:
            today = "Thunderstorm expected: low light and high drama. Keep an eye on leaf behavior."
        elif TODAY_day_sky in ["hail", "hail showers"]:
            today = "Hail expected: protect your plant from sudden light changes and physical damage."
        elif TODAY_day_sky in ["snow", "light snow", "heavy snow", "snow showers", "scattered snow showers"]:
            today = "Snow expected: your plant may enjoy the soft light but keep it warm and dry."
        else:
            today = "Sky conditions unclear today: observe how your plant responds and adjust placement if needed."

    # Today sky conditions for shade/full shade plants
    elif sunlight in ["shade", "full shade", "deep shade"]:
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny", "partly cloudy"]:
            today = "Sunny expected: too much light for a shade-seeker. Consider moving it to a cooler corner."
        elif TODAY_day_sky in ["cloudy", "mostly cloudy", "overcast"]:
            today = "Cloudy expected: perfect low-light conditions. Your plant's in its comfort zone."
        elif TODAY_day_sky in ["light rain", "rain", "heavy rain", "rain showers", "scattered showers", "chance of showers"]:
            today = "Rain expected: soft light and moisture—ideal for shade-loving plants."
        elif TODAY_day_sky in ["thunderstorm", "thundershower", "scattered thunderstorms", "heavy thunderstorm"]:
            today = "Thunderstorm expected today : low light and high humidity. Your plant should be just fine."
        elif TODAY_day_sky in ["hail", "hail showers"]:
            today = "Hail expected: protect your plant from sudden cold and physical damage."
        elif TODAY_day_sky in ["snow", "light snow", "heavy snow", "snow showers", "scattered snow showers"]:
            today = "Snow expected: low light and cool temps, your shade plant will likely be comfortable."
        else:
            today = "Sky conditions unclear today: keep your shade plant in a stable spot and monitor for stress."

    elif sunlight == "filtered shade":
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Strong light today: filtered shade is essential. Keep your plant behind foliage or sheer curtains."
        elif TODAY_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            today = "Soft light today: filtered shade plants will be comfortable without extra shielding."
        elif TODAY_day_sky in [
            "light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"
        ]:
            today = "Rainy conditions: filtered light will be minimal. Keep soil well-drained and avoid soggy roots."
        elif TODAY_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            today = "Stormy weather: protect from wind and erratic moisture. Filtered light will be scarce."
        elif TODAY_day_sky in [
            "snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"
        ]:
            today = "Snowy skies: filtered shade plants may struggle with low light. Keep them warm and bright indoors."
        elif TODAY_day_sky in ["fog", "mist", "haze"]:
            today = "Low visibility today: filtered light may not be enough. Consider supplemental lighting indoors."
        elif TODAY_day_sky in ["windy", "hail", "hail showers"]:
            today = "Harsh conditions: protect your plant from wind or impact. Light levels may vary."
        else:
            today = "Uncertain skies: maintain filtered exposure and adjust if light drops too low."

    elif sunlight in ["part sun/part shade", "partial sun shade"]:
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Bright day ahead: give your plant a few hours of direct sun, then retreat to shade."
        elif TODAY_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            today = "Perfect balance of light and shade today. Your plant will be in its element."
        elif TODAY_day_sky in ["fog", "mist", "haze"]:
            today = "Low visibility today: your plant may need a brighter spot to compensate."
        elif TODAY_day_sky in [
            "light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"
        ]:
            today = "Rainy skies: your plant may not get its sun quota, but moisture is welcome."
        elif TODAY_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            today = "Stormy conditions: protect your plant from wind and keep it shaded."
        elif TODAY_day_sky in [
            "snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"
        ]:
            today = "Snowy skies: light will be limited. Your plant may need a brighter indoor spot."
        elif TODAY_day_sky in ["windy", "hail", "hail showers"]:
            today = "Wind or hail expected: shield your plant and avoid direct exposure."
        else:
            today = "Mixed conditions: partial exposure should be fine. Just avoid extremes."

    elif sunlight == "deciduous shade (spring sun)":
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Spring sun is welcome today—if trees are bare, let your plant enjoy the light. Otherwise, keep it shaded."
        elif TODAY_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            today = "Soft light today: good for transitional shade lovers. No extra care needed."
        elif TODAY_day_sky in ["fog", "mist", "haze"]:
            today = "Low light today: your plant may want a brighter spot if spring sun is expected."
        elif TODAY_day_sky in [
            "light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"
        ]:
            today = "Rainy skies: your plant may miss its spring sun moment. Keep it near a bright window."
        elif TODAY_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            today = "Stormy weather: protect your plant and avoid placing it near exposed windows."
        elif TODAY_day_sky in [
            "snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"
        ]:
            today = "Snowy skies: spring sun won't reach your plant today. Keep it warm and well lit indoors."
        elif TODAY_day_sky in ["windy", "hail", "hail showers"]:
            today = "Wind or hail expected: protect your plant from sudden exposure or damage."
        else:
            today = "Mixed conditions: adjust based on tree cover and light availability."

    elif sunlight == "full sun partial sun shade":
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny", "partly cloudy"]:
            today = "Bright day ahead: your plant can handle it, but monitor for signs of stress in peak sun."
        elif TODAY_day_sky in ["mostly cloudy", "cloudy", "overcast"]:
            today = "Balanced light today: your plant's flexible needs will be well met."
        elif TODAY_day_sky in ["fog", "mist", "haze"]:
            today = "Dim skies today: not ideal, but your plant's adaptable. No major concerns."
        elif TODAY_day_sky in [
            "light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"
        ]:
            today = "Rainy conditions: light will be limited, but your plant will appreciate the moisture."
        elif TODAY_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            today = "Stormy weather: protect your plant from wind and monitor for waterlogging."
        elif TODAY_day_sky in [
            "snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"
        ]:
            today = "Snowy skies: your plant won't get much light, but it's adaptable. Keep it warm and dry."
        elif TODAY_day_sky in ["windy", "hail", "hail showers"]:
            today = "Wind or hail expected: shield your plant and check for leaf damage."
        else:
            today = "Mixed conditions: your plant's versatility makes care easy."

    # Fallback for unrecognized sunlight values
    else:
        today = "Sunlight preference not recognized. For today: monitor your plant and adjust care as needed."

    return today

def recommend_tmw_sunlight(sunlight, TMW_day_sky):
    if sunlight:
        sunlight = sunlight.lower().strip()
    else:
        return "Sunlight needs unavailable for this plant. For tomorrow: monitor your plant and adjust care as needed."

    if TMW_day_sky:
        TMW_day_sky = TMW_day_sky.lower().strip()
    else:
        return "Skies condition unavailable. For tomorrow: monitor your plant and adjust care as needed."

    if sunlight in ["full sun", "sun", "full sun partial sun"]:
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny", "partly cloudy"]:
            tomorrow = "Tomorrow's skies are bright: ideal for sun-hungry plants. Let them bask and thrive."
        elif TMW_day_sky in ["cloudy", "mostly cloudy", "overcast"]:
            tomorrow = "Clouds ahead: not harmful, but your sun-lover might feel underfed. Make sure the space gets sufficient natural light throughout the day."
        elif TMW_day_sky in ["light rain", "rain", "heavy rain", "rain showers", "scattered showers","chance of showers", "rain periodically heavy", "moderate to heavy rain"]:
            tomorrow = "Rain expected tomorrow: light levels will dip. If indoors, place near a window to catch stray rays."
        elif TMW_day_sky in ["thunderstorm", "scattered thunderstorms", "thundershower", "light thunderstorm rain", "heavy thunderstorm"]:
            tomorrow = "Stormy forecast for tomorrow: protect from wind, but keep near light. Tomorrow's sun will be shy."
        elif TMW_day_sky in ["fog", "haze", "mist"]:
            tomorrow = "Low visibility tomorrow: your plant may miss its solar fix. Brighten its day with artificial light."
        else:
            tomorrow = "Tomorrow's light is uncertain. Keep your sun-lover in a bright, stable spot just in case."

    elif sunlight == "full sun only if soil kept moist":
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Tomorrow's sun will be strong: your plant can thrive, but only if the soil stays consistently moist. Don't let it dry out."
        elif TMW_day_sky in ["partly cloudy", "mostly cloudy"]:
            tomorrow = "Filtered light tomorrow: good conditions for moisture-sensitive sun lovers. Keep the soil damp."
        elif TMW_day_sky in ["cloudy", "overcast"]:
            tomorrow = "Tomorrow brings softer light. Your plant won't bask in full sun, but keeping the soil moist remains essential for its well-being."
        elif TMW_day_sky in ["light rain", "rain", "scattered showers", "showers",
            "chance of showers", "rain periodically heavy", "moderate to heavy rain", "heavy rain"]:
            tomorrow = "Rain expected tomorrow: perfect for plants that need moist soil to handle full sun. Let nature do the watering."
        elif TMW_day_sky in ["snow", "light snow", "light snow showers", "snow showers",
            "snowstorm", "snow periodically heavy", "heavy snow", "heavy snow storm", "blowing snow"]:
            tomorrow = "Cold and snowy condition tomorrow: full sun won't be an issue, but moisture retention is still important if indoors."
        elif TMW_day_sky in ["thunderstorm", "scattered thunderstorms", "thundershower",
            "light thunderstorm rain", "heavy thunderstorm"]:
            tomorrow = "Stormy forecast for tomorrow: protect your plant and ensure the soil drains well while staying moist."
        elif TMW_day_sky in ["fog", "haze", "mist"]:
            tomorrow = "Low visibility tomorrow: not much light, but soil moisture still matters. Keep it damp and stable."
        elif TMW_day_sky in ["windy", "wind and rain"]:
            tomorrow = "Windy conditions ahead: full sun may be tolerable, but drying winds mean moisture is critical."
        elif TMW_day_sky in ["hail", "hail showers"]:
            tomorrow = "Hail expected tomorrow: protect your plant from damage and monitor soil moisture after impact."
        else:
            tomorrow = "Tomorrow's conditions are unclear. Keep soil moist and adjust light exposure based on how your plant responds."

    elif sunlight in ["part sun", "part shade", "partial shade"]:
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Skies are clear today, so your part-shade plant might get more sun than usual. Let it chill under a leafy neighbor " \
            "during peak hours to avoid leaf stress, and check soil moisture: it may dry out faster than expected."
        elif TMW_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            tomorrow = "Balanced skies ahead: tomorrow your plant will enjoy gentle light. No extra care needed."
        elif TMW_day_sky in ["light rain", "light to moderate rain", "rain showers", "scattered showers", "chance of showers"]:
            tomorrow = "Soft rain tomorrow: ideal for these light-sensitive plants. Let nature do the watering."
        elif TMW_day_sky in ["moderate to heavy rain", "rain periodically heavy", "heavy rain"]:
            tomorrow = "Heavy rain may overwhelm. For tomorrow ensure good drainage tomorrow and avoid overwatering."
        elif TMW_day_sky in ["windy", "wind and rain", "hail", "hail showers"]:
            tomorrow = "Wind or hail could damage tender leaves tomorrow. Provide shelter or move indoors."
        elif TMW_day_sky in ["light snow", "light snow showers", "chance of snow showers"]:
            tomorrow = "Cold snap incoming: tomorrow protect it from frost and consider insulating the base."
        elif TMW_day_sky in ["thunderstorm", "scattered thunderstorms", "thundershower", "heavy thunderstorm"]:
            tomorrow = "Storms ahead: tommorrow keep your plant safe from gusts and erratic moisture."
        else:
            tomorrow = "Tomorrow's conditions are mixed. Monitor your plant's response and adjust care if needed."

    elif sunlight in ["shade", "full shade", "deep shade"]:
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Skies are clear today, but your shade-loving plant prefers the cool and quiet. " \
            "Let it chill in its usual low-light spot, no need to chase the sun. Just keep an eye on soil moisture if temps rise."
        elif TMW_day_sky in ["cloudy", "mostly cloudy", "partly cloudy", "overcast"]:
            tomorrow = "Perfect shade conditions: tomorrow your plant will feel right at home."
        elif TMW_day_sky in ["light rain", "scattered showers", "chance of showers"]:
            tomorrow = "Gentle rain tomorrow: moisture is welcome, but avoid soggy soil."
        elif TMW_day_sky in ["heavy rain", "moderate to heavy rain", "rain and snow"]:
            tomorrow = "Heavy precipitation tomorrow may compact soil. Loosen it afterward to keep roots breathing."
        elif TMW_day_sky in ["snow", "snow showers", "snowstorm", "snow periodically heavy", "blowing snow", "heavy snow storm"]:
            tomorrow = "Snowy forecast for tomorrow: insulate roots and avoid exposure to freezing wind."
        elif TMW_day_sky in ["hail", "hail showers", "windy"]:
            tomorrow = "Harsh weather ahead: tomorrow shield delicate foliage or relocate temporarily."
        elif TMW_day_sky in ["thunderstorm", "light thunderstorm rain", "thundershower", "heavy thunderstorm"]:
            tomorrow = "Storms may bring erratic moisture. Keep your shade-lover in a stable, protected spot tomorrow."
        else:
            tomorrow = "Mix skies conditions tomorrow. Maintain consistent shade and moisture levels."

    elif sunlight == "filtered shade":
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Bright skies tomorrow: filtered shade is ideal. Avoid harsh direct rays."
        elif TMW_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            tomorrow = "Gentle light ahead: your plant will thrive without adjustments."
        elif TMW_day_sky in ["light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"]:
            tomorrow = "Rain expected: light levels will dip. Keep soil balanced and avoid soggy roots."
        elif TMW_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            tomorrow = "Storms ahead: protect your plant from gusts and keep it in a stable, sheltered spot."
        elif TMW_day_sky in ["snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"]:
            tomorrow = "Snowy forecast: filtered shade plants may need extra warmth and light indoors."
        elif TMW_day_sky in ["fog", "mist", "haze"]:
            tomorrow = "Visibility will be low: filtered light may not be enough. Consider boosting with artificial light."
        elif TMW_day_sky in ["windy", "hail", "hail showers"]:
            tomorrow = "Wind or hail expected: protect your plant and monitor light exposure."
        else:
            tomorrow = "Tomorrow's conditions are mixed. Adjust placement based on light availability and plant response."

    elif sunlight in ["part sun/part shade", "partial sun shade"]:
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Strong sun tomorrow: give your plant a few hours of exposure, then shift to shade."
        elif TMW_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            tomorrow = "Balanced skies ahead: ideal for part sun part shade plants."
        elif TMW_day_sky in ["fog", "mist", "haze"]:
            tomorrow = "Dim light tomorrow: your plant may need a brighter spot to compensate."
        elif TMW_day_sky in ["light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"]:
            tomorrow = "Rain expected: light will be limited, but your plant will appreciate the moisture."
        elif TMW_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            tomorrow = "Storms ahead: protect your plant and avoid exposing it to gusts or heavy drops."
        elif TMW_day_sky in ["snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"]:
            tomorrow = "Snowy forecast: your plant may need extra light and warmth indoors."
        elif TMW_day_sky in ["windy", "hail", "hail showers"]:
            tomorrow = "Wind or hail expected: keep your plant protected and avoid direct exposure."
        else:
            tomorrow = "Conditions are variable: partial exposure should be fine with a watchful eye."

    elif sunlight == "deciduous shade (spring sun)":
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Tomorrow's sun will be strong: if trees are still bare, your plant will benefit. Shade it otherwise."
        elif TMW_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            tomorrow = "Gentle skies ahead: ideal for plants that enjoy spring light under leafless trees."
        elif TMW_day_sky in ["fog", "mist", "haze"]:
            tomorrow = "Low light expected: your plant may need a boost if it's used to spring sun."
        elif TMW_day_sky in ["light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"]:
            tomorrow = "Rain expected: spring sun may be blocked. Keep your plant near a bright indoor spot."
        elif TMW_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            tomorrow = "Storms ahead: protect your plant and avoid placing it near exposed windows."
        elif TMW_day_sky in ["snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"]:
            tomorrow = "Snowy forecast: spring sun won't reach your plant. Keep it warm and well lit indoors."
        elif TMW_day_sky in ["windy", "hail", "hail showers"]:
            tomorrow = "Wind or hail expected: protect your plant from sudden exposure or damage."
        else:
            tomorrow = "Uncertain skies: monitor tree cover and light levels to guide placement."

    elif sunlight == "full sun partial sun shade":
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            tomorrow = "Strong sun tomorrow: your plant can handle it, but check for leaf stress."
        elif TMW_day_sky in ["partly cloudy", "mostly cloudy", "cloudy", "overcast"]:
            tomorrow = "Gentle light ahead: your plant's flexible needs will be satisfied."
        elif TMW_day_sky in ["fog", "mist", "haze"]:
            tomorrow = "Low visibility tomorrow: light will be weak, but your plant's flexibility makes it easy to manage."
        elif TMW_day_sky in ["light rain", "rain", "rain showers", "scattered showers", "chance of showers",
            "moderate to heavy rain", "heavy rain", "heavy rain showers", "rain periodically heavy",
            "wind and rain", "light to moderate rain"]:
            tomorrow = "Rain expected: light will be limited, but your plant will appreciate the moisture."
        elif TMW_day_sky in ["thunderstorm", "light thunderstorm rain", "scattered thunderstorms", "thundershower"]:
            tomorrow = "Storms ahead: protect your plant from wind and monitor for waterlogging."
        elif TMW_day_sky in ["snow", "light snow", "snow showers", "light snow showers", "scattered snow showers",
            "snowstorm", "heavy snow", "heavy snow showers", "heavy snow storm", "snow periodically heavy",
            "chance of snow showers", "blowing snow", "rain and snow", "light to moderate snow", "moderate to heavy snow"]:
            tomorrow = "Snowy forecast: your plant won't get much light, but it's adaptable. Keep it warm and dry."
        elif TMW_day_sky in ["windy", "hail", "hail showers"]:
            tomorrow = "Wind or hail expected: shield your plant and check for leaf damage."
        else:
            tomorrow = "Tomorrow's conditions are mixed. Your plant's broad tolerance makes care easy."

    # Fallback
    else:
        tomorrow = "Sunlight preference not recognized. For tomorrow: monitor your plant and adjust care as needed."

    return tomorrow

def recommend(watering, sunlight_today, sunlight_tomorrow):
    # Create and return the final recommendation phrase.
    recommendation = f"{watering} {sunlight_today} {sunlight_tomorrow}"
    return recommendation

def plant_weather_advisor(location, watering, sunlight):
    today, tmrrw = get_forecast(location)

    TODAY_day_sky, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity, TMW_day_sky, TMW_day_rain, TMW_day_humidity,  TMW_night_rain, TMW_night_humidity = extract(today, tmrrw)
    water_care = recommend_watering(watering, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity, TMW_day_rain, TMW_day_humidity, TMW_night_rain, TMW_night_humidity)
    today_care = recommend_today_sunlight(sunlight, TODAY_day_sky)
    tomorrow_care = recommend_tmw_sunlight(sunlight, TMW_day_sky)

    return recommend(water_care, today_care, tomorrow_care)

def main():
    from helper_functions import prompt_userLocation
    location = prompt_userLocation()
    print(plant_weather_advisor(location, "average", "full sun"))
if __name__ == "__main__":
    main()

#--------------------------------------------------------------------------------------------------------------
gmaps_API_descr = [
    "blowing_snow","chance_of_showers","chance_of_snow_showers","clear","cloudy","hail","hail_showers",
    "heavy_rain","heavy_rain_showers","heavy_snow","heavy_snow_showers","heavy_snow_storm","light_rain",
    "light_rain_showers","light_snow","light_snow_showers","light_thunderstorm_rain","light_to_moderate_rain",
    "light_to_moderate_snow","moderate_to_heavy_rain","moderate_to_heavy_snow","mostly_clear","mostly_cloudy",
    "partly_cloudy","rain","rain_and_snow","rain_periodically_heavy","rain_showers","scattered_showers",
    "scattered_snow_showers","scattered_thunderstorms","snow","snow_periodically_heavy","snow_showers",
    "snowstorm","thundershower","thunderstorm","wind_and_rain","windy",
]