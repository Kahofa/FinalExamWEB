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
                       phone TEXT NOT NULL DEFAULT '+77777777777',
                       comment TEXT,
                       files TEXT,
                       FOREIGN KEY (user_id) REFERENCES users(id)
                       FOREIGN KEY (type_id) REFERENCES work_types(id)
                   )
               ''')
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
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"message": "Please provide all fields"}), 400

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({"message": "Username already exists"}), 400

            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, hashed_password))
            conn.commit()
            cursor.execute('SELECT id, role_id FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            session.clear()
            session['user_id'] = user[0]
            session['username'] = username
            session['role_id'] = user[1]
            return jsonify({"message": "Registration successful", "success": True}), 200

    return jsonify({"message": "Method not allowed"}), 405


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
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
    if session.get('username') is not None:
        return render_template('order-page.html')
    else:
        return redirect('/login')


@app.route('/add_order', methods=['POST'])
def add_order():
    phone = request.form.get('phone')
    category = request.form.get('category')
    comments = request.form.get('comments')
    url = request.form.get('url')

    if not phone or not category or not url:
        return jsonify({"message": "Пожалуйста, заполните все обязательные поля"}), 400
    try:
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT id FROM work_types WHERE title = ?''', (category,))
            type_id = cursor.fetchone()
            if not type_id:
                return jsonify({"message": "Категория услуги не найдена"}), 400
            type_id = type_id[0]
            cursor.execute('''
                INSERT INTO orders (user_id, type_id, phone, comment, files)
                VALUES (?, ?, ?, ?, ?)
            ''', (session.get('user_id'), type_id, phone, comments, url))
            conn.commit()
        return jsonify({"message": "Заказ успешно добавлен!"}), 200
    except Exception as e:
        return jsonify({"message": f"Ошибка при добавлении заказа: {str(e)}"}), 500


@app.route('/admin')
@admin_required
def admin():
    with sqlite3.connect('database.db') as conn:
        sort_by = request.args.get('sort_by', default=None)
        cursor = conn.cursor()

        if sort_by == 'type':
            cursor.execute('''
                            SELECT orders.id, orders.user_id, orders.phone, orders.comment, orders.files, work_types.title AS category
                            FROM orders
                            JOIN work_types ON orders.type_id = work_types.id ORDER BY orders.type_id
                        ''')
            orders = cursor.fetchall()
        elif sort_by == 'id':
            cursor.execute('''
                            SELECT orders.id, orders.user_id, orders.phone, orders.comment, orders.files, work_types.title AS category
                            FROM orders
                            JOIN work_types ON orders.type_id = work_types.id ORDER BY orders.id
                        ''')
            orders = cursor.fetchall()
        else:
            cursor.execute('''
                            SELECT orders.id, orders.user_id, orders.phone, orders.comment, orders.files, work_types.title AS category
                            FROM orders
                            JOIN work_types ON orders.type_id = work_types.id
                        ''')
            orders = cursor.fetchall()
    return render_template('admin.html', orders=orders)


@app.route('/admin/update', methods=['POST'])
@admin_required
def update_orders():
    try:
        data = request.form
        order_ids = data.getlist('order_id')
        user_ids = data.getlist('user_id')
        phones = data.getlist('phone')
        types = data.getlist('type')
        comments = data.getlist('comment')
        files = data.getlist('files')

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            for i in range(len(order_ids)):
                cursor.execute('''
                    UPDATE orders SET user_id = ?, phone = ?, type_id = (SELECT id FROM work_types WHERE title = ?),
                    comment = ?, files = ? WHERE id = ?
                ''', (user_ids[i], phones[i], types[i], comments[i], files[i], order_ids[i]))
            conn.commit()
        return redirect(url_for('admin'))
    except Exception as e:
        print("Exception")
        return redirect(url_for('admin'))


@app.route('/admin/delete/<int:order_id>', methods=['POST'])
@admin_required
def delete_order(order_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
    return redirect(url_for('admin'))


@app.route('/reset')
def reset_session():
    session.clear()
    print(session)
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
