from flask import Flask, request, redirect, url_for, render_template, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'SECRETKEY'


def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if session.get('role_id') != 0:
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
                       role_id INTEGER NOT NULL DEFAULT 1,
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
                ("admin", generate_password_hash("admin"), "admin", 0),
                ("user", generate_password_hash("user"), "user", 1)
            ])
        conn.commit()


@app.route('/')
def home():
    print(session)
    return render_template('index.html')


@app.route('/get_session_data', methods=['GET'])
def get_session_data():
    if 'user_id' in session:
        return jsonify({
            'user_id': session['user_id'],
            'username': session['username'],
            'role_id': session['role_id']
        })
    else:
        return jsonify({'message': 'No session data found'}), 404


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()  # Получаем JSON-данные из тела запроса
        if not data:
            return jsonify({"message": "No data provided"}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"message": "Please provide all fields"}), 400

        # Проверка на существование пользователя с таким именем
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({"message": "Username already exists"}), 400

            # Хэширование пароля перед сохранением
            hashed_password = generate_password_hash(password)

            # Вставка нового пользователя в базу данных
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, hashed_password))
            conn.commit()

            # Получаем id нового пользователя
            cursor.execute('SELECT id, role_id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            # Добавление данных пользователя в сессию
            session.clear()
            session['user_id'] = user[0]
            session['username'] = username
            session['role_id'] = user[1]  # Можно добавить роль или другие данные

            return jsonify({"message": "Registration successful", "success": True}), 200

    return jsonify({"message": "Method not allowed"}), 405


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()  # Получаем JSON-данные из тела запроса
        if not data:
            return jsonify({"success": False, "message": "Данные не были переданы."}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"success": False, "message": "Заполните все поля."}), 400

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password, role_id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                session.clear()
                session['user_id'] = user[0]
                session['role_id'] = user[2]
                session['username'] = username
                return jsonify({"success": True, "message": "Вход выполнен успешно."})
            else:
                return jsonify({"success": False, "message": "Неверное имя пользователя или пароль."}), 401
    return render_template('login-form.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/whatsapp')
def whatsapp():
    return render_template('whatsapp.html')


@app.route('/order')
def order():
    return render_template('order-page.html')


@app.route('/add_order', methods=['POST'])
def add_order():
    phone = request.form.get('phone')
    category = request.form.get('category')
    comments = request.form.get('comments')
    url = request.form.get('url')

    if not phone or not category or not url:
        return jsonify({"message": "Пожалуйста, заполните все обязательные поля"}), 400

    try:
        # Соединяемся с базой данных
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()

            # Получаем тип услуги по категории
            cursor.execute('''SELECT id FROM work_types WHERE title = ?''', (category,))
            type_id = cursor.fetchone()

            if not type_id:
                return jsonify({"message": "Категория услуги не найдена"}), 400

            type_id = type_id[0]

            # Добавляем заказ в таблицу orders
            cursor.execute('''
                INSERT INTO orders (user_id, type_id, comment, files)
                VALUES (?, ?, ?, ?)
            ''', (1, type_id, comments, url))  # user_id=1 для примера

            conn.commit()

        return jsonify({"message": "Заказ успешно добавлен!"}), 200

    except Exception as e:
        return jsonify({"message": f"Ошибка при добавлении заказа: {str(e)}"}), 500


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
