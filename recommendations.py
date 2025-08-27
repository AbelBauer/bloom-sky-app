# Helper function to provide short recommendations to the user based on the weather forecast and pollen risk levels variables.

def get_recommendation(is_daytime, temp, rain_prob, humidity, grass_pollen_risk, tree_pollen_risk, weed_pollen_risk) -> str:
    
    recommendation = ""

    # Pollen risk level variables
    grass = grass_pollen_risk.lower()
    tree = tree_pollen_risk.lower()
    weed = weed_pollen_risk.lower()

    high = ["high", "very high"]
    moderate = "moderate"
    #low = ["low", "very low"]


    # Time of Day
    if not is_daytime:
        recommendation += "🕚➱🌃 Night owl mode: dim lights, indoor chill. Cozy up with blanket-movie combo. Or....sweat dreams 💤💤\n"
    else:
        recommendation += "🕗➱🌅 The day's in full swing. Soak it up your way!\n"

    # Temperature
    if 28 <= temp <= 37 and humidity < 80 and rain_prob < 25 and is_daytime:
        recommendation += "☀️  Beach vibes activated! Rock your swimwear, flip-flops, and sunglasses.\n"
    elif temp > 37:
        recommendation += "🥵 It's a desert out there. Hydrate like it's your job!\n"
    elif 20 <= temp <= 28 and rain_prob < 50:
        if is_daytime:
            recommendation += "😎 Perfect time for a park stroll or café terrace. You are good to go!\n"
        else:
            recommendation += "🍽️  Warm evening out there. Perfect time for a dinner out or catching a late film.\n"
    elif 10 <= temp < 20 and is_daytime:
        recommendation += "🧥 Light layers recommended, it's brisk but charming. Channel that autumn wanderer vibe.\n"
    elif temp < 10 and is_daytime:
        recommendation += "🥶 Stay layered and warm. Consider indoor fun and skip the frostbite.\n"

    # Rain
    if rain_prob >= 60 and temp > 15:
        recommendation += "☔ Umbrella alert! Waterproof vibes only.\n"
    elif rain_prob >= 40:
        recommendation += "🌧️  Light rain possible. Bring a hoodie just in case.\n"
    elif 20 < rain_prob < 40:
        recommendation += "☁️  Grey skies: maybe rain, probably not. Trust issues remain.\n"
    elif rain_prob < 20 and is_daytime:
        recommendation += "🌞 Sun's out. Perfect day to bloom and roam!\n"
    
    # Humidity
    if humidity >= 80:
        recommendation += "💦 Sticky alert! Hydrate well and skip the heavy fabrics.\n"
    elif humidity < 30:
        recommendation += "💨 Dry air today. Moisturize and sip that water.\n"
    elif 30 < humidity < 80 and is_daytime:
        if temp < 32:
            recommendation += "⛹️  Comfortable humidity today. Great for any activity!\n"
        else:
            recommendation += "🥵 Step out and it's instant bake mode. Shade up, hydrate hard!\n"

    # Pollen Alert
    # Analyze grass pollen
    if grass in high:
        recommendation += "\n🔴 ➜ 🌾 Grass pollen is high today. Mask up or stay indoors!\n"
    elif grass == "moderate":
        recommendation += "\n🟠 ➜ 🌾 Moderate grass pollen levels. Keep allergy meds handy.\n"
    else:
        recommendation += "\n🟢 ➜ 🌾 Grass pollen levels are low right now. If you're super sensitive, there's a good chance you'll feel it today.\n"
    
    # Analyze tree pollen
    if tree in high:
        recommendation += "🔴 ➜ 🌳 Tree pollen is spiking. Avoid parks or wooded areas if you're sensitive.\n"
    elif tree == "moderate":
        recommendation += "🟠 ➜ 🌳 Moderate tree pollen. Check symptoms and avoid peak hours.\n"
    else:
        recommendation += "🟢 ➜ 🌳 Trees pollen levels are low right now. If you're super sensitive, there's a good chance you'll feel it today.\n"
    
    # Analyze weed pollen
    if weed in high:
        recommendation += "🔴 ➜ 🌿 Weed pollen levels are high. Keep windows closed and limit outdoor exposure."
    elif weed == "moderate":
        recommendation += "🟠 ➜ 🌿 Moderate weed pollen. Some discomfort possible if you're allergic."
    else:
        recommendation += "🟢 ➜ 🌿 Weed pollen levels are low right now. If you're super sensitive, there's a good chance you'll feel it today."
   
    return recommendation