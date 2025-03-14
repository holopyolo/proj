import sqlite3
import os
import sys
from flask import Flask

app = Flask(__name__)
app.config['DATABASE'] = 'coding_platform.db'

def update_database():
    """Обновляет структуру базы данных, добавляя необходимые столбцы"""
    print("Начинаю обновление базы данных...")
    
    # Проверяем, существует ли база данных
    if not os.path.exists(app.config['DATABASE']):
        print(f"Ошибка: база данных {app.config['DATABASE']} не найдена")
        return False
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # Проверяем, есть ли столбец output в таблице solutions
        cursor.execute("PRAGMA table_info(solutions)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Текущие столбцы в таблице solutions: {columns}")
        
        # Добавляем столбец output, если его нет
        if 'output' not in columns:
            print("Добавляю столбец 'output' в таблицу solutions...")
            cursor.execute("ALTER TABLE solutions ADD COLUMN output TEXT")
            conn.commit()
            print("Столбец 'output' успешно добавлен.")
        else:
            print("Столбец 'output' уже существует.")
        
        # Добавляем столбец analysis, если его нет
        if 'analysis' not in columns:
            print("Добавляю столбец 'analysis' в таблицу solutions...")
            cursor.execute("ALTER TABLE solutions ADD COLUMN analysis TEXT")
            conn.commit()
            print("Столбец 'analysis' успешно добавлен.")
        else:
            print("Столбец 'analysis' уже существует.")
        
        # Проверяем, были ли добавлены столбцы
        cursor.execute("PRAGMA table_info(solutions)")
        columns_after = [col[1] for col in cursor.fetchall()]
        print(f"Столбцы в таблице solutions после обновления: {columns_after}")
        
        if 'output' not in columns_after:
            print("ОШИБКА: Столбец 'output' не был добавлен!")
            return False
        
        if 'analysis' not in columns_after:
            print("ОШИБКА: Столбец 'analysis' не был добавлен!")
            return False
        
        # Тестовый запрос
        try:
            cursor.execute("SELECT id, output, analysis FROM solutions LIMIT 1")
            print("Тестовый запрос к таблице solutions выполнен успешно.")
        except sqlite3.OperationalError as e:
            print(f"ОШИБКА при выполнении тестового запроса: {e}")
            return False
        
        print("Обновление базы данных успешно завершено!")
        
        # Выводим информацию о таблице solutions
        cursor.execute("PRAGMA table_info(solutions)")
        columns = cursor.fetchall()
        print("\nТекущая структура таблицы solutions:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Закрываем соединение
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении базы данных: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_database()
    if not success:
        print("Обновление базы данных не выполнено!")
        sys.exit(1)
    else:
        print("Обновление базы данных выполнено успешно!") 