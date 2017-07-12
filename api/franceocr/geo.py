import operator
import re

from fuzzywuzzy import fuzz, process

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


def city_exists(city_name):
    similar_cities = {}

    # Uppercase city name cut to the first number
    city_name = delete_numbers(city_name).upper()

    # Find 5 most similar cities as a sorted (city, concordance_score) list
    similar_cities = process.extract(city_name, FRENCH_CITIES, limit=5, scorer=fuzz.ratio)

    city_modified = similar_cities[0][0]
    # The city exists if the best score is 100
    city_exists = similar_cities[0][1] == 100

    return city_exists, city_modified, similar_cities
