import sqlite3

conn = sqlite3.connect('coding_platform.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM problems')
count = c.fetchone()[0]
print(f"Количество задач в базе данных: {count}")

if count > 0:
    c.execute('SELECT id, title, topic, difficulty FROM problems')
    problems = c.fetchall()
    for p in problems:
        print(f"ID: {p[0]}, Название: {p[1]}, Тема: {p[2]}, Сложность: {p[3]}")

conn.close()

# Записываем результат в файл для проверки
with open('problem_count.txt', 'w') as f:
    f.write(f"Количество задач: {count}\n") 