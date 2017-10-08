"""
BSD 3-Clause License

Copyright (c) 2017, Mairie de Paris
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import re

from fuzzywuzzy import fuzz, process

from franceocr.config import BASEDIR


with open(BASEDIR + '/french_cities.txt', 'r', encoding="UTF-8") as f:
    FRENCH_CITIES = [city.replace("\n", "") for city in f.readlines()]


def delete_numbers(s):
    # Cutting at the first number
    new_s = re.split('(\d+)', s)[0].strip()

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
