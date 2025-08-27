import ee
ee.Initialize(project="utility-state-467714-p5")

clay = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select("b0")
sand = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select("b0")


point = ee.Geometry.Point([28.644800, 77.216721])  # lat and lon from location here!
clay_value = clay.reduceRegion(ee.Reducer.first(), point, scale=250)
sand_value = sand.reduceRegion(ee.Reducer.first(), point, scale=250)

print(clay_value.getInfo(), sand_value.getInfo())












def get_soil_texture(lat, lon):
    point = ee.Geometry.Point([lon, lat])
    clay = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select("b0")
    silt = ee.Image("OpenLandMap/SOL/SOL_SILT-WFRACTION_USDA-3A1A1A_M/v02").select("b0")
    sand = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select("b0")

    clay_val = clay.reduceRegion(ee.Reducer.first(), point, scale=250).get("b0").getInfo()
    silt_val = silt.reduceRegion(ee.Reducer.first(), point, scale=250).get("b0").getInfo()
    sand_val = sand.reduceRegion(ee.Reducer.first(), point, scale=250).get("b0").getInfo()

    return {"clay": clay_val, "silt": silt_val, "sand": sand_val}

