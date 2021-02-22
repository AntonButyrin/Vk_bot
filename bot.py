#!/usr/bin/env python3
import requests
from random import randint

from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter, FileHandler
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from pony.orm import db_session

import handlers
from towns import random_choices, json_creater
from models import UserState, Registration

try:
    from settings import GROUP_ID, TOKEN, SCENARIOS, INTENTS, DEFAULT_ANSWER
except ImportError:
    TOKEN = None
    print('Для работы бота')
    exit()

log = getLogger("bot")


def conf_logging():
    stream_handler = StreamHandler()
    stream_handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(message)s"))
    stream_handler.setLevel(INFO)

    file_handler = FileHandler("logs_bot.log", encoding="utf-8")
    file_handler.setFormatter(Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M'))
    file_handler.setLevel(DEBUG)

    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    log.setLevel(DEBUG)


class Bot:
    """
    Получает главные атрибуты для  бота:
    self.group_id = group --- получает id группы где будет находиться бот
    self.token = _token   --- получает уникальный идентификатор(Токен) для  бота
    self.vk = vk_api.VkApi(token=_token) --- подключает бибиотеку в  класс и передает токен
    self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id) --- настраивает передачу данных
    от вк к боту(указывает токен бота и группу в которой он установлен)
    self.api = self.vk.get_api() --- подключает возможность взаимодействовать с пользователем
    """

    def __init__(self, group, _token):
        self.group_id = group
        self.token = _token
        self.vk = VkApi(token=_token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """
        Создает постоянное "прослушивание вк нашим ботом" и смотрит события которые он присылает.
        Если есть события с которыми бот не умеет работать он присылает исключение.
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('ошибка в событии')

    @db_session
    def on_event(self, event):
        """
        Смотрит, если  событие-сообщение, то  отправляет пользователю его дубликат.
        Если нет, то смотрит какое событие  пришло
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info("отправляем сообщение назад")
            return

        user_id = str(event.message.peer_id)
        text = event.message.text
        state = UserState.get(user_id=user_id)

        self.search_intent(text, user_id, state)

    def search_intent(self, text, user_id, state):
        """
        Ищет интенты для работы с ними
        """
        for intent in INTENTS:
            if any(token in text for token in intent['tokens']):
                if state is not None:
                    state.delete()
                if intent['answer']:
                    self.send_text(intent['answer'], user_id)
                else:
                    self.start_scenario(user_id, intent['scenario'])
                break
        else:
            if state is not None:
                self.continue_scenario(text, state, user_id)
            else:
                self.send_text(DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        """
        Отправляет сообщение
        """

        log.debug('Отправляем сообщение пользователю')
        self.api.messages.send(
            message=f' {text_to_send}',
            random_id=randint(0, 2 ** 20),
            peer_id=user_id)

    def send_image(self, image, user_id):
        """
        Отправляет картинку
        """
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            attachment=attachment,
            random_id=randint(0, 2 ** 20),
            peer_id=user_id)
        log.info('Отправлен билет пользователю.')

    def send_step(self, step, user_id, context):
        """
        Выбирает вариант отправки сообщение или картинку
        """
        if 'text' in step:
            print(step['text'], context)
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name):
        """
        Начинает сценарий
        """
        scenario = SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, context={})
        UserState(user_id=user_id, scenario_name=scenario_name, step_name=first_step, context={})

    def continue_scenario(self, text, state, user_id):
        """
        Продолжает идти по сценарию
        """
        steps = SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, context=state.context)
            if next_step['next_step']:
                # switch next step
                state.step_name = step['next_step']
            else:
                # registration in db
                Registration(
                    user_id=user_id,
                    fro=str(state.context['fro']),
                    to=str(state.context['to']),
                    data=str(state.context['data']),
                    place=str(state.context['place']),
                    result=str(state.context['result']),
                    comment=str(state.context['comment']),
                    phone=str(state.context['phone']),
                )
                state.delete()
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)
            self.send_text(text_to_send, user_id)


if __name__ == "__main__":
    conf_logging()
    random_choices()
    json_creater()
    bot = Bot(GROUP_ID, TOKEN)
    bot.run()
