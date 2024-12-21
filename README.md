# Database using SQLite

## Name: `database.db`

### Structure of Database:

#### `roles`
*Purpose:* We need roles to give admins the opportunity to delete and check orders created by users.

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `role`: TEXT NOT NULL UNIQUE

**Standard Roles:**
- `(0, 'admin')`
- `(1, 'user')`

#### `work_types`
*Purpose:* Table of accessible types of work our company can do.

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `title`: TEXT NOT NULL UNIQUE
- `description`: TEXT

#### `users`
*Purpose:* Users table to give users feedback about their orders.

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `email`: TEXT NOT NULL UNIQUE
- `username`: TEXT NOT NULL UNIQUE
- `password`: TEXT NOT NULL
- `role_id`: INTEGER NOT NULL DEFAULT 1 // Value of 'user' role
  - **Foreign Key** (`role_id`): References `roles(id)`

#### `orders`
*Purpose:* Orders that users create and associated contact information.

- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER NOT NULL
- `type_id`: INTEGER NOT NULL
- `phone`: TEXT NOT NULL DEFAULT '+77777777777'
- `comment`: TEXT
- `files`: TEXT
  - **Foreign Key** (`user_id`): References `users(id)`
  - **Foreign Key** (`type_id`): References `work_types(id)`

---

## Database Usage in Project

### Register and Login:
- **Relevant Lines:** `main.py:120`, `main.py:149`
  ```python
  cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                 (username, email, hashed_password)) // You are not able to register as admin
  cursor.execute('SELECT id, password, role_id FROM users WHERE username = ?', (username,))
  ```

### Adding a New Order:
- **Relevant Lines:** `main.py:196`
  ```python
  cursor.execute('''INSERT INTO orders (user_id, type_id, phone, comment, files) VALUES (?, ?, ?, ?, ?)''',
                 (session.get('user_id'), type_id, phone, comments, url))
  ```

### Show Orders with Sorting:
- **Relevant Lines:** `main.py:213-232`
  ```python
  cursor.execute('''
      SELECT orders.id, orders.user_id, orders.phone, orders.comment, orders.files, work_types.title AS category
      FROM orders
      JOIN work_types ON orders.type_id = work_types.id ORDER BY orders.type_id
  ''')
  ```
  // Sorting by orders `type_id` and getting `title` as category from `work_types` matching by `id` etc.

### Delete Orders as Admin:
- **Relevant Lines:** `main.py:242`
  ```python
  cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
  ```

---

## How to Use Interface:

### As a User:

1. **Sign Up or Login** on the website (localhost):
   - URL: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)

2. **Explore Company Information:**
   - Visit the main page: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
   - Check our works and media. Choose a project type by clicking on one of the cards to open the order creation page.

3. **Create an Order:**
   - URL: [http://127.0.0.1:5000/order](http://127.0.0.1:5000/order)
   - Fill in the phone line and choose a work type.
   - Optionally, add a comment about your order and provide a link to a reference for the work you want.
   - Click on the "Send Order" button. We will contact you later.

### As an Admin:

1. **Log in as Admin:**
   - URL: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
   - Base admin credentials for testing:
     - Username: `admin`
     - Password: `admin`

2. **Access the Admin Page:**
   - URL: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

3. **Manage Orders:**
   - View actual orders.
   - Sort orders by "Type" and "Order ID." To sort, click on the title of the table column you want to sort.
   - Delete non-actual orders by clicking the "Delete" button next to the respective order row.

