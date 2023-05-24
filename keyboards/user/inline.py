import math

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from database import models
from sqlalchemy import and_

movies_cd = CallbackData("show_movies", "level", "year", "genre", "page", "movie")

def make_movies_cd(level: int, year: str = "2019", genre: str = "0",page: str = "1", movie: str = "0") -> CallbackData:
    return movies_cd.new(level=level, year=year, genre=genre, page=page, movie=movie)

async def menu_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()

    movies = len(await models.Movie.query.gino.all())
    buttons = [
        {'text': f'Сериалы ({movies})', 'callback_data': make_movies_cd(level=0)}
    ]

    for button in buttons:
        markup.insert(
            InlineKeyboardButton(**button)
        )

    return markup

async def choose_year_keyboard() -> InlineKeyboardMarkup:
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=2)

    available_years = [f"{year}" for year in range(2019, 2024)]
    for year in available_years:
        callback_data = make_movies_cd(level=CURRENT_LEVEL + 1, year=year)
        movies = len(await models.Movie.query.where(models.Movie.year == year).gino.all())
        if bool(movies):
            markup.insert(
                InlineKeyboardButton(
                    text=f"{year} ({movies})",
                    callback_data=callback_data
                )
            )

    markup.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data='menu'
        )
    )
    
    return markup
 
async def choose_genre_keyboard(year: str) -> InlineKeyboardMarkup:
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=2)

    genres = await models.Genre.query.gino.all()
    for genre in genres:
        callback_data = make_movies_cd(level=CURRENT_LEVEL + 1, year=year, genre=genre.name)
        movies = len(await models.Movie.query.where(and_(
            models.Movie.genres.contains(genre.name),
            models.Movie.year == year
        )).gino.all())
        if bool(movies):
            markup.insert(
                InlineKeyboardButton(
                    text=f"{genre.name} ({movies})",
                    callback_data=callback_data
                )
            )

    markup.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data=make_movies_cd(level=CURRENT_LEVEL - 1, year=year)
        )
    )
    
    return markup

async def choose_movie_keyboard(year: str, genre: str, current_page: str = '1') -> InlineKeyboardMarkup:
    CURRENT_LEVEL = 2
    current_page = int(current_page)
    markup = InlineKeyboardMarkup(row_width=2)

    movies = await models.Movie.query.where(and_(
            models.Movie.genres.contains(genre),
            models.Movie.year == year
        )).order_by(models.Movie.rate).gino.all()
    MAX_ITEMS_PER_PAGE=20
    MAX_PAGES = math.ceil(len(movies)/MAX_ITEMS_PER_PAGE)
    next_page = movies[(current_page*MAX_ITEMS_PER_PAGE)-MAX_ITEMS_PER_PAGE:current_page*MAX_ITEMS_PER_PAGE]

    for movie in next_page:
        callback_data = make_movies_cd(level=CURRENT_LEVEL + 1,year=year, genre=genre, movie=movie.idx)
        markup.insert(
            InlineKeyboardButton(
                text=f"⭐️({movie.rate}) {movie.title}",
                callback_data=callback_data
            )
        )

    markup.row(
        InlineKeyboardButton(
            text='<<',
            callback_data=make_movies_cd(level=CURRENT_LEVEL, year=year, genre=genre,page=(current_page -1) if current_page != 1 else current_page)
        )
    )
    markup.insert(
        InlineKeyboardButton(
            text='>>',
            callback_data=make_movies_cd(level=CURRENT_LEVEL, year=year, genre=genre,page=(current_page + 1) if not current_page >= MAX_PAGES else current_page)
        )
    )

    markup.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data=make_movies_cd(level=CURRENT_LEVEL - 1)
        )
    )

    return markup

async def show_movie_keyboard(year: str,genre: str, page: str, movie: str) -> InlineKeyboardMarkup:
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup()
    movie = await models.Movie.query.where(models.Movie.idx == int(movie)).gino.first()
    buttons = [
        {'text': 'Смотреть', 'url': movie.href},
        # {'text': 'Назад', 'callback_data': make_movies_cd(level=CURRENT_LEVEL - 1, genre=genre, page=page)}
    ]
    for button in buttons:
        markup.row(
            InlineKeyboardButton(**button)
        )
    return markup