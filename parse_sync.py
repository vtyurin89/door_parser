import requests
import csv
from bs4 import BeautifulSoup


from models import Door
from constants import URL, URL_ROOT
from utils import calculate_time_decorator


# TODO
# FIX parser UnicodeEncodeError


class ParserBaseclass:
    """
    This class was designed for website prydwen.gg.
    """
    def __init__(self, url: str, character_url_first_part: str):
        self.characters = {}
        self.url = url
        self.character_url_first_part = character_url_first_part

    @staticmethod
    def _clean_string(input_str):
        return input_str.encode('ascii', 'ignore').decode('utf-8')

    def _create_character(self, character_name: str, character_url: str) -> None:
        self.characters.setdefault(character_name, Character(
            url=character_url,
        ))

    def _get_relics(self, items_div) -> list:
        """
        Find the names of all relics in the div element and add them to the list.
        """
        result = []
        for item in items_div:
            if item.find('div', class_='split-sets row'):
                buttons = item.findAll('button', class_='accordion-button collapsed')
                relic_set = " + ".join([item.find_next('div').next_sibling.strip() for item in buttons])
                result.append(relic_set)
            else:
                relic_set = item.find('button', class_='accordion-button collapsed').\
                    find_next('div').next_sibling.strip()
                result.append(relic_set)
        return result

    @staticmethod
    def _get_best_stats(soup) -> dict:
        stats_divs = soup.find('div', class_='main-stats').findAll('div', class_="col")
        return {item.find('div', class_="stats-header").text.strip():
                [stat.text for stat in item.findAll('div', class_='hsr-stat')]
                for item in stats_divs}

    @staticmethod
    def create_csv():
        with open("character_log.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "name",
                "url",
                "element",
                "best_relic_sets",
                "best_planetary_sets",
                "best_stats"
            ])

    def write_in_csv(self):
        with open("character_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            for character in self.characters.values():
                try:
                    writer.writerow([
                        character.real_name,
                        character.url,
                        character.element,
                        character.best_relic_sets,
                        character.best_planetary_sets,
                        character.best_stats
                    ])
                except UnicodeEncodeError:
                    print('==================================================================================')
                    print(f"Unicode Encode error occurred with the character {character.real_name}")
                    print(f"Character INFO: {character.__dict__}")
                    print('==================================================================================')


class HSRParserSync(ParserBaseclass):

    def __init__(self, url: str, character_url_first_part: str):
        super().__init__(url, character_url_first_part)

    @calculate_time_decorator
    def parse(self) -> None:
        self.create_csv()
        soup = BeautifulSoup(requests.get(url=self.url).text, 'lxml')
        character_divs = soup.findAll("div", class_='avatar-card card')
        for character_div in character_divs:
            character_url = URL_ROOT + character_div.find('a').attrs.get('href')
            character_name = character_url.split(CHARACTER_URL_FIRST_PART)[1]
            self._create_character(character_name, character_url)
            self._parse_individual_character(character_url, character_name)
        self.write_in_csv()

    def _parse_individual_character(self, character_url: str, character_name: str) -> None:
        soup = BeautifulSoup(requests.get(url=character_url).text, 'lxml')
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
    my_parser = HSRParserSync(URL, CHARACTER_URL_FIRST_PART)
    my_parser.parse()