import psycopg2
from sport_handlers.main_handler import MatchHandler
from details.main_selectors import Selectors
import time


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
                   ADD CONSTRAINT unique_match_constraint UNIQUE (league_id, match_date, start_time, team_home, team_away);
                   """

            cur.execute(add_constraint_query)
        except psycopg2.errors.DuplicateTable:
            pass

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
            # SQL запрос для вставки данных в таблицу matches
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
        home_win = None
        away_win = None
        average_total = None
        average_handicap = None
        average_handicap_q1 = None

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
        print(self.coefs, '<-')


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