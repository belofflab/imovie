import asyncio

from aiogram import types
from database import models
from loader import dp
from utils.lostfilm import LostFilm


@dp.message_handler(commands='fill')
async def fillgenre(message: types.Message) -> None:
    genres = {
            'триллер', 'мюзикл', 'музыка', 'военный', 
            'ужасы', 'аниме', 'криминал', 'приключения', 
            'фантастика', 'история', 'комедия', 'биография', 
            'спорт', 'семейный', 'мультфильм', 'ток-шоу', 
            'мелодрама', 'документальный', 'реальное ТВ', 
            'боевик', 'вестерн', 'драма', 'детектив', 'фэнтези'
        }
    loop = asyncio.get_event_loop()
    lf = LostFilm()
    for genre in genres:
        await models.Genre.create(
            name=genre
        )

    # for year in range(2019, 2023+1):
    #     await lf.get_novelties(year=str(year))
    await message.answer('Success')