import requests
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError
from details.main_selectors import Selectors
import sys

class SeasonsCollector:
    def __init__(self, link):
        self.champ = link
        self.all_links = None
        self.seasons = 5

    def get_links(self):
        archive_link = f'{self.champ}/archive'
        response = requests.get(archive_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        pre_link = f"{'/'.join(self.champ.split('/')[:-1])}/"
        self.all_links = [pre_link + i.get('href').split('/')[2] for cnt, i in
                          enumerate(soup.select('.archive__season a'))
                          if cnt < self.seasons]
        return self.all_links


class SeasonsHandler:
    def __init__(self, links):
        self.links = links
        self.browser = sync_playwright().start().chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.pages = []

    def open_pages(self):
        for link in self.links:
            page = self.context.new_page()
            page.goto(link)
            self.pages.append(page)
            print(self.pages)

    def click_to_bottom(self):
        for page in self.pages:
            while True:
                try:
                    elements = page.query_selector_all(Selectors.show_more)
                    if len(elements) == 0:
                        break
                    elements[0].click()
                    page.wait_for_load_state('networkidle', timeout=300000)
                except TimeoutError:
                    continue
                import time
                time.sleep(1)

    def get_links_to_matches(self, sport_selector):
        all_links = []
        for page in self.pages:
            all_matches = page.query_selector_all(sport_selector)
            for match in all_matches:
                match_id = match.get_attribute('id')
                href = '/'.join(f'{page.url}'.split('/')[:3]) + '/match/' + match_id[4:]
                all_links.append(href)
            print(len(all_links))
        return all_links

    def close_all(self):
        for page in self.pages:
            page.close()
        self.context.close()
        self.browser.close()
        print('browser has been closed')


def link_collerctor(url):
    links_champ = SeasonsCollector(url).get_links()
    handler = SeasonsHandler(links_champ)
    handler.open_pages()
    handler.click_to_bottom()
    matches_links = handler.get_links_to_matches(Selectors.bb_all_matches)
    handler.close_all()
    file_name = '-'.join(url.split('/')[-2:])
    with open(f"details\\txt_links\\{file_name}.txt", "w") as file:
        file.write("\n".join(matches_links))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python link_collector.py [url]')
        sys.exit(1)
    arg = sys.argv[1]
    link_collerctor(arg)

