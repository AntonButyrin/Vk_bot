import json
import re
import datetime
from random import randint, choice


with open('voyages.json', 'r', encoding='utf-8') as read_file:
    loaded_json_file = json.load(read_file)

re_city = re.compile(r"[а-яА-Я]\w{1,11}")
re_date = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
re_phone = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
lol = {}


def random_choices():
    """ Ищет подходящую строчку с датой и городами город """
    creator = list()
    cities = ["Белгород", "Москва", "Сочи", "Воронеж", "Краснодар", "Екатеринбург",
              "Махачкала", "Чита", "Владивосток", "Анапа", "Саратов", "Самара"]
    while True:
        choice_city = choice(cities)
        for voyage_string in loaded_json_file.values():
            city_from = re.match(re_city, voyage_string[0]).group()
            if choice_city in city_from:
                # Если есть совпадения, то разбирает на нужные части строку
                city_to = re.match(re_city, voyage_string[1]).group()
                found_data = re.search(re_date, voyage_string[0])
                creator.append(city_from)
                creator.append(city_to)
                if found_data is None:
                    a, b, c = voyage_string[0].split()
                    found_data = b + " " + c
                    creator.append(found_data)
                else:
                    result_data = found_data[0]
                    creator.append(result_data)
                return creator
