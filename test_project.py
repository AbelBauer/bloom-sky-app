'''
Test Suite for Weather Recommendations and Gmaps Forecast Integration

This module contains unit tests for validating the behavior and output of weather-related functions,
including expressive recommendations, pollen level handling, and Google Maps-based forecast retrieval.

Test Coverage:
--------------
- get_recommendation():
    Verifies output structure, emoji presence, and phrasing based on weather and pollen inputs.
    Includes tests for malformed data, invalid types, and fallback behavior when inputs are missing or incorrect.

- default_pollen():
    Checks that the pollen data returned for the default location is a valid tuple of known levels.

- default_forecast():
    Ensures the forecast function returns a well-formed tuple with correct types for all weather metrics.

Validation Focus:
-----------------
- Type checking and error raising for invalid inputs
- Phrase and emoji presence in expressive recommendation strings
- Graceful handling of unknown or malformed pollen levels
- Structural integrity of forecast and pollen data

Dependencies:
-------------
- pytest
- recommendations
- gmaps_pollen
- gmaps_package

Note:
-----
This suite assumes that external API calls are either cached or rate-limited via decorators.
Tests are designed to be deterministic and avoid real-time API dependencies where possible.
'''


from recommendations import get_recommendation
from gmaps_pollen import default_pollen
from gmaps_package import default_forecast
import pytest

def test_get_recommendation_content():
    result = get_recommendation(is_daytime=True, temp=-2, rain_prob=75, humidity=75, grass_pollen_risk="low",
                                tree_pollen_risk="Unknown", weed_pollen_risk="low")

    assert isinstance(result, str)
    assert "🌾" in result
    assert "🌳" in result
    assert "🌿" in result
    assert "🕗➱🌅" in result
    assert "The day's in full swing" in result
    assert "Grass pollen levels are low right now" in result
    assert "⭕   ➜ 🌳 Tree pollen 'N/A'" in result
    assert "frostbite" in result

def test_recommendation_invalid_weather_data():
    with pytest.raises(TypeError):
        get_recommendation(is_daytime=True, temp="N/A", rain_prob="N/A", humidity="N/A",
                           grass_pollen_risk="low", tree_pollen_risk="low", weed_pollen_risk="low")

def test_recommendation_invalid_daytime_type():
    with pytest.raises(TypeError):
        get_recommendation(is_daytime=1, temp=12.5, rain_prob=54, humidity=44,
                           grass_pollen_risk="low", tree_pollen_risk="low", weed_pollen_risk="very low")

def test_recommendation_invalid_temp_type():
    with pytest.raises(TypeError):
        get_recommendation(is_daytime=False, temp="low", rain_prob=54, humidity=44,
                           grass_pollen_risk="low", tree_pollen_risk="low", weed_pollen_risk="very low")

def test_recommendation_invalid_rain_humidity_type():
    with pytest.raises(TypeError):
        get_recommendation(is_daytime=False, temp=12.5, rain_prob="high", humidity="low",
                           grass_pollen_risk="low", tree_pollen_risk="low", weed_pollen_risk="very low")


def test_recommendation_malformed():
    result = get_recommendation(is_daytime=False, temp=12.5, rain_prob=54, humidity=44, grass_pollen_risk="veyow",
                                tree_pollen_risk="wer", weed_pollen_risk="asft")
    assert "⭕   ➜ 🌾 Grass pollen 'N/A'" in result
    assert "⭕   ➜ 🌳 Tree pollen 'N/A'" in result
    assert "⭕   ➜ 🌿 Weed pollen 'N/A'" in result

def test_default_pollen():
    result = default_pollen() # Gmaps pollen levels for HOME (default location)
    assert isinstance(result, tuple)
    assert len(result) == 3
    pollen_levels = ["very low", "low", "moderate", "high", "very high", "unknown"]
    grass, tree, weed = result # unpack pollen levels from Gmaps
    assert grass.lower() in pollen_levels
    assert tree.lower() in pollen_levels
    assert weed.lower() in pollen_levels

def test_default_forecast():
    result = default_forecast()
    assert len(result) == 5
    assert isinstance(result, tuple)

    is_day, temp, description, rain, humidity = result
    try:
        assert isinstance(is_day, bool)
        assert isinstance(temp, int)
        assert isinstance(description, str)
        assert isinstance(rain, int)
        assert isinstance(humidity, int)
    except ValueError:
        raise