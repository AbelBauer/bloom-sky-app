"""
generate_plant_recommendation

Generates a personalized, conversational care recommendation for a plant based on its environmental needs and growth stage. 
This function blends structured horticultural logic with playful language to produce engaging advice suitable for CLI display, 
garden apps, or educational tools.

Parameters:
-----------
plant_name : str  
    The name of the plant (vernacular, common, or scientific) to personalize the recommendation.

watering_level : str  
    Indicates how much water the plant typically requires. Accepted values include 'frequent', 'average', 'minimum', 'unknown', or None.

watering_frequency : str  
    A descriptive phrase or frequency label (e.g., 'daily', 'weekly') used to enrich the watering advice.

sunlight_level : str, optional  
    Describes the plant's light preference. Accepted values include 'full sun', 'part sun', 'shade', 'indirect light', etc.

growth_stage : str, optional  
    Indicates the plant's current developmental phase. Accepted values include 'seed', 'juvenile', 'adult', 'flowering', 'fruiting', 'senescence'.

soil_type : str, optional  
    Describes the soil in which the plant is growing. Accepted values include 'clay', 'sand', 'loam', 'peat', 'chalk', 'silt'.

Returns:
--------
str  
    A randomly selected, fully composed care recommendation string that combines watering, sunlight, growth stage, and soil advice.

Behavior:
---------
- Uses predefined phrase banks for watering, sunlight, soil, and growth stage to construct a natural-sounding recommendation.
- Randomly selects from multiple sentence templates to ensure variety and personality.
- Handles missing or unknown inputs gracefully with fallback phrases.
- Injects humor and metaphor to make plant care advice more relatable and memorable.

Example Output:
---------------
"Rose is living her best leaf life. It thrives in full sun, give it a front-row seat to the sky show. Give it thirsty (daily), keep an eye on the watering can! Rose is flowering with flair. Pollinators are welcome and admiration is encouraged. Loamy soil is the Goldilocks of dirt — just right for most plants."

Design Notes:
-------------
- The function is designed for expressive CLI output, not strict scientific reporting.
- Growth stage descriptions are randomized from a curated list to add emotional depth and variation.
- Soil advice includes embedded calls to action (e.g., 'Check Best Soil') to encourage further learning.
- All phrase banks are extensible and can be localized or themed for different audiences.

Limitations:
------------
- Does not validate input values; assumes they are pre-sanitized or user-controlled.
- Output tone is intentionally informal and metaphorical, which may not suit all contexts.
- Growth stage descriptions are static and not dynamically linked to plant species.

Author:
-------
abelnuovo@gmail.com - Bloom and Sky Project
"""



import random

def generate_plant_recommendation(plant_name, watering_level, watering_frequency, sunlight_level=None, growth_stage=None, soil_type=None):

    # Phrase banks
    water_frequency_phrases = {
        "frequent": f"is always waiting for some watering love ({watering_frequency}), so keep the water can close!",
        "average": f"needs balanced ({watering_frequency}), not too wet, not too dry watering.",
        "minimum": f"needs low-maintenance watering ({watering_frequency}). A splash now and then will do.",
        None : f"is not a thirsty plant({watering_frequency}). No watering needed, like a cactus on vacation.",
        "unknown": f"somewhat ({watering_frequency}), so observe and adjust as needed."
    }

    soil_types = {
        "clay": "Clay soil holds water like a clingy ex, go easy on the watering. Your plant deserves more than mud; check 'Best Soil' to ensure you are giving it the right one.",
        "sand": "Sandy soil drains fast, so keep the hydration coming. Your plant will thank you for the right soil. Check 'Best Soil' to make sure it's getting what it needs.",
        "loam": "Loamy soil is the Goldilocks of dirt — just right for most plants. Want to give your plant the best care? Check 'Best Soil'. It can help you choose the right foundation.",
        "peat": "Peaty soil is moisture-loving, so your plant's basically living in a mud spa. Healthy roots begin with the right soil. Check 'Best Soil' for guidance.",
        "chalk": "Chalky soil can be picky, so keep an eye on nutrient levels. Not sure if your soil's a good match? Check 'Best Soil' to find out.",
        "silt": "Silty soil is smooth and fertile. Your plant's living the good life. A little soil check can go a long way. Check 'Best Soil' to help your plant thrive."
    }

    sunlight_notes = {
        "full sun": "thrives in full sun, give it a front-row seat to the sky show.",
        "part sun": "enjoys a mix: a few hours of direct sun, then some shade to chill.",
        "part shade": "prefers gentle light, like sipping tea under a leafy pergola.",
        "partial shade": "does best with dappled light: think woodland vibes, not desert heat.",
        "shade": "is a shade seeker, it flourishes where the sun barely peeks in.",
        "full shade": "avoids direct sunlight altogether; low light is its comfort zone.",
        "indirect light": "loves bright but filtered light; cozy near a window, not center stage."
    }

    growth_stages = {
        "seed": [
            f"{plant_name} is in its seed phase. It holds quiet potential and waits patiently for the right conditions.",
            f"{plant_name} is a dormant dream. No roots, no shoots, just a promise tucked inside a shell.",
            f"{plant_name} is preparing for life. Keep it dry, safe, and let nature decide when to wake it up."
        ],
        "juvenile": [
            f"{plant_name} is in its juvenile phase. Roots are forming, leaves are stretching, and growth is in full swing.",
            f"{plant_name} is young and hungry for light. Support it with gentle care and consistent hydration.",
            f"{plant_name} is finding its rhythm. It's not a baby anymore, but still needs your guidance."
        ],
        "adult": [
            f"{plant_name} has reached adulthood. Growth slows, but strength and structure take center stage.",
            f"{plant_name} is stable and self-assured. It's focused on reproduction and long-term survival.",
            f"{plant_name} is in its prime. Respect its routine and it will thrive with grace."
        ],
        "flowering": [
            f"{plant_name} is flowering with flair. Pollinators are welcome and admiration is encouraged.",
            f"{plant_name} is showing off its blooms. Keep it nourished and let it shine.",
            f"{plant_name} is in full bloom. This is its moment to attract attention and fulfill its purpose."
        ],
        "fruiting": [
            f"{plant_name} is fruiting with intention. It's channeling energy into seeds and sustenance.",
            f"{plant_name} is producing fruit. Support it through this demanding and rewarding phase.",
            f"{plant_name} is nearing the finish line. Feed it well and celebrate its effort."
        ],
        "senescence": [
            f"{plant_name} is entering senescence. Growth fades, but its legacy lives on in seeds and memories.",
            f"{plant_name} is winding down. Offer comfort and let it rest with dignity.",
            f"{plant_name} is aging gracefully. It's not the end, just a transition toward renewal or rest."
        ]
    }

    # Fallback for soil type
    soil_type = soil_types.get(soil_type, "") if soil_type else ""

    # Fallback for watering level

    watering_phrase = str(water_frequency_phrases.get(
        watering_level,
        f"unpredictable ({watering_level}), so keep an eye out and adjust as needed."
    ))

    # Fallback for sunlight level
    sunlight_phrase = str(sunlight_notes.get(
        sunlight_level,
        "has diverse light needs depending on season and climate. Observe its behavior and adjust placement accordingly (Check 'Plant Care Information' for detailed guidance)."
    ))

    # Fallback for growth stage
    def get_growth_description(growth, name):
        if growth in growth_stages:
            options = growth_stages[growth]
            selected = random.choice(options)
            return selected.replace("{plant_name}", name)
        else:
            return f"{name} is in an undefined growth stage. Care gently and observe its progress."

    growth_description = get_growth_description(growth_stage, plant_name)

    # Combined template variants
    templates = [
        f"Your {plant_name} is living her best leaf life. It {sunlight_phrase} Give it {watering_phrase} {growth_description} {soil_type}",
        f"{plant_name} {sunlight_phrase} Also, {watering_phrase} {growth_description} {soil_type}",
        f"{plant_name} needs {watering_phrase} It also {sunlight_phrase} {growth_description} {soil_type}",
        f"{plant_name} {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}",
        f"{plant_name} thrives with {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} likes {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} {watering_phrase}. Let it chill: It {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} is about needing {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}",
        f"{plant_name} is photosynthesizing like a diva. It demands {watering_phrase} {sunlight_phrase.capitalize()} {growth_description} {soil_type}",
        f"Your {plant_name} is basking in the sun like a superstar. It {sunlight_phrase} Time to step up the watering game: {watering_phrase} {growth_description} {soil_type}",
        f"{plant_name} expects {watering_phrase} It also {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} is not just a plant. It's your garden star! It needs {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} is chilling in chlorophyll serenity. {plant_name} is {watering_phrase} It also {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} is vibing with your garden rhythm. Give it {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}",
        f"Your {plant_name} {watering_phrase} It {sunlight_phrase} {growth_description} {soil_type}"
    ]

    # Final return with safety check
    if templates:
        return random.choice(templates)
    else:
        return f"{plant_name} care info is currently unavailable. Try checking sunlight, watering, or growth stage inputs."
