#Script to request pollen data from Google Maps Pollen API. It returns grass, weed and trees risk levels in a given location.

import requests

def get_pollen(lat, long):

    API_key = "AIzaSyDU2kPehR5E6yrOlf1bqTZhBGc7A-mvkrU"

    url = f"https://pollen.googleapis.com/v1/forecast:lookup?key={API_key}&location.longitude={long}&location.latitude={lat}&days=1"

    response = requests.get(url)

    try:
        data = response.json()
        
        daily = data["dailyInfo"][0]

        
        risk_levels = {
        'GRASS': 'unknown',
        'WEED': 'unknown',
        'TREE': 'unknown'
        }

        # Search in pollenTypeInfo
        for item in daily.get('pollenTypeInfo', []):
            code = item.get('code')
            index_info = item.get('indexInfo')
            if code in risk_levels and index_info:
                risk_levels[code] = index_info.get('category', 'unknown')

        return risk_levels['GRASS'], risk_levels['WEED'], risk_levels['TREE']
        
        #with open("daily.json", "w", encoding="utf-8") as f:
            #json.dump(daily, f, indent=4, ensure_ascii=False)
    except requests.RequestException as r:
        print(f"Error fetching pollen data: {r}.")



#print(get_pollen(location="den haag, nl"))