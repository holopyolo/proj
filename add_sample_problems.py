import sqlite3
from init_db import SAMPLE_PROBLEMS

# Подключаемся к существующей базе данных
conn = sqlite3.connect('coding_platform.db')
cursor = conn.cursor()

# Проверяем, есть ли уже задачи
cursor.execute("SELECT COUNT(*) FROM problems")
count = cursor.fetchone()[0]
print(f"Текущее количество задач: {count}")

# Добавляем примеры задач
for problem in SAMPLE_PROBLEMS:
    # Проверяем, существует ли уже задача с таким названием
    cursor.execute("SELECT id FROM problems WHERE title = ?", (problem['title'],))
    existing = cursor.fetchone()
    
    if existing:
        print(f"Задача '{problem['title']}' уже существует, пропускаем")
        continue
    
    print(f"Добавляем задачу: {problem['title']}")
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

# Проверяем новое количество задач
cursor.execute("SELECT COUNT(*) FROM problems")
new_count = cursor.fetchone()[0]
print(f"Новое количество задач: {new_count}")
print(f"Добавлено задач: {new_count - count}")

# Выводим список всех задач
cursor.execute("SELECT id, title, topic, difficulty FROM problems")
problems = cursor.fetchall()
print("\nСписок всех задач:")
for p in problems:
    print(f"ID: {p[0]}, Название: {p[1]}, Тема: {p[2]}, Сложность: {p[3]}")

conn.close()

# Записываем результат в файл
with open('problems_added.txt', 'w', encoding='utf-8') as f:
    f.write(f"Было задач: {count}\n")
    f.write(f"Стало задач: {new_count}\n")
    f.write(f"Добавлено: {new_count - count}\n")
    f.write("\nСписок всех задач:\n")
    for p in problems:
        f.write(f"ID: {p[0]}, Название: {p[1]}, Тема: {p[2]}, Сложность: {p[3]}\n") 