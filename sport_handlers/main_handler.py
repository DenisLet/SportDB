import psycopg2
from playwright.sync_api import sync_playwright
from abc import ABC, abstractmethod
from details.main_selectors import Selectors

class MatchHandler:
    def __init__(self, links, url):
        self.links = links
        self.__url = url
        self.match_title = None
        self.scoreline = None
        self.coefs = None
        self.league_id = None
        self.league_name = None
        self.browser = None
        self.context = None
        self.page = None
        if links != 1:
            self.get_league_id()

    def reset_data(self):
        self.match_title = None
        self.scoreline = None
        self.coefs = None

    def is_match_exists(self, match_data):
        conn = psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="123456er",
            port="5432",
        )
        cur = conn.cursor()

        select_match_query = """
        SELECT match_id FROM matches
        WHERE league_id = %s
          AND match_date = %s
          AND team_home = %s
          AND team_away = %s
        """
        cur.execute(select_match_query, match_data[:4])
        match_id = cur.fetchone()

        conn.close()

        return match_id is not None

    def open_browser_and_process_links(self):
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page_empty = self.context.new_page()


            self.create_match_tables()

            for link in self.links:
                try:
                    self.page = self.context.new_page()

                    self.reset_data()

                    self.page.goto(link)
                    self.page.wait_for_selector(Selectors.scoreline)
                    self.process_title()
                    self.process_scoreline()
                    self.process_coefs()

                    match_data = (self.league_id, self.match_title[1],
                                  self.match_title[3], self.match_title[4])

                    if self.is_match_exists(match_data):
                        print(f"Match already exists: {self.match_title}")
                        continue  #Продолжаем -> continue, прекращаем обработку всех оставшихся ссылок(когда обновляю уже накачанную базу) -> break
                    else:
                        print('-----')
                        print(self.match_title)
                        print(self.scoreline)
                        print(self.coefs)
                        print('-----')
                        self.page.close()
                        self.save_to_database(self.match_title,
                                              self.scoreline,
                                              self.coefs)
                except Exception as e:
                    print(e)
                    self.save_failed_link(link)
                    print('ok8')
                    self.page.close()
                    continue



    def save_failed_link(self, link):
        file_name = '-'.join(self.__url.split('/')[-2:])
        with open(f"details\\txt_links\\failed\\{file_name}.txt", 'a') as file:
            file.write(link + "\n")
            print('Failed link has been saved')

    @abstractmethod
    def create_match_tables(self):
        pass

    @abstractmethod
    def process_scoreline(self):
        pass

    @abstractmethod
    def process_coefs(self):
        pass

    @abstractmethod
    def save_to_database(self, title, scores, coefs):
        pass


    def process_title(self):
        team_home_element = self.page.query_selector(Selectors.team_home)
        team_away_element = self.page.query_selector(Selectors.team_away)
        tournament_header = self.page.query_selector(Selectors.tournament)
        date_header = self.page.query_selector(Selectors.date_and_time)
        final_score_header = self.page.query_selector(Selectors.final_score)
        full_time_score = self.page.query_selector(Selectors.fulltime_score)

        team_home = team_home_element.text_content().strip() if team_home_element else None
        team_away = team_away_element.text_content().strip() if team_away_element else None
        tournament = tournament_header.text_content() if tournament_header else None
        date_and_time = date_header.text_content() if date_header else None
        final_score = final_score_header.text_content() if final_score_header else None
        score_ft = full_time_score.text_content() if full_time_score else None

        stage = self.extract_stage(tournament)
        date, start_time = self.extract_date_and_time(date_and_time)
        home_score, away_score, home_score_ft, away_score_ft = self.extract_scores(final_score, score_ft)
        total_result = home_score_ft + away_score_ft

        match_data =  (self.league_id, date, start_time,
                       team_home, team_away, self.league_name, stage,
                       home_score, away_score, home_score_ft, away_score_ft, total_result)
        self.match_title = match_data

    def extract_stage(self, tournament):
        if tournament:
            print(tournament)
            colon_index = tournament.find(":")
            if colon_index != -1:
                stage_part = tournament[colon_index + 1:].strip()
                if '-' in stage_part:
                    stage = stage_part.split('-', 1)[1].strip().upper()
                    if 'ALL' in stage:
                        stage = 'ALL STARS'
                    if "SEMI-FINALS" in stage or "QUARTER-FINALS" in stage or "1/8-FINALS" in stage or "PROMOTION" in stage:
                        stage = "PLAY OFFS"
                    elif "FINAL" in stage:
                        stage = "FINAL"
                    elif "ROUND" in stage or "NBA" in stage:
                        stage = "MAIN"
                    return stage

        return "MAIN"

    def extract_date_and_time(self, date_and_time):
        if date_and_time:
            date = date_and_time.split()[0]
            start_time = date_and_time.split()[1]
            return date, start_time
        return None, None

    def extract_scores(self, final_score, score_ft):
        if final_score:
            home_score = int(final_score.split('-')[0])
            away_score = int(final_score.split('-')[1])
        else:
            home_score, away_score = None, None

        if score_ft is None:
            home_score_ft, away_score_ft = home_score, away_score
        else:
            home_score_ft = int(score_ft.split('-')[0].replace('(',''))
            away_score_ft = int(score_ft.split('-')[1].replace(')',''))

        return home_score, away_score, home_score_ft, away_score_ft


    def get_league_id(self):
        conn = psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="123456er",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute(f"SELECT id, league FROM championships WHERE link = '{self.__url}'")
        data = cur.fetchall()
        conn.close()
        print(data)
        self.league_id = data[0][0]
        self.league_name = data[0][1]
