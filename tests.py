from unittest import TestCase
from unittest.mock import patch, Mock
from vk_api.bot_longpoll import VkBotMessageEvent
from pony.orm import db_session, rollback
from copy import deepcopy

import settings
from generate_ticket import Ticket
from random_str_for_tests import random_choices
from bot import Bot


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()

    return wrapper


class Test1(TestCase):

    a = random_choices()
    RAW_EVENT = {'type': 'message_new',
                 'object': {
                     'message': {'date': 1613667428, 'from_id': 522596326, 'id': 595, 'out': 0, 'peer_id': 522596326,
                                 'text': 'привет', 'conversation_message_id': 586, 'fwd_messages': [],
                                 'important': False,
                                 'random_id': 0, 'attachments': [], 'is_hidden': False}, 'client_info': {
                         'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'intent_subscribe',
                                            'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': True,
                         'carousel': False,
                         'lang_id': 0}},
                 'group_id': 198991770, 'event_id': '988a74fd06967382aa6b21d1ef3f760cada75dd1'}
    INPUTS_RANDOM = '10203040'
    INPUTS_IMAGE = {
        'fro': 'Самара',
        'to': 'Москва',
        'data': '2020-02-20',
        'place': '2',
        'comment': 'без детей рядом',
    }
    INPUTS = [
        'привет',
        '/ticket',
        a[0],
        a[1],
        a[2],
        '1',
        '1',
        'Хочу место без детей',
        'да',
        '+79077077777'
    ]

    EXPECTED_OUTPUTS = [
        settings.INTENTS[0]['answer'],
        settings.SCENARIOS['buy_ticket']['steps']['step1']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step2']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step3']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step4']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step5']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step6']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step7']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step8']['text'],
        settings.SCENARIOS['buy_ticket']['steps']['step9']['text'].format(
            fro='Краснодар', to='Москва', data='2021-04-01', result='1', place='2', comment='Хочу место без детей')

    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert len(real_outputs) == len(self.EXPECTED_OUTPUTS)

    def test_ticket_generation(self):
        with open('files/avatar.png', 'rb') as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()
        with patch('requests.get', return_value=avatar_mock):
            ticket_file = Ticket(self.INPUTS_IMAGE, self.INPUTS_RANDOM).create()
        with open('files/template.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
        assert ticket_file.read() == expected_bytes
