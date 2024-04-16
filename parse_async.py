import csv
import time
from bs4 import BeautifulSoup
import asyncio
import aiohttp

from models import Door
from constants import URL, URL_ROOT
from utils import async_calculate_time_decorator
from parse_sync import ParserBaseclass


class HSRParserAsync(ParserBaseclass):
    def __init__(self, url: str, character_url_first_part: str):
        super().__init__(url, character_url_first_part)

    @async_calculate_time_decorator
    async def parse(self) -> None:
        self.create_csv()
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                character_divs = soup.findAll("div", class_='avatar-card card')
                tasks = [self._process_character(character_div) for character_div in character_divs]
                await asyncio.gather(*tasks)
        self.write_in_csv()

    async def _process_character(self, character_div) -> None:
        character_url = URL_ROOT + character_div.find('a').attrs.get('href')
        character_name = character_url.split(CHARACTER_URL_FIRST_PART)[1]
        self._create_character(character_name, character_url)
        await self._parse_individual_character(character_url, character_name)

    async def _parse_individual_character(self, character_url: str, character_name: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(character_url) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                self.characters[character_name].real_name = soup.find('div', class_='character-top').find('strong').text
                self.characters[character_name].element = soup.find('div', class_='character-top').\
                    find('strong').attrs.get('class')[0]
                relic_divs = soup.find('div', class_='relics row row-cols-xxl-2 row-cols-xl-2 row-cols-1').\
                    findChildren('div', class_='col')
                relic_items_div = relic_divs[0].findAll("div", class_='relic-sets-rec')
                planetary_items_div = relic_divs[1].findAll("div", class_='relic-sets-rec')
                self.characters[character_name].best_relic_sets = self._get_relics(relic_items_div)
                self.characters[character_name].best_planetary_sets = self._get_relics(planetary_items_div)
                self.characters[character_name].best_stats = self._get_best_stats(soup)


if __name__ == "__main__":
    my_parser = HSRParserAsync(URL, CHARACTER_URL_FIRST_PART)
    asyncio.run(my_parser.parse())