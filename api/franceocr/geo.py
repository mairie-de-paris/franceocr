import operator
import re

from fuzzywuzzy import fuzz

from franceocr.config import BASEDIR


with open(BASEDIR + '/french_cities.txt', 'r') as f:
    FRENCH_CITIES = [city.replace("\n", "") for city in f.readlines()]


def delete_numbers(s):
    # Cutting at the first number
    new_s = re.split('(\d+)', s)[0]

    # Removing the last space character
    if new_s[-1] == ' ':
        new_s = new_s[:-1]

    return new_s


def city_exists(city):
    # Initialising boolean and list response
    city_exists = False
    similar_cities = {}

    # Cutting the city name to the first number and applying title case
    city_modified = delete_numbers(city).upper()

    # Looking for the city in the city list
    for city_name in FRENCH_CITIES:
        concordance_score = fuzz.ratio(city_name, city_modified)
        if concordance_score == 100:
            city_exists = True
        if concordance_score >= 70:
            similar_cities[city_name] = concordance_score

    # Sorting the similar_cities dict by score
    similar_cities = sorted(similar_cities.items(), key=operator.itemgetter(1), reverse=True)
    # Keeping just the 5 cities that matched the most
    similar_cities = similar_cities[:5]
    # Correct city name is the city with the highest score
    city_modified = similar_cities[0][0]

    return city_exists, city_modified, similar_cities
