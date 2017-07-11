import codecs
import re
from fuzzywuzzy import fuzz
import operator

def delete_numbers(s):
    # Cutting at the first number
    new_s = re.split('(\d+)',s)[0]

    # Removing the last space character
    if new_s[-1] == ' ':
        new_s = new_s[:-1]

    return new_s

def birth_city_exists(city):
    # Opening data file in read mode
    city_list = codecs.open("french_cities_data.txt", "r", "utf-8")

    # Initialising boolean and list response
    city_exists = False
    similar_cities = {}

    # Cutting the city name to the first number and applying title case
    city_modified = delete_numbers(city).title()

    # Looking for the city in the city list
    for line in city_list:
        city_name = line.rstrip('\n\r')  # Removing '\n\r' from line

        concordance_score = fuzz.ratio(city_name, city_modified)
        if concordance_score == 100:
            city_exists = True
            similar_cities = {}
            break
        elif concordance_score >= 60:
            city_exists = True
            similar_cities[city_name] = concordance_score

    # Closing data file
    city_list.close()

    # In case the 100 score has not been reached
    if not similar_cities=={}:
        # Sorting the similar_cities dict by score
        similar_cities = sorted(similar_cities.items(), key=operator.itemgetter(1))
        similar_cities.reverse()
        # Keeping just the 5 cities that matched the most
        similar_cities = similar_cities[:5]
        # Correct city name is the city with the highest score
        city_modified = similar_cities[0][0]

    return city_exists, city_modified, similar_cities