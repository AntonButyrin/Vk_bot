import os
import requests
import random
from io import BytesIO

from PIL import ImageDraw, ImageFont, Image


class Ticket:
    """инициализирует основные данные(размер, нахождения файлов)"""
    TEMPLATE_PATH = 'files/ticket.png'
    FONT_PATH = 'files/Roboto-Regular.ttf'
    FONT_SIZE = 30
    FONT_SIZE_DATA = 40
    BLACK = (0, 0, 0, 255)
    TO_OFFSET = (10, 190)
    FRO_OFFSET = (379, 190)
    DATA_OFFSET = (700, 190)
    COMMENT_OFFSET = (180, 268)
    AVATAR_SIZE = 50
    AVATAR_OFFSET = (10, 315)
    user_id = 1

    def __init__(self, context, randoms=None):
        """Принимает файлы из словаря"""
        self.randoms = randoms
        self.fro = context['fro']
        self.to = context['to']
        self.data = context['data']
        self.place = context['place']
        self.comment = context['comment']

    def create(self):
        """Создает билет"""
        if self.randoms is None:
            self.randoms = random.random()
        ticket = Image.open(self.TEMPLATE_PATH).convert('RGBA')
        font = ImageFont.truetype(font=self.FONT_PATH, size=self.FONT_SIZE_DATA)
        # write on the ticket
        draw = ImageDraw.Draw(ticket)
        draw.text(self.TO_OFFSET, self.to, font=font, fill=self.BLACK)
        draw.text(self.FRO_OFFSET, self.fro, font=font, fill=self.BLACK)
        draw.text(self.DATA_OFFSET, self.data, font=font, fill=self.BLACK)
        font = ImageFont.truetype(font=self.FONT_PATH, size=self.FONT_SIZE)
        draw.text(self.COMMENT_OFFSET, self.comment, font=font, fill=self.BLACK)
        # make avatar
        response = requests.get(url=f'https://www.peterbe.com/avatar.png?seed=0.{self.randoms}')
        avatar_file_like = BytesIO(response.content)
        avatar = Image.open(avatar_file_like)
        new_avatar = avatar.resize((200, 200))
        shape = [(210, 518), (9, 311)]
        draw.rectangle(shape, outline="black", width=4)
        # paste avatar on the ticket
        ticket.paste(new_avatar, self.AVATAR_OFFSET)
        temp_file = BytesIO()
        ticket.save(temp_file, 'png')
        temp_file.seek(0)
        return temp_file
