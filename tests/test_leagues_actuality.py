import psycopg2
import requests
from bs4 import BeautifulSoup
import pytest

# Функция для получения данных из таблицы
def fetch_data():
    conn = psycopg2.connect(
        host="127.0.0.1",
        user="postgres",
        password="123456er",
        port="5432",
    )

    cur = conn.cursor()
    cur.execute("SELECT league, link FROM championships")
    data = cur.fetchall()
    conn.close()

    return data

# Функция для сравнения строк, игнорируя символы, кроме букв и цифр
def clean_string(s):
    return ''.join(filter(str.isalnum, s)).lower()

# Проверка что ссылка на лигу актуальна и назваеие лиги не поменяли
@pytest.mark.parametrize("league, link", fetch_data(), ids=lambda item: item)
def test_links_match(league, link):
    response = requests.get(link)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, 'html.parser')
    element = soup.find(class_='heading__name').text.strip().lower()

    assert clean_string(element) == clean_string(league)
