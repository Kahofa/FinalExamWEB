from flask import Flask, render_template, session, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'SECRETKEY'


def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Access denied.")
            return redirect(url_for('home'))
        return func(*args, **kwargs)

    return decorated_view


# Создание базы данных и таблиц
def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()

        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS roles (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       role TEXT NOT NULL UNIQUE
                   )
               ''')

        cursor.execute('''
                           CREATE TABLE IF NOT EXISTS work_types (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               title TEXT NOT NULL UNIQUE,                            
                               description TEXT
                           )
                       ''')

        cursor.execute('''SELECT COUNT(*) FROM roles''')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''INSERT INTO roles (role) VALUES ('admin')''')
            cursor.execute('''INSERT INTO roles (role) VALUES ('user')''')

        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       email TEXT NOT NULL UNIQUE,
                       username TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL,
                       role_id INTEGER NOT NULL,
                       FOREIGN KEY (role_id) REFERENCES roles(id)
                   )
               ''')

        cursor.execute('''
                   CREATE TABLE IF NOT EXISTS orders (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER NOT NULL,
                       type_id INTEGER NOT NULL,
                       comment TEXT,
                       files TEXT,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                       FOREIGN KEY (type_id) REFERENCES work_types(id)
                   )
               ''')

        # Добавляем тестовые данные (если пусто)
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO users (username, password, email, role_id)
                VALUES (?, ?, ?, ?)
            ''', [
                ("admin", "admin", "admin", 0),
                ("user", "user", "user", 1)
            ])
        conn.commit()


@app.route('/')
def home():
    # проверка с бд
    session['role'] = 'user'

    return render_template('index.html')


@app.route('/whatsapp')
def whatsapp():
    return render_template('whatsapp.html')


@app.route('/order')
def order():
    return render_template('order-page.html')


@app.route('/login')
def login():
    return render_template('login-form.html')


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
