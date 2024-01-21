import psycopg2


def fetch_data():
    conn = psycopg2.connect(
        host="127.0.0.1",
        user="postgres",
        password="123456er",
        port="5432"
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM championships")
    data = cur.fetchall()
    conn.close()

    return data

data_table1 = fetch_data()




for i in data_table1:
    print(i)
