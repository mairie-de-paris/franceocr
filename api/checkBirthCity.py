# -*- coding: utf-8 -*-
import codecs
import re


def delete_numbers(s):
    return re.split('(\d+)',s)[0]


def convertCapitalWord(original_word):
    #convert CAPITAL LETTERS FIRSTNAME to Capital Letters Firstname
    newFirstName = original_word[0].upper()

    for lettre in original_word[1:len(original_word)-1]:
        newFirstName = newFirstName + lettre.lower()
    return newFirstName


def BirthCityExists(city):
    # Opening data file in read mode
    cityList = codecs.open("french_cities_data.txt", "r", "utf-8")

    # Initialising boolean response
    city_exists = False

    #Cutting the city name to the first space
    city_modified = convertCapitalWord(delete_numbers(city))

    #Looking for the city in the city list
    for ligne in cityList:
        city_name = ligne.rstrip('\n\r')  # Removing '\n\r' from ligne
        if city_name == city_modified:
            city_exists = True
            break

    # Closing data file
    cityList.close()

    return [city_exists, city_modified]


# Testing
print(BirthCityExists("Paris"))
