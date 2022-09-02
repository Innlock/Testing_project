import sqlite3
from sqlite3 import Error


def sql_connection(name):
    try:
        con = sqlite3.connect(name)
        return con
    except Error:
        print(Error)


con = sql_connection('posts.db')
cursorObj = con.cursor()
ex = "DROP TABLE IF EXISTS posts;"
cursorObj.execute(ex)
ex = '''
CREATE TABLE posts (
    id integer PRIMARY KEY,
    id_post integer,
    getter text,
    note text,
    good text,
    unit text,
    amount integer,
    issued integer,
    date_time text
);'''
cursorObj.execute(ex)
con.commit()

connection = sqlite3.connect('posts.db')

cur = connection.cursor()
attachDatabaseSQL = "ATTACH DATABASE ? AS processing"
dbSpec = ("processing.db",)
cur.execute(attachDatabaseSQL, dbSpec)

attachDatabaseSQL = "ATTACH DATABASE ? AS invoices"
dbSpec = ("invoices.db",)
cur.execute(attachDatabaseSQL, dbSpec)

posts = cur.execute('SELECT company.id, processing.id, company.getter, company.note, company.good, company.unit, company.amount'
                    ', processing.issued, processing.date_time '
                    'FROM processing, company where company.note = processing.number_note').fetchall()
print(posts)

for post in posts:
    print(post)
    cur.execute(
        "INSERT INTO posts (id, id_post, getter, note, good, unit, amount, issued, date_time) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        post
        )

connection.commit()
connection.close()
