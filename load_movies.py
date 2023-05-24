import asyncio
from utils.lostfilm import LostFilm


asyncio.run(LostFilm().get_novelties('2019'))