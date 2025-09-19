

valid_cases_ = [
    "St. Louis, United States",         # Period in city name
    "O'Fallon, United States",          # Apostrophe in city name
    "Coeur d'Alene, United States",     # Apostrophe and lowercase particle
    "Newcastle-upon-Tyne, United Kingdom",  # Hyphenated city name
    "Fort McMurray, Canada",            # Compound city name
    "Saint-Pierre, France",             # Hyphenated with accented country
    "San José, Costa Rica",             # Accented character in city
    "Québec, Canada",                   # Accented character in city
    "Dún Laoghaire, Ireland",           # Accented and compound
    "Nuku'alofa, Tonga",                # Polynesian okina character
]

valid_cases = [
    "St. John's, Canada",              # Apostrophe and period
    "N'Djamena, Chad",                # Apostrophe at start
    "Ho Chi-Minh, Vietnam",           # Hyphenated compound
    "Port-au-Prince, Haiti",         # Multiple hyphens
    "Dzaoudzi, Mayotte",             # Rare city name
    "São Tomé, São Tomé and Príncipe", # Accented characters
    "Nuuk, Greenland",               # Non-sovereign country
    "Avarua, Cook Islands",          # Island nation
    "Funafuti, Tuvalu",              # Micronation
    "Tórshavn, Faroe Islands",       # Nordic diacritics
    "Saint-Denis, Réunion",          # French overseas region
    "Honiara, Solomon Islands",      # Multi-word country
    "Pago Pago, American Samoa",     # US territory
    "Mariehamn, Åland Islands",      # Special characters
    "Lomé, Togo",                    # Accented city
    "Zürich, Switzerland",           # Umlaut
    "Bogotá, Colombia",              # Acute accent
    "Reykjavík, Iceland",            # Icelandic characters
    "Ulan-Ude, Russia",              # Hyphenated Cyrillic transliteration
    "San Andrés, Colombia",          # Spanish compound
]

invalid_cases = [
    "123ville, United States",          # Digits in city name
    "City@Name, United States",         # Special character (@)
    "City!, United States",             # Exclamation mark
    "City#, United States",             # Hash symbol
    "City$, United States",             # Dollar sign
    "City%, United States",             # Percent symbol
    "City?, United States",             # Question mark
    "City/Name, United States",         # Slash
    "City\\Name, United States",        # Backslash
    "City_Name, United States",         # Underscore
    "Moscow123, Russia",             # Digits in city
    "Moscow!, Russia",               # Exclamation mark
    "Moscow@Russia",                 # Missing comma
    "Moscow,Russia",                 # No space after comma (if strict)
    "Moscow,, Russia",               # Double comma
    "Moscow; Russia",                # Semicolon instead of comma
    "Moscow:Russia",                 # Colon instead of comma
    "Moscow/ Russia",                # Slash instead of comma
    "Moscow\\ Russia",               # Backslash
    "Moscow - Russia",               # Hyphen instead of comma
    "Moscow, Ru$$ia",                # Symbols in country
    "Moscow, RUS!",                  # Shouting + punctuation
    "Moscow, Ru<script>",           # Injection attempt
    "Moscow, Ru\nssia",              # Embedded newline
    "Moscow, Ru\tssia",              # Tab character
    "Moscow, Ru\rssia",              # Carriage return
    "Moscow, ",                      # Missing country
    ", Russia",                      # Missing city
    "Moscow Russia",                 # Missing comma
    "Moscow,123",                    # Numeric country
]

from gmaps_package import get_geocode
from helper_functions import validate_input
from requests import HTTPError
import time

for name in invalid_cases:
    try:
        location = validate_input(name)
        get_geocode(location)
        print(f".- Succesfully saved => '{location}'")
        print("")
    except (AttributeError, IndexError, HTTPError, ValueError, NameError) as e:
        print(f"Error geocoding {name}. {e}")
        time.sleep(0.7)
        continue

print("All done!")