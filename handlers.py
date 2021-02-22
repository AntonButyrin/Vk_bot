import json
import re

from generate_ticket import Ticket

with open('voyages.json', 'r', encoding='utf-8') as read_file:
    loaded_json_file = json.load(read_file)

re_city = re.compile(r"[а-яА-Я]\w{1,11}")
re_date = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
re_phone = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')


def handle_from(text, context):
    """Создает шаблон города и ищет существует ли город"""
    counter = len(loaded_json_file)
    context['fro'] = None
    for i, j in loaded_json_file.items():
        counter -= 1
        city1 = re.match(re_city, j[0]).group()
        if city1 in text:
            context['fro'] = text
            if 'voyage' in context:
                context['voyage'].append(j)
            else:
                context['voyage'] = list()
                context['voyage'].append(j)
        if counter == 0 and context['fro'] is not None:
            return True
    else:
        name_var = list()
        for m in loaded_json_file.values():
            city1 = re.match(re_city, m[0]).group()
            name_var.append(city1)
        name_var = set(name_var)
        context['fail'] = ", ".join(name_var)
        return False


def handle_to(text, context):
    """Создает шаблон города и ищет существует ли город"""
    counter = len(context['voyage'])
    name = list()
    for j in context['voyage']:
        counter -= 1
        city2 = re.match(re_city, j[1]).group()
        if city2 == text:
            context['to'] = text
            name.append(j)
            if counter == 0:
                del context['voyage']
                context['voyage'] = list()
                context['voyage'].extend(name)
                return True
    else:
        name_var = list()
        for m in context['voyage']:
            city2 = re.match(re_city, m[1]).group()
            name_var.append(city2)
        name_var = set(name_var)
        context['fail'] = ", ".join(name_var)
        return False


def handle_date(text, context):
    """Ищет существует ли дата в списке"""
    n = 0
    for j in context['voyage']:
        nice = re.search(re_date, j[0])
        if nice is not None:
            if text in nice[0]:
                n += 1
                context['data'] = text
                del context['voyage']
                context['voyage'] = list()
                context['voyage'].extend(j)
                context["number_voyage"] = str(n), j
                return True
    else:
        for counter, voyage in enumerate(context['voyage']):
            context['fail'] = str(counter + 1) + '.', ' '.join(voyage)
        return False


def handle_voyage(text, context):
    """Выбирает рейс"""
    if text in context['number_voyage'][0]:
        context['result'] = context['number_voyage'][1]
        return True
    else:
        return False


def handle_place(text, context):
    """Определяет количество мест"""
    list_to_place = ['1', '2', '3', '4', '5']
    if text in list_to_place:
        context['place'] = text
        return True
    else:
        return False


def handle_comment(text, context):
    """Комментирует"""
    context['comment'] = text
    return True


def handle_yesno(text, context):
    """Проверяет точность"""
    if 'да' in text:
        return True
    else:
        context['continue'] = False
        return False


def handle_phone(text, context):
    """Определяет номер"""
    match = re.findall(re_phone, text)
    if match:
        context['phone'] = match[0]
        return True
    else:
        return False


def generate_ticket_handler(context):
    return Ticket(context).create()
