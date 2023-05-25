from aiogram import types 
from loader import dp, bot
from database import models
from utils.lostfilm import LostFilm
from sqlalchemy import or_
lf = LostFilm()


async def answer_movies(query: types.InlineQuery,bot_info, movies: list):
    await query.answer(
            results=[types.InlineQueryResultArticle(
                id=movie.idx,
                title=f"{movie.title} ({movie.rate}⭐️) ({movie.country})",
                description=movie.genres,
                thumb_url="https://belofflab.com/static/vpn/img/video-camera.png",
                input_message_content=types.InputTextMessageContent(
                                                                        message_text=f"Фильм: {movie.title} ({movie.rate}⭐️) ({movie.country})\n\n{movie.description}\n\n<a href='https://t.me/{bot_info.username}?start=watch{movie.idx}'>Смотреть</a>"
                                                                    )
            ) for movie in movies[:50]]
        )

@dp.inline_handler()
async def search_movie(query: types.InlineQuery):
    bot_info = await bot.get_me()
    if len(query.query) > 0:
        movies = await models.Movie.query.where(
                or_(
                    models.Movie.title.contains(query.query.capitalize()),
                    models.Movie.genres.contains(query.query)
                )
            ).gino.all()
        return await answer_movies(query=query,bot_info=bot_info, movies=movies)
    
    movies = await models.Movie.query.gino.all()
    return await answer_movies(query=query, bot_info=bot_info, movies=movies)