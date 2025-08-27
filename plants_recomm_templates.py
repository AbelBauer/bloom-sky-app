import random # mention in README


def generate_plant_recommendation(plant_name, watering_level, watering_frequency, sunlight_level, growth_stage=None, soil_type=None):
    
    # Phrase banks
    water_frequency_phrases = {
        "frequent": f"thirsty ({watering_frequency}), keep the watering can close!",
        "average": f"balanced ({watering_frequency}), not too wet, not too dry", # period: YES or NO?
        "minimum": f"low-maintenance ({watering_frequency}), a splash now and then will do.",
        "none": f"independent ({watering_frequency}), no watering needed, like a cactus on vacation."
    }
    
    soil_types = {
        "clay": "clay soil holds water like a clingy ex, go easy on the watering.",
        "sand": "Sandy soil drains fast, so keep the hydration coming.",
        "loam": "Loamy soil is the Goldilocks of dirt — just right for most plants.",
        "peat": "Peaty soil is moisture-loving, so your plant's basically living in a mud spa.",
        "chalk": "Chalky soil can be picky, so keep an eye on nutrient levels.",
        "silt": "Silty soil is smooth and fertile. Your plant's living the good life."
    }

    sunlight_notes = {
        "full sun": "thrives in full sun. Give it a front-row seat to the sky show", # period out
        "part sun": "enjoys a mix: a few hours of direct sun, then some shade to chill.",
        "part shade": "prefers gentle light, like sipping tea under a leafy pergola", # period out
        "partial shade": "does best with dappled light. Think woodland vibes, not desert heat.",
        "shade": "is a shade seeker, it flourishes where the sun barely peeks in.",
        "full shade": "avoids direct sunlight altogether. Low light is its comfort zone.",
        "indirect light": "loves bright but filtered light. Cozy near a window, not center stage."
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

    if soil_type:
        soil_type = soil_types.get(soil_type, "")
    else:
        soil_type = ""

    def get_growth_description(growth, name):
        if growth in growth_stages:
            options = growth_stages[growth]
            selected = random.choice(options)
            description = selected.replace("{plant_name}", name)
            return description
        else:
            return ""

    growth_description = get_growth_description(growth_stage, plant_name)

    # Combined template variants
    templates = [
    f"{plant_name} {sunlight_notes[sunlight_level]}. Water it {water_frequency_phrases[watering_level]}. {growth_description} {soil_type}",
    f"{plant_name} {sunlight_notes[sunlight_level]}. Also, water it {water_frequency_phrases[watering_level]}. {growth_description} {soil_type}",
    f"{plant_name} needs watering that's {water_frequency_phrases[watering_level]}. It also {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"For {plant_name}, aim for {water_frequency_phrases[watering_level]} watering. It {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} thrives with {water_frequency_phrases[watering_level]} hydration. It {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} likes its water {water_frequency_phrases[watering_level]}. It {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"Give {plant_name} {water_frequency_phrases[watering_level]} drinks and let it chill — it {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} is about needing {water_frequency_phrases[watering_level]} watering. It {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} is currently in its prime era, think diva. It demands {water_frequency_phrases[watering_level]} hydration. {sunlight_notes[sunlight_level].capitalize()} {growth_description} {soil_type}",
    f"{plant_name} {sunlight_notes[sunlight_level]}. And since it's thriving, it's time to step up your watering game: {water_frequency_phrases[watering_level]}. {growth_description} {soil_type}",
    f"{plant_name} expects {water_frequency_phrases[watering_level]} watering. It also {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} is not just a plant. It's your garden rockstar. It needs {water_frequency_phrases[watering_level]} hydration. {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} is soaking up the vibes. Just remember: {water_frequency_phrases[watering_level]} watering is key. It also {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"{plant_name} is vibing. Give it {water_frequency_phrases[watering_level]} water and let it bask — it {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}",
    f"Hydrate {plant_name} {water_frequency_phrases[watering_level]}. It {sunlight_notes[sunlight_level]}. {growth_description} {soil_type}"
    ]


    return random.choice(templates).strip()
