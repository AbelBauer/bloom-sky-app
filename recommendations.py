"""
get_recommendation

Generates a weather and pollen-based lifestyle recommendation string based on current conditions. 
Combines temperature, humidity, rain probability, time of day, and pollen risks to produce contextual advice.

Parameters:
-----------
is_daytime : bool  
    Indicates whether it's currently daytime.

temp : int  
    Current temperature in Celsius.

rain_prob : int  
    Probability of precipitation (0-100%).

humidity : int  
    Current humidity percentage.

grass_pollen_risk : str  
    Risk level for grass pollen ('very low', 'low', 'moderate', 'high', 'very high').

tree_pollen_risk : str  
    Risk level for tree pollen.

weed_pollen_risk : str  
    Risk level for weed pollen.

Returns:
--------
str  
    A formatted recommendation string combining weather and pollen insights.
"""


def get_recommendation(is_daytime, temp, rain_prob, humidity, grass_pollen_risk, tree_pollen_risk, weed_pollen_risk) -> str:

    if not isinstance(is_daytime, bool):
        raise TypeError
    if not isinstance(temp, (int, float)):
        raise TypeError
    if not isinstance(rain_prob and humidity, int):
        raise TypeError
    if not isinstance(grass_pollen_risk and tree_pollen_risk and weed_pollen_risk, str):
        raise TypeError
    if temp and rain_prob and humidity == "N/A":
        raise TypeError

    recommendation = ""

    # Pollen risk level variables
    grass = grass_pollen_risk.lower().strip()
    tree = tree_pollen_risk.lower().strip()
    weed = weed_pollen_risk.lower().strip()

    high = ["high", "very high"]

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
    if humidity >= 70 and temp > 20 and is_daytime:
        recommendation += "💦 Sticky alert! Hydrate well and skip the heavy fabrics.\n"
    elif humidity >= 70 and temp < 20 and not is_daytime:
        recommendation += "🧥💦 If you're going out wear an extra layer, might be chillier than you think.\n"
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
        recommendation += "\n🔴   ➜ 🌾 Grass pollen is high today. Mask up or stay indoors!"
    elif grass == "moderate":
        recommendation += "\n🟠   ➜ 🌾 Moderate grass pollen levels. Keep allergy meds handy."
    elif grass == "low":
        recommendation += "\n🟢   ➜ 🌾 Grass pollen levels are low right now. If you're super sensitive, there's a chance you'll feel it today."
    elif grass == "very low":
        recommendation += "\n🟢🟢 ➜ 🌾 Grass pollen levels are very low right now. Most people won't notice a thing, even sensitive noses can relax today."
    else:
        recommendation += "\n⭕   ➜ 🌾 Grass pollen 'N/A'"
    # Analyze tree pollen
    if tree in high:
        recommendation += "\n🔴   ➜ 🌳 Tree pollen is spiking. Avoid parks or wooded areas if you're sensitive."
    elif tree == "moderate":
        recommendation += "\n🟠   ➜ 🌳 Moderate tree pollen. Check symptoms and avoid peak hours."
    elif tree == "low":
        recommendation += "\n🟢   ➜ 🌳 Trees pollen levels are low right now. If you're super sensitive, there's a chance you'll feel it today."
    elif tree == "very low":
        recommendation +=  "\n🟢🟢 ➜ 🌳 Trees pollen levels are very low right now. Most people won't notice a thing, even sensitive noses can relax today.\n"
    else:
        recommendation += "\n⭕   ➜ 🌳 Tree pollen 'N/A'"
    
    # Analyze weed pollen
    if weed in high:
        recommendation += "\n🔴   ➜ 🌿 Weed pollen levels are high. Keep windows closed and limit outdoor exposure."
    elif weed == "moderate":
        recommendation += "\n🟠   ➜ 🌿 Moderate weed pollen. Some discomfort possible if you're allergic."
    elif weed == "low":
        recommendation += "\n🟢   ➜ 🌿 Weed pollen levels are low right now. If you're super sensitive, there's a chance you'll feel it today."
    elif weed == "very low":
        recommendation += "\n🟢🟢 ➜ 🌿 Weed pollen levels are very low right now. Most people won't notice a thing, even sensitive noses can relax today."
    else:
        recommendation += "\n⭕   ➜ 🌿 Weed pollen 'N/A'"

    return recommendation

def main():
    result = get_recommendation(is_daytime=True, temp=10.6, rain_prob=75, humidity=75, grass_pollen_risk="low",
                                tree_pollen_risk="low", weed_pollen_risk="very low")
    print(result)
if __name__ == "__main__":
    main()