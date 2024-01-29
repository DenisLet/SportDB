import psycopg2
import subprocess
import os
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
                    self.process_coefs()

                    match_data = (self.league_id, self.match_title[1],
                                  self.match_title[3], self.match_title[4])

                    if self.is_match_exists(match_data):
                        print(f"Match already exists: {self.match_title}")
                        break  # Прекращаем обработку всех оставшихся ссылок
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






class Basketball(MatchHandler):
    def __init__(self, links, url):
        super().__init__(links, url)


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
            total_ft INTEGER
        );
        """

        cur.execute(create_matches_table_query)

        # SQL-запрос для создания таблицы match_details
        create_match_details_table_query = """
        CREATE TABLE IF NOT EXISTS details (
            match_id INTEGER PRIMARY KEY REFERENCES matches(match_id),
            home_q1 INTEGER,
            away_q1 INTEGER,
            home_q2 INTEGER,
            away_q2 INTEGER,
            home_q3 INTEGER,
            away_q3 INTEGER,
            home_q4 INTEGER,
            away_q4 INTEGER,
            home_ot INTEGER,
            away_ot INTEGER,
            home_win REAL,
            away_win REAL,
            total REAL,
            handicap REAL,
            hc_q1 REAL
        );
        """

        cur.execute(create_match_details_table_query)

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


    def save_to_database(self, title, scores, coefs):
        if not title or not scores or not coefs:
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
            insert_match_query = """
            INSERT INTO matches (league_id, match_date, start_time, team_home, team_away, league_name, stage,
                                home_score, away_score, home_score_ft, away_score_ft, total_ft)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING match_id
            """
            cur.execute(insert_match_query, title)
            match_id = cur.fetchone()[0]

            # SQL-запрос для вставки данных в таблицу match_details
            insert_details_query = """
            INSERT INTO details (match_id, home_q1, away_q1, home_q2, away_q2, home_q3, away_q3,
                                  home_q4, away_q4, home_ot, away_ot, home_win, away_win, total, handicap, hc_q1)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(insert_details_query, (match_id,) + scores + coefs)

            conn.commit()

        except Exception as e:
            print('Error with saving')
            print(e)

        conn.close()


    def process_scoreline(self):
        home_parts = Selectors.home_part
        away_parts = Selectors.away_part
        try:
            home_scores = [self.get_int_score(self.page.query_selector(part)) for part in home_parts]
            away_scores = [self.get_int_score(self.page.query_selector(part)) for part in away_parts]
            scores_data = [item for pair in zip(home_scores, away_scores) for item in pair]
        except Exception as e:
            scores_data = [None]*10
            print('Erorr with scoreline handling', e.with_traceback())

        self.scoreline = tuple(scores_data)
        print(scores_data)

    def process_coefs(self):
        def process_coef_button(selector):
            self.page.wait_for_selector(selector, timeout=3000)
            element = self.page.query_selector(selector)

            if element:
                element.click()
                self.page.wait_for_selector(Selectors.coef_box)
                all_coefs = [i.inner_text() for i in self.page.query_selector_all(Selectors.coef_box)]
                return self.find_average_value(all_coefs)
            return None
        try:
            self.page.query_selector(Selectors.odds_on_bar).click()
            self.page.wait_for_selector(Selectors.coef_box)
        except:
            print('No odds section')
            pass

        # try:
        #     check_all_coefs = self.page.query_selector(Selectors.home_away)
        #     if check_all_coefs:
        #         coefs_text = self.page.query_selector(Selectors.coef_box).inner_text().split()[:2]
        #         home_win = float(coefs_text[0])
        #         away_win = float(coefs_text[1])
        #     else:
        #         home_win, away_win = 1.0, 1.0
        #
        #
        # except Exception as e:
        #     print('Fail with win/win coefs ', e.with_traceback())
        #     home_win, away_win = 1.0, 1.0

        try:
            if self.page.query_selector(Selectors.home_away):
                coefs_text = self.page.query_selector(Selectors.coef_box).inner_text().split()[:2]
                home_win = float(coefs_text[0])
        except:
            home_win = 1.0


        try:
            if self.page.query_selector(Selectors.home_away):
                coefs_text = self.page.query_selector(Selectors.coef_box).inner_text().split()[:2]
                away_win = float(coefs_text[1])
        except:
            away_win = 1.0


        try:
            average_total = process_coef_button(Selectors.total_button)
        except Exception as e:
            print(f"Error processing total button: {e}")
            average_total = None

        try:
            average_handicap = process_coef_button(Selectors.handicap_button)
        except Exception as e:
            print(f"Error processing handicap button: {e}")
            average_handicap = None

        try:
            average_handicap_q1 = process_coef_button(Selectors.handicap_quarter1)
        except Exception as e:
            print(f"Error processing handicap quarter 1 button: {e}")
            average_handicap_q1 = None

        coefs = (home_win, away_win, average_total, average_handicap, average_handicap_q1)
        self.coefs = coefs
        print(self.coefs,'<-')


    @staticmethod
    def find_average_value(coefline):
        k = None
        value = None
        min_diff = 100
        for case in coefline:
            current_total = case.split()[0]
            k1, k2 = list(map(float, case.split()[1:3]))
            diff = abs(k1 - k2)
            if diff < min_diff:
                min_diff = diff
                value = current_total
        print(f"The total/handicap with the smallest diff is: {value}")
        return float(value)


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



urls = [
"https://www.basketball24.com/south-korea/kbl",
"https://www.basketball24.com/sweden/basketligan",
"https://www.basketball24.com/switzerland/sb-league"
]


for url in urls:

    subprocess.run(['python', 'link_collector.py', url], check=True)
    file_name = '-'.join(url.split('/')[-2:])
    print(file_name)
    with open(f"details\\txt_links\\{file_name}.txt", 'r') as file:
        links = [line.strip() for line in file.readlines()]

    basketball_handler = Basketball(links, url)
    basketball_handler.open_browser_and_process_links()

