from random import randint, choice
import datetime
import json

creator = dict()


def random_choices():
    """ Генерирует дату, время, город """
    n = 0
    while n < 6:
        start = datetime.datetime.today()
        date = start + datetime.timedelta(days=randint(1, 365), hours=randint(1, 24), minutes=randint(1, 365))
        time1 = date.strftime('%Y-%m-%d %H:%M')
        time2 = date.strftime('%Y-%m-%d %H:%M')
        cities = ["Белгород", "Москва", "Сочи", "Воронеж", "Краснодар", "Екатеринбург",
                  "Махачкала", "Чита", "Владивосток", "Анапа", "Саратов", "Самара"]
        cs1 = choice(cities)
        cs2 = choice(cities)
        if cs1 == cs2:
            cs2 = choice(cities)
        if n == 2:
            time1 = time2 = "Каждую среду"
        if n == 5:
            time1 = "Раз в месяц"
        departure = cs1 + " " + time1
        coming = cs2 + " " + time2
        creator[n + 1] = coming, departure
        n += 1


def json_creater():
    """Записывает json-файл"""
    json_result = json.dumps(creator, ensure_ascii=False)
    with open('voyages.json', 'w', encoding='utf-8') as f:
        f.write(json_result)


if __name__ == "__main__":
    random_choices()
    json_creater()
