from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, \
    url_for, flash, redirect
from werkzeug.exceptions import abort
import random


def get_db_connection():
    conn = sqlite3.connect('posts.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id_post = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT id_post, note,getter,date_time,issued '
                         'FROM posts group by note order by id ').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>',methods=('GET', 'POST'))
def post(post_id):
    conn = get_db_connection()
    post = get_post(post_id)
    headings = ["#", "good", "unit", "amount"]
    goods = conn.execute(f'SELECT ROW_NUMBER() OVER(ORDER BY good ASC) AS num,'  # нумерация в sql запросе
                         f'good, unit, amount FROM posts where id_post = {post_id}').fetchall()

    if request.method == 'POST':
        if request.form['submit_button'] == 'Выдать':
            con = get_db_connection()
            cursor = con.cursor()
            # current_time = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:19]
            current_time = "2020-01-01"
            cursor.execute(f'''UPDATE posts
            SET issued = {random.randint(0, 1)},
            date_time = "{current_time}"
            where id_post = "{post_id}"''')
            con.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('post.html', post=post, goods=goods, headings=headings)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/create', methods=('GET', 'POST'))
def create(posts=[]):  # posts - товары в текущей накладной
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cur = conn.cursor()
    goods_list = []
    goods = cur.execute('SELECT good, unit FROM posts group by good ').fetchall()
    for good in goods:
        goods_list.append(good['good'])
    # good - словарь: товар - единица
    # good_list - список товаров

    if request.method == 'POST':
        cursor = conn.cursor()

        getter = str(request.form['getter'])
        # good = str(request.form['good'])
        good = str(request.form.get('comp_select'))
        if good:
            unit = str([x for x in goods if x["good"] == good][0]['unit'])
        amount = 0
        if request.form['amount']:
            amount = int(request.form['amount'])
        date = str(request.form['date'])
        if not getter:
            flash('Название компании не заполнено')
        if not (good and amount):
            flash('Введите информацию о товаре')
        if getter and good and amount:
            # кнопка для создания накладной
            if request.form['submit_button'] == 'Create':
                p = cursor.execute("SELECT id_post from posts group by id_post").fetchall()
                id_post = cursor.execute("SELECT id_post from posts order by id_post desc limit 1").fetchone()
                id_post = id_post['id_post'] + 10
                if not posts:
                    posts.append([good, unit, amount])
                for p in posts:
                    good, unit, amount = p[0], p[1], p[2]
                    post = (id_post, getter, f"AB_{id_post}_{date}", good,
                            unit, amount+100, 0, "YYYY-MM-DD HH:MM:SS")
                    ex = '''INSERT INTO posts (id_post, getter, note,
                    good, unit, amount, issued, date_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                    cursor.execute(ex, post)
                    conn.commit()
                conn.close()
                posts.clear()
                return redirect(url_for('index'))
            # кнопка для добавления товара

            elif request.form['submit_button'] == 'Add':
                posts.append([good, unit, amount])
    return render_template('create.html', goods_list=goods_list,
                           goods=goods, posts=posts)
