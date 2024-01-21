import psycopg2
import subprocess
from playwright.sync_api import sync_playwright, TimeoutError
from details.main_selectors import Selectors
from abc import ABC, abstractmethod
import time

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
        self.get_league_id()

    def reset_data(self):
        self.match_title = None
        self.scoreline = None

    def open_browser_and_process_links(self):
        with sync_playwright() as p:
            self.browser = p.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page_empty = self.context.new_page()

            # Создаем таблицы перед обработкой матчей
            self.create_match_tables()

            for link in self.links:
                try:
                    self.page = self.context.new_page()
                    # Сбрасываем данные перед началом обработки ссылок
                    self.reset_data()
                    self.page.goto(link)
                    self.page.wait_for_selector(Selectors.scoreline)
                    self.process_title()
                    self.process_scoreline()
                    print('-----')
                    print(self.match_title)
                    print(self.scoreline)
                    print(self.coefs)
                    print('-----')
                    self.save_to_database(self.match_title, self.scoreline)
                    self.page.close()
                except Exception as e:
                    print(e)
                    self.save_failed_link(link)
                    print('ok8')
                    continue

    def save_failed_link(self, link):
        file_name = '-'.join(self.__url.split('/')[-2:])
        with open(f"details\\txt_links\\failed\\{file_name}.txt", 'a') as file:
            file.write(link + "\n")
            print('Failed link has been saved')

    def create_match_tables(self):
        conn = psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="123456er",
            port="5432"
        )
        cur = conn.cursor()

        # SQL-запрос для создания таблицы matches
        create_matches_table_query = """
        CREATE TABLE IF NOT EXISTS matches (
            match_id SERIAL PRIMARY KEY,
            league_id INTEGER,
            match_date DATE,
            start_time TIME,
            team_home VARCHAR(255),
            team_away VARCHAR(255),
            league_name VARCHAR(255),
            stage VARCHAR(255),
            home_score INTEGER,
            away_score INTEGER,
            home_score_ft INTEGER,
            away_score_ft INTEGER,
            home_q1 INTEGER,
            away_q1 INTEGER,
            home_q2 INTEGER,
            away_q2 INTEGER,
            home_q3 INTEGER,
            away_q3 INTEGER,
            home_q4 INTEGER,
            away_q4 INTEGER,
            home_ot INTEGER,
            away_ot INTEGER
        );
        """

        cur.execute(create_matches_table_query)

        try:
            add_constraint_query = """
                   ALTER TABLE matches
                   ADD CONSTRAINT unique_match_constraint UNIQUE (league_id, match_date, team_home, team_away);
                   """

            cur.execute(add_constraint_query)
        except psycopg2.errors.DuplicateTable:
            pass  # Игнорируем ошибку, если ограничение уже существует

        conn.commit()
        conn.close()


    @abstractmethod
    def process_scoreline(self):
        pass

    @abstractmethod
    def process_coefs(self):
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

        match_data =  (self.league_id, date, start_time,
                       team_home, team_away, self.league_name, stage,
                       home_score, away_score, home_score_ft, away_score_ft)
        self.match_title = match_data

    def extract_stage(self, tournament):
        if tournament:
            stage = tournament[tournament.find(":") + 1:].strip().split('-', 1)[1].strip().upper()
            if "FINAL" in stage:
                stage = "FINAL"
            elif "PLAY OFFS" in stage:
                stage = "PLAY OFFS"
            elif "ROUND" in stage:
                stage = "MAIN"
            return stage
        return None

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

    def save_to_database(self, match_data_list, scores_data_list):
        if not match_data_list or not scores_data_list:
            return

        conn = psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="123456er",
            port="5432",
        )
        cur = conn.cursor()

        try:
            # SQL-запрос для вставки данных в таблицу matches
            insert_data_query = """
            INSERT INTO matches (league_id, match_date, start_time, team_home, team_away, league_name, stage,
                                 home_score, away_score, home_score_ft, away_score_ft,
                                 home_q1, away_q1, home_q2, away_q2, home_q3, away_q3, home_q4, away_q4, home_ot, away_ot)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_data_query, match_data_list + scores_data_list)
            conn.commit()

        except Exception as e:
            print(e.with_traceback())

        conn.close()

class Basketball(MatchHandler):
    def __init__(self, links, url):
        super().__init__(links, url)

    def process_scoreline(self):
        home_parts = Selectors.home_part
        away_parts = Selectors.away_part

        home_scores = [self.get_int_score(self.page.query_selector(part)) for part in home_parts]
        away_scores = [self.get_int_score(self.page.query_selector(part)) for part in away_parts]

        scores_data = [item for pair in zip(home_scores, away_scores) for item in pair]

        self.scoreline = tuple(scores_data)
        print(scores_data)

    @staticmethod
    def get_int_score(element):
        if element:
            content = element.text_content()
            try:
                return int(content) if content else None
            except ValueError:
                return None
        else:
            return None





script_path = 'link_collector.py'
urls = ['https://www.basketball24.com/italy/lega-a']

for url in urls:
    command = ['python', script_path, url]
    subprocess.run(command, check=True)
    file_name = '-'.join(url.split('/')[-2:])
    with open(f"details\\txt_links\\{file_name}.txt", 'r') as file:
        links = [line.strip() for line in file.readlines()]

    basketball_handler = Basketball(links, url)
    basketball_handler.open_browser_and_process_links()