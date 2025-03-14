import sqlite3
import os

# Удаляем существующие базы данных
if os.path.exists('coding_platform.db'):
    os.remove('coding_platform.db')

# Создаем базу данных и таблицы
conn = sqlite3.connect('coding_platform.db')
c = conn.cursor()

# Создаем таблицу пользователей
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
)
''')

# Создаем таблицу проблем
c.execute('''
CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    topic TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    test_cases TEXT NOT NULL,
    initial_code TEXT,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users (id)
)
''')

# Создаем таблицу решений
c.execute('''
CREATE TABLE solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    error TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (problem_id) REFERENCES problems (id)
)
''')

# Создаем пользователя admin
c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
          ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin'))  # пароль: admin

# Создаем пару тестовых задач
c.execute('''
INSERT INTO problems (title, description, topic, difficulty, test_cases, initial_code, created_by)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('Тестовая задача 1', 'Описание тестовой задачи 1', 'Тест', 'Легкая',
     '[{"input": [1, 2], "expected": 3}]', 'def test_func():\n    pass', 1))

c.execute('''
INSERT INTO problems (title, description, topic, difficulty, test_cases, initial_code, created_by)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('Тестовая задача 2', 'Описание тестовой задачи 2', 'Алгоритмы', 'Средняя',
     '[{"input": [3, 4], "expected": 7}]', 'def test_func2():\n    pass', 1))

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close() 