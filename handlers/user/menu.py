from aiogram import types
from data.config import MEDIA_URL
from database import models
from keyboards.user import inline
from loader import dp

async def get_or_create_user(user_id: int, username: str) -> models.User:
    user = await models.User.query.where(models.User.idx == user_id).gino.first()
    if user is not None:
        return user
    return await models.User.create(idx=user_id, username=username if username is not None else 'no username')

async def list_years(callback: types.CallbackQuery, **kwargs) -> None:
    markup = await inline.choose_year_keyboard()

    await callback.message.edit_text(
        text="За какой год смотрим?",
        reply_markup=markup
    )

async def list_genres(callback: types.CallbackQuery,year,  **kwargs) -> None:
    markup = await inline.choose_genre_keyboard(year=year)

    await callback.message.edit_text(
        text="Выберите жанр: ",
        reply_markup=markup
    )

async def list_movies(callback: types.CallbackQuery, year, genre, page, **kwargs) -> None:
    markup = await inline.choose_movie_keyboard( year=year, genre=genre, current_page=page)
    await callback.message.edit_text(
        text="Выберите фильм: ",
        reply_markup=markup
    )
async def show_movie(callback: types.CallbackQuery,year, genre, page, movie) -> None:
    markup = await inline.show_movie_keyboard(year=year, genre=genre, page=page, movie=movie)

    q_movie = await models.Movie.query.where(models.Movie.idx == int(movie)).gino.first()
    await callback.message.answer_photo(
        photo=types.InputFile(MEDIA_URL / q_movie.preview),
        caption=f"""
Фильм: <code>{q_movie.title}</code>

<b>{q_movie.description}</b>

Рейтинг (imdb): {q_movie.rate}
Страна: {q_movie.country}
Озвучка: {q_movie.voiced_by}
    
""",
        reply_markup=markup
    )

@dp.message_handler(commands='start')
async def start(message:types.Message) -> None:
    await get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username
    )
    markup = await inline.menu_keyboard()
    await message.answer(f'Добро пожаловать, {message.from_user.full_name}!', reply_markup=markup)

@dp.callback_query_handler(lambda c:c.data == 'menu')
async def menu(callback:types.CallbackQuery) -> None:
    markup = await inline.menu_keyboard()
    await callback.message.edit_text(f'Добро пожаловать, {callback.from_user.full_name}!', reply_markup=markup)


@dp.callback_query_handler(inline.movies_cd.filter())
async def movie_navigate(callback: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get("level")
    year = callback_data.get("year")
    genre = callback_data.get("genre")
    page = callback_data.get('page')
    movie = callback_data.get('movie')

    levels = {
        "0": list_years,
        "1": list_genres,
        "2": list_movies,
        "3": show_movie
    }

    current_level_function = levels[current_level]

    await current_level_function(
        callback,
        year=year,
        genre=genre,
        page=page,
        movie=movie
    )
