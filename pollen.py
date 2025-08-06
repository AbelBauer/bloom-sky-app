# to extract (only!) the required pollen data from ambee.com API's response.

import requests, sys #type: ignore

def get_pollen(location):

    url = "https://api.ambeedata.com/latest/pollen/by-place"
    params = {
        "place": location
    }

    headers = {
        "x-api-key": "a5f1c465220712b4587ca5ce64affc6d81c55eb3855f4093bfeb7f4f484d922d",  # getambee.com API key
        "Content-type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    try:
        response_data = response.json() # Convert to JSON first. Do not forget!
        pollen_risk = response_data['data'][0]['Risk']
        # count = response_data['data'][0]['Count'] # Pollen count data. Might be useful 
        grass_pollen_risk = pollen_risk.get("grass_pollen")
        tree_pollen_risk = pollen_risk.get("tree_pollen")
        weed_pollen_risk = pollen_risk.get("weed_pollen")

        return grass_pollen_risk, tree_pollen_risk, weed_pollen_risk
    
    except KeyError as k:
        print(f"Error fetching pollen data: {k}.")
    except requests.RequestException as r:
        print(f"Error fetching pollen data: {r}.")
        sys.exit(1)