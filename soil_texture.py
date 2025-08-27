import requests, json

# Soil Care Recommendations Template.
soil_care_recommendations = {
    "sandy": {
        "watering": (
            "Sandy soils drain quickly and retain little moisture. "
            "Water deeply but more frequently, especially during dry spells."
        ),
        "fertility": (
            "Low in nutrients due to leaching. Improve fertility by adding organic matter "
            "such as compost or well-rotted manure. Mulching helps retain moisture."
        ),
        "plants": [
            "Lavender", "Rosemary", "Thyme", "Carrots", "Sage", "Sedum."
        ]
    },
    "clay": {
        "watering": (
            "Clay soils retain water and can become compacted. Avoid overwatering, "
            "and ensure good drainage to prevent root rot."
        ),
        "fertility": (
            "Rich in nutrients but poorly aerated. Improve structure by incorporating coarse sand, "
            "gypsum, and organic matter. Raised beds can help."
        ),
        "plants": [
            "Daylilies", "Hostas", "Asters", "Tomatoes", "Peonies", "Bee Balm."
        ]
    },
    "silty": {
        "watering": (
            "Silty soils hold moisture well but can compact easily. Water moderately and avoid walking on wet soil."
        ),
        "fertility": (
            "Naturally fertile. Maintain structure with compost and avoid tilling when wet. "
            "Cover crops can help preserve soil health."
        ),
        "plants": [
            "Lettuce", "Peas", "Hydrangeas", "Ferns", "Spinach", "Coleus."
        ]
    },
    "peaty": {
        "watering": (
            "Peaty soils retain a lot of moisture and are often acidic. Monitor water levels to avoid waterlogging."
        ),
        "fertility": (
            "High in organic matter but low in minerals. Lime may be needed to raise pH. "
            "Use balanced fertilizers for nutrient support."
        ),
        "plants": [
            "Azaleas", "Blueberries", "Camellias", "Ferns", "Rhododendrons."
        ]
    },
    "loamy": {
        "watering": (
            "Loamy soils have ideal moisture retention and drainage. Water as needed, adjusting for plant type and season."
        ),
        "fertility": (
            "Naturally fertile and well-balanced. Maintain with seasonal compost and avoid over-fertilizing."
        ),
        "plants": [
            "Most vegetables", "Roses", "Zinnias", "Beans", "Marigolds", "Sunflowers."
        ]
    },
    "chalky": {
        "watering": (
            "Chalky soils drain quickly and can be dry. Water regularly and deeply, especially during hot weather."
        ),
        "fertility": (
            "Alkaline and low in nutrients. Add organic matter and use acidifying fertilizers if needed. "
            "Iron and manganese deficiencies are common."
        ),
        "plants": [
            "Lilacs", "Clematis", "Spinach", "Beets", "Sweet Alyssum", "Wallflowers."
        ]
    }
}

# Fetch soil texture data in form of json response (whole content), from SoilGrids based on a given lat and long.
def get_soil_data(lat, lon):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.json()
        #print(content)
        with open("soil.json", "w") as f:
            json.dump(content, f, ensure_ascii=True, indent=2)
        print("All Done! Check 'soil.json' file. ")

        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching soil data: {e}")
        return None

#Extract soil texture values from SoilGrids API.
def get_soil_texture(lat, lon):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Helper to extract mean value from top layer
        def extract_mean(property_name):
            try:
                layers = data["properties"][property_name]["layers"]
                return layers[0]["values"]["mean"]
            except (KeyError, IndexError, TypeError):
                print(f"⚠️ '{property_name}' data not available at this location.")
                return None

        clay = extract_mean("clay")
        silt = extract_mean("silt")
        sand = extract_mean("sand")

        if None in (clay, silt, sand):
            print("❌ Incomplete soil texture data. Cannot classify.")
            return None

        print(f"🧪 Soil Texture at ({lat}, {lon}):")
        print(f"Clay: {clay:.1f}%")
        print(f"Silt: {silt:.1f}%")
        print(f"Sand: {sand:.1f}%")

        texture = classify_texture(sand, silt, clay)
        print(f"🧭 Dominant Texture Class: {texture}")
        return texture

    except requests.RequestException as e:
        print(f"❌ Error fetching soil data: {e}")
        return None

def classify_texture(sand, silt, clay):
    # Very simplified logic — for full accuracy, use USDA soil triangle
    if clay > 40:
        return "Clay"
    elif sand > 70:
        return "Sandy"
    elif silt > 80:
        return "Silty"
    elif 20 < clay < 35 and 20 < sand < 50:
        return "Loam"
    else:
        return "Mixed Texture"


#This logic is based on USDA guidelines, using the triangle logic with conditional ranges.
def classify_usda_texture(sand, silt, clay):
    if clay >= 40:
        return "Clay"
    elif clay >= 27 and clay < 40 and sand <= 20:
        return "Silty Clay"
    elif clay >= 27 and clay < 40 and sand > 20:
        return "Sandy Clay"
    elif clay >= 20 and clay < 27 and silt >= 28 and silt < 50 and sand <= 52:
        return "Clay Loam"
    elif clay >= 7 and clay < 20 and sand > 52 and silt < 50:
        return "Sandy Loam"
    elif clay >= 7 and clay < 27 and silt >= 50:
        return "Silty Loam"
    elif clay >= 7 and clay < 27 and silt < 50 and sand < 52:
        return "Loam"
    elif clay < 7 and silt >= 50 and sand <= 20:
        return "Silt"
    elif clay < 7 and silt >= 50 and sand > 20:
        return "Silt Loam"
    elif clay < 7 and silt < 50 and sand >= 80:
        return "Sand"
    elif clay < 7 and silt < 50 and sand >= 50:
        return "Loamy Sand"
    else:
        return "Unclassified"

# Use with soil templates
def get_soil_care_advice(soil_type):
    soil_type = soil_type.lower()
    advice = soil_care_recommendations.get(soil_type)
    if advice:
        print(f"🧭 Soil Type: {soil_type.title()}")
        print(f"💧 Watering Advice: {advice['watering']}")
        print(f"🌾 Fertility Tips: {advice['fertility']}")
        print(f"🌿 Recommended Plants: {', '.join(advice['plants'])}")
    else:
        print("❌ Soil type not recognized.")

#get_soil_data(lat=52.078663, lon=4.288788) #lat 52.078663 lon 4.288788 for Den Haag, NL.

get_soil_texture(lat = 48.8566, lon = 2.3522)

#get_soil_care_advice(soil_type="loamy")