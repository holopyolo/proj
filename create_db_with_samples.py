import sqlite3
import os
import hashlib
from init_db import SAMPLE_PROBLEMS

# Удаляем существующую базу данных
db_file = 'coding_platform.db'
if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f"Удалена существующая база данных {db_file}")
    except Exception as e:
        print(f"Не удалось удалить базу данных: {e}")
        db_file = 'coding_platform_new.db'
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Удалена альтернативная база данных {db_file}")

# Создаем новую базу данных
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Создаем таблицы
cursor.executescript('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);

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
);

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
);
''')

# Создаем пользователей
users = [
    ('admin', 'admin', 'admin'),  # username, password, role
    ('teacher', 'teacher', 'teacher')
]

for username, password, role in users:
    # Хеширование пароля
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_password, role)
    )

# Добавляем примеры задач
for problem in SAMPLE_PROBLEMS:
    cursor.execute(
        """
        INSERT INTO problems 
        (title, description, topic, difficulty, test_cases, initial_code, created_by) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            problem['title'],
            problem['description'],
            problem['topic'],
            problem['difficulty'],
            problem['test_cases'],
            problem['initial_code'],
            1  # created_by (admin user id)
        )
    )

# Сохраняем изменения
conn.commit()

# Проверяем количество задач
cursor.execute("SELECT COUNT(*) FROM problems")
count = cursor.fetchone()[0]
print(f"Добавлено задач: {count}")

# Записываем результат в файл
with open('db_created.txt', 'w', encoding='utf-8') as f:
    f.write(f"База данных {db_file} создана\n")
    f.write(f"Добавлено задач: {count}\n")
    
    # Список задач
    cursor.execute("SELECT id, title, topic, difficulty FROM problems")
    problems = cursor.fetchall()
    f.write("\nСписок задач:\n")
    for p in problems:
        f.write(f"ID: {p[0]}, Название: {p[1]}, Тема: {p[2]}, Сложность: {p[3]}\n")

conn.close()

print(f"База данных {db_file} успешно создана с {count} задачами") 