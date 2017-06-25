# -*- coding: utf-8 -*-

def BirthCityExist(src, city):
    # Opening data file in read mode
    cityList = open(src, "r")

    #Initialising boolean response
    city_exist = False

    for ligne in cityList:
        city_name = ligne.rstrip('\n\r') #Removing '\n\r' from ligne
        if city_name == city :
            city_exist = True
            break


    # Closing data file
    cityList.close()

    return city_exist


#Testing
print BirthCityExist("french_cities_data.txt", "Quimper")