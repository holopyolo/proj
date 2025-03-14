import os
import sqlite3

print("Отладочный скрипт запущен!")

# Проверяем существование файлов
db_file = 'coding_platform.db'
db_exists = os.path.exists(db_file)
print(f"Файл базы данных {db_file} существует: {db_exists}")

schema_file = 'schema.sql'
schema_exists = os.path.exists(schema_file)
print(f"Файл схемы {schema_file} существует: {schema_exists}")

# Если базы данных нет, пробуем создать пустую
if not db_exists:
    try:
        print(f"Создаем пустую базу данных {db_file}...")
        conn = sqlite3.connect(db_file)
        print(f"База данных {db_file} успешно создана.")
        
        if schema_exists:
            print(f"Применяем схему из файла {schema_file}...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = f.read()
            conn.executescript(schema)
            print("Схема успешно применена.")
        
        # Вставляем тестовые данные
        print("Вставляем тестовые данные...")
        conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                     ('testuser', 'testhash', 'user'))
        conn.execute("""
            INSERT INTO problems (title, description, topic, difficulty, test_cases, initial_code, created_by) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('Тестовая задача', 'Описание тестовой задачи', 'Тест', 'Легкая', 
             '[{"input": [1, 2], "expected": 3}]', 'def test_func():\n    pass', 1))
        conn.commit()
        print("Тестовые данные успешно добавлены.")
        
        conn.close()
    except Exception as e:
        print(f"Ошибка при работе с базой данных: {str(e)}")
else:
    # Если база данных существует, пробуем выполнить запрос
    try:
        print(f"Подключаемся к существующей базе данных {db_file}...")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print("Запрашиваем количество задач...")
        cursor.execute("SELECT COUNT(*) FROM problems")
        count = cursor.fetchone()[0]
        print(f"Количество задач в базе данных: {count}")
        
        if count > 0:
            print("Список задач:")
            cursor.execute("SELECT id, title, topic, difficulty FROM problems")
            problems = cursor.fetchall()
            for p in problems:
                print(f"ID: {p[0]}, Название: {p[1]}, Тема: {p[2]}, Сложность: {p[3]}")
        
        conn.close()
    except Exception as e:
        print(f"Ошибка при запросе к базе данных: {str(e)}")

print("Отладочный скрипт завершен.") 