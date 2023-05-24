import shutil
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from database import models

from data.config import MEDIA_URL

class LostFilm(object):

    def __init__(self) -> None:
        self.date = datetime.now()
        self.monthes = {
            1: 'jan',
            2: 'feb',
            3: 'mar',
            4: 'apr',
            5: 'may',
            6: 'jun',
            7: 'jul',
            8: 'aug',
            9: 'sep',
            10: 'oct',
            11: 'nov',
            12: 'dec',
        }
        self.url = f'https://{self.date.day}{self.monthes[self.date.month]}.lostfilma.net'
        self.session = requests.Session()
        self.session.headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.available_years = [f"{year}" for year in range(2019, 2024)]
    
    def link_changer(self, old_link: str) -> str:
        splitted_link = old_link.split('.')[0]

        to_change = f'https://{self.date.day}{self.monthes[self.date.month]}'

        return old_link.replace(splitted_link, to_change)

    def _send_req(self,qurl: str):
        return self.session.get(
            self.url + qurl
        ).text

    def parse_finfo(self, finfo: str):
        keywords = {
            'Жанр':'genre',
            'Страна': 'country',
            'Озвучка': 'voiced_by'
        }
        new_finfo = {}
        for el in finfo.split('\n'):
            if len(el)> 0:
                sel = el.split(':')
                key = sel[0]
                value = sel[1]
                try:
                    new_finfo[keywords[key]] = value
                except KeyError:
                    continue
        return new_finfo

    def get_novelty_detail(self, href: str):
        soup = BeautifulSoup(self.session.get(href).text, 'lxml')

        return {
                'finfo':self.parse_finfo(soup.select_one('ul#finfo').text if soup.select_one('ul#finfo') is not None else "Жанр: -\nСтрана: -\nОзвучка: -"),
                'description': soup.select_one('div#serial-kratko').text if soup.select_one('div#serial-kratko') is not None else '-',
                'rate': soup.select_one('span.rat-imdb').text if soup.select_one('span.rat-imdb') is not None else '0.0'
            }
    
    async def save_novelty(self, novelty: dict):
        await models.Movie.create(
            title=novelty['title'],
            preview=str(novelty['img']),
            href=novelty['href'],
            year=novelty['year'],
            description=novelty['detail']['description'],
            rate=novelty['detail']['rate'],
            genres=novelty['detail']['finfo']['genre'].strip(),
            country=novelty['detail']['finfo']['country'].strip(),
            voiced_by=novelty['detail']['finfo']['voiced_by'].strip(),

        )

    async def parse_novelty(self, soup: BeautifulSoup, year: str):
        return [await self.save_novelty(novelty={
            'title': item.select_one('div.vi-title').text,
            'href':item.select_one('a').attrs.get('href'),
            'detail': self.get_novelty_detail(item.select_one('a').attrs.get('href')),
            'img': self.save_image(item.select_one('a > img').attrs.get('data-src')),
            'year': year
        }) for item in
            soup.select('div.video-item > div.vi-in')
            ]

    async def get_novelties(self, year: str):
        if year not in self.available_years:
            return []
        
        html = self._send_req(
            f'/serials/{year}/'
        )
        soup = BeautifulSoup(html, 'lxml')
        max_pages = int(soup.select('div.navigation > a')[-1].text)
        total_items = []
        items = await self.parse_novelty(soup=soup, year=year)
        total_items += items

        for page in range(2, max_pages + 1):
            html = self._send_req(
                f'/serials/{year}/page/{page}/'
            )
            soup = BeautifulSoup(html, 'lxml')

            items = await self.parse_novelty(soup=soup, year=year)
            total_items += items

        return total_items
         

    def save_image(self, path: str):
        self.session.stream = True
        response = self.session.get(
            self.url + path
        )
        
        file_name = MEDIA_URL / path.split('/')[-1]
        try:
            with open(file_name,'wb') as f:
                shutil.copyfileobj(response.raw, f)
        except PermissionError:
            self.save_image(path=path)
        self.session.stream = False

        return file_name




if __name__ == '__main__':
    lf = LostFilm()
    print(lf.get_novelties(year='2023'))