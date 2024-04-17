import requests
import csv

import random

from bs4 import BeautifulSoup


from models import Door
from constants import FIRST_PAGE_URL, URL_ROOT
from utils import calculate_time_decorator


class ParserBaseclass:

    def __init__(self, url: str):
        self.doors = {}
        self.url = url

    def _create_door(self, door_url: str) -> None:
        self.doors.setdefault(door_url, Door(
            url=door_url,
        ))

    @staticmethod
    def _get_best_stats(soup) -> dict:
        stats_divs = soup.find('div', class_='main-stats').findAll('div', class_="col")
        return {item.find('div', class_="stats-header").text.strip():
                [stat.text for stat in item.findAll('div', class_='hsr-stat')]
                for item in stats_divs}

    @staticmethod
    def create_csv():
        with open("door_list.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "url",
                "description"
            ])

    def write_in_csv(self):
        with open("character_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            for character in self.characters.values():
                writer.writerow([
                    character.real_name,
                    character.url,
                    character.element,
                    character.best_relic_sets,
                    character.best_planetary_sets,
                    character.best_stats
                ])


class DoorParserSync(ParserBaseclass):

    def __init__(self, url: str):
        super().__init__(url)

    @calculate_time_decorator
    def parse(self) -> None:
        self.create_csv()
        soup = BeautifulSoup(requests.get(url=self.url).text, 'lxml')
        paginate_items = soup.findAll("li", class_='pagination__item')
        for paginate_item in paginate_items:
            if 'active' in paginate_item['class']:
                self._parse_page_with_doors(FIRST_PAGE_URL)
            else:
                doors_page_url = paginate_item.find('a').get('href')
                doors_page_url.replace("http", "https")
                self._parse_page_with_doors(doors_page_url)


            # self._create_character(character_name, character_url)
            # self._parse_individual_character(character_url, character_name)
        # self.write_in_csv()

    def _parse_page_with_doors(self, doors_page_url: str) -> None:
        soup = BeautifulSoup(requests.get(url=doors_page_url).text, 'lxml')
        doors = soup.findAll('div', class_='products__item')
        for door in doors:
            door_url = door.find('a').get('href')
            door_url = URL_ROOT + door_url
            self._parse_door(door_url)

    def _parse_door(self, door_url: str) -> None:
        soup = BeautifulSoup(requests.get(url=door_url).text, 'lxml')
        door_img = soup.find("div", class_='product__img-wrap').find('img').get('src')
        door_img_url = URL_ROOT + door_img
        image_bytes = requests.get(door_img_url).content
        with open(f"pics/{random.randint(1, 10000)}.jpg", "wb") as file:
            file.write(image_bytes)


if __name__ == "__main__":
    my_parser = DoorParserSync(FIRST_PAGE_URL)
    my_parser.parse()
