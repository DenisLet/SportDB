import os
import json
import psycopg2
from .details.bb_links import links_men, links_women

'''    Class create json and sql table with basketball
    championships(and link for them to flashscore.com 
    choosen by yourself manually before
'''


class Championships:

    def __init__(self, sport=None):
        self.all_leagues = {}
        self.sport = sport
        print(self.sport)

    def add_league(self, data, gender):
        for l in data:
            country = l.split('/')[3].replace('-', ' ').title()
            league = l.split('/')[4].replace('-', ' ').upper()
            link = 'https:/' + '/'.join(l.split('/')[1:5])

            if country not in self.all_leagues:
                self.all_leagues[country] = {'Men': {}, 'Women': {}}

            if league not in self.all_leagues[country][gender]:
                self.all_leagues[country][gender][league] = link

    def process_data(self, data_men, data_women):
        self.add_league(data_men, 'Men')
        self.add_league(data_women, 'Women')

    def save_to_json(self, filename='all_champs.json'):
        folder_path = 'details'
        file_path = os.path.join(folder_path, filename)
        json_data = json.dumps(self.all_leagues, indent=4)
        with open(file_path, 'w') as file:
            file.write(json_data)


    def connect_to_db(self, dbname):
        return psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="123456er",
            port="5432",
            dbname=dbname
        )

    def create_postgresql_db(self, dbname):
        conn = self.connect_to_db(dbname)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Проверка - есть база или нет
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        database_exists = cur.fetchone()

        # Если базы данных нет, создаю новую
        if not database_exists:
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"Database '{dbname}' created successfully")

        conn.close()

        # Подключаюсь к созданной или существующей базе
        conn = self.connect_to_db(dbname)
        cur = conn.cursor()

        # Проверка таблицы в базе
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'championships')")
        table_exists = cur.fetchone()[0]

        # Если таблицы нет, создаю новую
        if not table_exists:
            create_table_query = '''
                CREATE TABLE championships (
                    id SERIAL PRIMARY KEY,
                    country VARCHAR(100),
                    gender VARCHAR(10),
                    league VARCHAR(100),
                    link VARCHAR(255),
                    CONSTRAINT unique_country_gender_league UNIQUE (country, gender, league)
                )
            '''
            cur.execute(create_table_query)
            conn.commit()
            print("Table created successfully in PostgreSQL")


        for country, genders in self.all_leagues.items():
            for gender, leagues in genders.items():
                for league, link in leagues.items():
                    insert_query = f'''
                        INSERT INTO championships (country, gender, league, link) 
                        VALUES ('{country}', '{gender}', '{league}', '{link}')
                        ON CONFLICT (country, gender, league) DO NOTHING
                    '''
                    cur.execute(insert_query)
                    conn.commit()

        conn.close()

championships = Championships()
championships.process_data(links_men, links_women)
championships.save_to_json()
championships.create_postgresql_db(dbname="sportdb")


