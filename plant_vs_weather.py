import requests, os
from googlemaps.exceptions import HTTPError
from diskcache import Cache
from dotenv import load_dotenv
from gmaps_package import extract_forecast, get_geocode
from helpers import get_geocode

# Initialize local cache for geocoding.
cache = Cache("gmaps_module_cache")

def get_forecast(location):
    lat, long = get_geocode(location)

    load_dotenv()
    API_key = os.getenv("GMAPS_API_KEY")
    url = f"https://weather.googleapis.com/v1/forecast/days:lookup?key={API_key}&location.latitude={lat}&location.longitude={long}&days=2"

    try:
        key = (location, lat, long)
        if key in cache:
            cached = cache[key]
            td_result = cached["today"]
            tm_result = cached["tomorrow"]
        else:
            response = requests.get(url)
            content = response.json()
            forecast = content.get('forecastDays', [])
            if len(forecast) < 2:
                return "Error fetching weather forecast data"

            td_result = extract_forecast(forecast[0])
            tm_result = extract_forecast(forecast[1])
            cache[key] = {"today": td_result, "tomorrow": tm_result}

        return td_result, tm_result

    except (requests.RequestException, HTTPError) as r:
        print(f"Error fetching forecast data: {r}")
    except KeyError as k:
        print(f"Error processing forecast data: {k}")

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

def recommend_watering(watering, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity, TMW_day_rain, TMW_day_humidity,  TMW_night_rain, TMW_night_humidity):
    # Watering recommendations based on today's and tomorrow's weather
    if (TODAY_day_rain or TODAY_night_rain) > 70 and (TODAY_day_humidity or TODAY_night_humidity) > 80:
        if watering == "minimum":
            watering_phrase = "No need to lift the watering can. Your plant's chill and the sky's got it covered."
        elif watering == "average":
            watering_phrase = "If you plan to water it today, let the rain do the job. Rainy and humid day ahead!"
        elif watering == "frequent":
            watering_phrase = "Even thirsty plants deserve a rainy day. Skip the watering and let nature hydrate. Your plant is throwing a party!"

    elif (TMW_day_rain or TMW_night_rain) > 70 and (TODAY_day_rain and TODAY_night_rain) < 30:
        if watering == "minimum":
            watering_phrase = "Dry today, wet tomorrow. Your plant can wait—rain's RSVP is confirmed."
        elif watering == "average":
            watering_phrase = "Hold off if you can. Tomorrow's forecast looks juicy enough to skip the hose."
        elif watering == "frequent":
            watering_phrase = "Even if your plant's a diva, today's dryness won't last. Let tomorrow's rain take the stage."

    elif (TODAY_day_humidity or TODAY_night_humidity) < 40 and (TODAY_day_rain and TODAY_night_rain) < 30:
        if watering == "minimum":
            watering_phrase = "Low humidity and no rain? Might be borderline, but your plant's probably fine."
        elif watering == "average":
            watering_phrase = "Rain and humidity are not doing their job. Your plant might be thirstier than it looks. Check your location extended forecast and consider watering."
        elif watering == "frequent":
            watering_phrase = "Your plant's living in a desert fantasy. Give it a drink!"

    elif (TODAY_day_humidity or TODAY_night_humidity) > 80 and (TODAY_day_rain and TODAY_night_rain) < 30:
        if watering == "minimum":
            watering_phrase = "Humidity's high, skies are dry. Your plant's probably fine with the ambient vibes."
        elif watering == "average":
            watering_phrase = "Humidity's high but skies are dry. A light misting might be enough."
        elif watering == "frequent":
            watering_phrase = "Your plant's used to the VIP treatment. Give it a gentle mist, just enough to keep it smiling."

    elif (TODAY_day_rain + TODAY_night_rain + TMW_day_rain + TMW_night_rain) < 40 and (TODAY_day_humidity + TODAY_night_humidity + TMW_day_humidity + TMW_night_humidity) < 160:
        if watering == "minimum":
            watering_phrase = "Low rain, low humidity across the board. Might be time to break the drought with a splash."
        elif watering == "average":
            watering_phrase = "Your plant's not getting much help from the sky. A solid watering session is in order."
        elif watering == "frequent":
            watering_phrase = "This is your moment. Your plant's craving hydration, don't hold back."

    elif (TODAY_day_rain + TODAY_night_rain) < 30 and (TMW_day_rain + TMW_night_rain) < 30 and (TODAY_day_humidity + TODAY_night_humidity) > 70:
        if watering == "minimum":
            watering_phrase = "Dry skies but decent humidity. Your plant's probably coasting just fine."
        elif watering == "average":
            watering_phrase = "Humidity's helping, but a light watering wouldn't hurt."
        elif watering == "frequent":
            watering_phrase = "Your plant's expecting its usual spa day. Give it a gentle soak, it's earned it."

    else:
        watering_phrase = "Weather's playing it cool. Check soil moisture and trust your plant-parent instincts."

    return watering_phrase


def recommend_today_sunlight(sunlight, TODAY_day_sky):
    # Sunlight recommendations based on plant needs and actual weather

    # Today sky conditions for full sun plants
    if sunlight == "full sun":
        if TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly sunny"]:
            today = "Clear expected: perfect day for sun worship. Your plant's soaking up the rays."
        elif TODAY_day_sky in ["partly cloudy", "mostly cloudy"]:
            today = "Partly cloudy expected: your sun-loving plant might pout today. Keep an eye on leaf behavior."
        elif TODAY_day_sky in ["cloudy"]:
            today = "Cloudy expected: not ideal for full sun plants. Consider moving it closer to a window."
        elif TODAY_day_sky in ["light rain", "rain", "heavy rain", "rain showers", "scattered showers", "chance of showers"]:
            today = "Rain expected: your full sun plant might feel gloomy. Monitor for drooping or leaf stress."
        elif TODAY_day_sky in ["thunderstorm", "thundershower", "scattered thunderstorms"]:
            today = "Thunderstorm expected: not much light today. Your plant may need extra warmth or support."
        elif TODAY_day_sky in ["hail", "hail showers"]:
            today = "Hail expected: protect your plant from damage and low light conditions."
        elif TODAY_day_sky in ["snow", "light snow", "heavy snow", "snow showers", "scattered snow showers"]:
            today = "Snow expected: your sun-loving plant won't be thrilled. Keep it warm and well-lit indoors."
        else:
            today = "Sky conditions unclear today: check your plant's response and adjust light exposure as needed."

    # Today sky conditions for part sun/part shade plants
    elif sunlight in ["part sun", "part shade", "partial shade"]:
        if TODAY_day_sky in ["partly cloudy", "mostly cloudy", "cloudy"]:
            today = "Partly cloudy expected: ideal filtered light today. Your plant's getting a gentle glow."
        elif TODAY_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny"]:
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
    elif sunlight in ["shade", "full shade"]:
        if TODAY_day_sky in ["sunny", "partly sunny", "clear", "mostly clear", "mostly sunny", "partly cloudy"]:
            today = "Sunny expected: too much light for a shade-seeker. Consider moving it to a cooler corner."
        elif TODAY_day_sky in ["cloudy", "mostly cloudy"]:
            today = "Cloudy expected: perfect low-light conditions. Your plant's in its comfort zone."
        elif TODAY_day_sky in ["light rain", "rain", "heavy rain", "rain showers", "scattered showers", "chance of showers"]:
            today = "Rain expected: soft light and moisture—ideal for shade-loving plants."
        elif TODAY_day_sky in ["thunderstorm", "thundershower", "scattered thunderstorms", "heavy thunderstorm"]:
            today = "Thunderstorm expected: low light and high humidity. Your plant should be just fine."
        elif TODAY_day_sky in ["hail", "hail showers"]:
            today = "Hail expected: protect your plant from sudden cold and physical damage."
        elif TODAY_day_sky in ["snow", "light snow", "heavy snow", "snow showers", "scattered snow showers"]:
            today = "Snow expected: low light and cool temps, your shade plant will likely be comfortable."
        else:
            today = "Sky conditions unclear today: keep your shade plant in a stable spot and monitor for stress."

    # Fallback for unrecognized sunlight values
    else:
        today = "Sunlight preference not recognized. For today: monitor your plant and adjust care as needed."

    return today


def recommend_tmw_sunlight(sunlight, TMW_day_sky):
    if sunlight == "full sun":
        if TMW_day_sky in ["clear", "mostly clear", "sunny", "mostly sunny", "partly cloudy"]:
            tomorrow = "Tomorrow's skies are bright: ideal for sun-hungry plants. Let them bask and thrive."
        elif TMW_day_sky in ["cloudy", "mostly cloudy"]:
            tomorrow = "Clouds ahead: not harmful, but your sun-lover might feel underfed. Consider supplemental light."
        elif TMW_day_sky in [
            "light rain", "rain", "heavy rain", "rain showers", "scattered showers",
            "chance of showers", "rain periodically heavy", "moderate to heavy rain"
        ]:
            tomorrow = "Rain expected: light levels will dip. If indoors, place near a window to catch stray rays."
        elif TMW_day_sky in [
            "thunderstorm", "scattered thunderstorms", "thundershower", "light thunderstorm rain", "heavy thunderstorm"
        ]:
            tomorrow = "Stormy forecast: protect from wind, but keep near light. Tomorrow's sun will be shy."
        elif TMW_day_sky in ["fog", "haze", "mist"]:
            tomorrow = "Low visibility tomorrow: your plant may miss its solar fix. Brighten its day with artificial light."
        else:
            tomorrow = "Tomorrow's light is uncertain. Keep your sun-lover in a bright, stable spot just in case."

    elif sunlight in ["part sun", "part shade", "partial shade"]:
        if TMW_day_sky in ["partly cloudy", "mostly cloudy", "cloudy"]:
            tomorrow = "Balanced skies ahead: your plant will enjoy gentle light. No extra care needed."
        elif TMW_day_sky in ["light rain", "light to moderate rain", "rain showers", "scattered showers", "chance of showers"]:
            tomorrow = "Soft rain tomorrow: ideal for these light-sensitive plants. Let nature do the watering."
        elif TMW_day_sky in ["moderate to heavy rain", "rain periodically heavy", "heavy rain"]:
            tomorrow = "Heavy rain may overwhelm. Ensure good drainage and avoid overwatering."
        elif TMW_day_sky in ["windy", "wind and rain", "hail", "hail showers"]:
            tomorrow = "Wind or hail could damage tender leaves. Provide shelter or move indoors."
        elif TMW_day_sky in ["light snow", "light snow showers", "chance of snow showers"]:
            tomorrow = "Cold snap incoming: protect from frost and consider insulating the base."
        elif TMW_day_sky in ["thunderstorm", "scattered thunderstorms", "thundershower", "heavy thunderstorm"]:
            tomorrow = "Storms ahead: keep your plant safe from gusts and erratic moisture."
        else:
            tomorrow = "Tomorrow's conditions are mixed. Monitor your plant's response and adjust care if needed."

    elif sunlight in ["shade", "full shade"]:
        if TMW_day_sky in ["cloudy", "mostly cloudy", "partly cloudy"]:
            tomorrow = "Perfect shade conditions: your plant will feel right at home."
        elif TMW_day_sky in ["light rain", "scattered showers", "chance of showers"]:
            tomorrow = "Gentle rain tomorrow: moisture is welcome, but avoid soggy soil."
        elif TMW_day_sky in ["heavy rain", "moderate to heavy rain", "rain and snow"]:
            tomorrow = "Heavy precipitation may compact soil. Loosen it afterward to keep roots breathing."
        elif TMW_day_sky in ["snow", "snow showers", "snowstorm", "snow periodically heavy", "blowing snow", "heavy snow storm"]:
            tomorrow = "Snowy forecast: insulate roots and avoid exposure to freezing wind."
        elif TMW_day_sky in ["hail", "hail showers", "windy"]:
            tomorrow = "Harsh weather ahead: shield delicate foliage or relocate temporarily."
        elif TMW_day_sky in ["thunderstorm", "light thunderstorm rain", "thundershower", "heavy thunderstorm"]:
            tomorrow = "Storms may bring erratic moisture. Keep your shade-lover in a stable, protected spot."
        else:
            tomorrow = "Mix skies conditions tomorrow. Maintain consistent shade and moisture levels."

    else:
        tomorrow = "Sunlight preference not recognized. For tomorrow: monitor your plant and adjust care as needed."

    return tomorrow


def recommend(watering, sunlight_today, sunlight_tomorrow):
    # Create and return the final recommendation phrase.
    recommendation = f"{watering} {sunlight_today} {sunlight_tomorrow}"
    return recommendation

def weather_plant(location, watering, sunlight):
    today, tmrrw = get_forecast(location)
    #print(today, tmrrw)
    TODAY_day_sky, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity, TMW_day_sky, TMW_day_rain, TMW_day_humidity,  TMW_night_rain, TMW_night_humidity = extract(today, tmrrw)
    water_care = recommend_watering(watering, TODAY_day_rain, TODAY_day_humidity, TODAY_night_rain, TODAY_night_humidity, TMW_day_rain, TMW_day_humidity, TMW_night_rain, TMW_night_humidity)
    today_care = recommend_today_sunlight(sunlight, TODAY_day_sky)
    tomorrow_care = recommend_tmw_sunlight(sunlight, TMW_day_sky)
    return recommend(water_care, today_care, tomorrow_care)

def main():

    print(weather_plant("Amsterdam, NL", "average", "part shade"))

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



'''
Recommendations based on gmaps weather APi description parameters:

Clear & Sunny
Clear sky expected: enjoy optimal conditions for planting and pruning.

Clear sky expected: water early in the morning to reduce evaporation.

Clear sky expected: monitor for sun stress on delicate plants.

Sunny weather expected: provide shade for sensitive plants to prevent scorching.

Sunny weather expected: increase watering frequency to combat heat stress.

Sunny weather expected: apply mulch to retain soil moisture.

🌤️ Cloudy & Overcast
Cloudy sky expected: ideal for transplanting due to reduced sun stress.

Cloudy sky expected: monitor for fungal growth in humid conditions.

Cloudy sky expected: reduce watering slightly, less evaporation.

Mostly cloudy skies today: check for signs of mildew or mold.

Mostly cloudy skies today: use this time to fertilize; less sun stress.

Mostly cloudy skies today: prune without risk of sunburn on exposed cuts.

Partly cloudy sky: good conditions for light garden tasks.

Partly cloudy sky: monitor for pests hiding in shaded areas.

Partly cloudy sky: water moderately, sun may still dry soil.

🌧️ Rain & Showers
Light rain expected: let nature water your garden. Pause irrigation.

Light rain expected: check drainage to prevent root rot.

Light rain expected: avoid fertilizing, nutrients may wash away.

Rain expected: secure containers and check for pooling water.

Rain expected: delay planting, soil may be too wet.

Rain expected: inspect for slug and snail activity.

Heavy rain expected: protect young plants from soil erosion.

Heavy rain expected: avoid walking on wet soil to prevent compaction.

Heavy rain expected: reinforce raised beds and borders.

Showers expected: pause watering and let rainfall do the work.

Showers expected: inspect for leaf damage post-showers.

Showers expected: avoid spraying pesticides, they'll wash off.

❄️ Snow & Cold
Snow expected: cover vulnerable plants with frost cloth.

Snow expected: avoid watering, frozen soil can damage roots.

Snow expected: shake off snow from branches to prevent breakage.

Snowstorm expected: pause all outdoor gardening and let your plants hunker down.

Snowstorm expected: move potted plants indoors or cover them securely.

Snowstorm expected: inspect for broken branches and gently clear heavy snow buildup.

Snow periodically heavy expected: brush off accumulation gently to reduce stress on branches.

Snow periodically heavy expected: reinforce plant covers and mulch to protect roots.

Snow periodically heavy expected: avoid pruning, plants are dormant and vulnerable.

⚡ Thunder & Wind
Thundershower expected: secure tall or fragile plants against sudden wind and rain.

Thundershower expected: avoid fertilizing, nutrients may wash away.

Thundershower expected: inspect for leaf damage and check soil stability afterward.

Thunderstorm expected: unplug irrigation systems and shelter sensitive plants.

Thunderstorm expected: avoid working outdoors, safety first.

Thunderstorm expected: check for wind damage and prune broken stems.

Wind and rain expected: add mulch or ground cover to protect roots from erosion.

Wind and rain expected: secure containers and hanging plants.

Wind and rain expected: avoid fertilizing, nutrients may be lost to runoff.

Windy condition today: water deeply to counter increased evaporation.

Windy condition today: stake tall plants to prevent snapping.

Windy condition today: use windbreaks or cloches to shield young plants.


'''

"""
Watering Advice (Rain + Humidity)
“Rain’s on the guest list today. Let nature do the watering while you sip your coffee.”

“Humidity’s high and the clouds are moody — your plant’s basically in a botanical spa.”

“Planning to water today? Hold that thought. Afternoon showers are RSVP’ing with 90% certainty.”

“Your plant’s thirst level is ‘frequent,’ but the sky’s already prepping a downpour. Let it rain.”

“Humidity’s low and skies are clear — your plant’s parched and ready for a drink.”

“Rain tomorrow, dry today. If your plant’s not gasping, let the clouds handle hydration.”

“Humidity’s flirting with 90%, but no rain in sight. A light misting might be just the vibe.”

“Your low-maintenance plant says ‘meh,’ but the dry air says ‘maybe.’ Trust your soil.”

Sunlight vs. Sky Condition
“Full sun plant meets cloudy skies — not ideal, but it’s a good day to observe leaf behavior.”

“Your shade-loving plant is getting spotlighted today. Consider a strategic relocation.”

“Sun’s blazing and your plant’s a shade seeker. Time to play umbrella.”

“Clouds are thick, but your indirect-light plant is vibing. No sunglasses needed.”

“Mostly cloudy with a chance of drama — your part-shade plant will be just fine.”

“Light rain and full sun needs? Not a match made in heaven. Monitor for leaf stress.”

“Sunny skies and loamy soil — your plant’s living its best Mediterranean fantasy.”

"""

