import unittest
import sys
import os
import sqlite3
import tempfile

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, get_db, close_db

class TestDbBasics(unittest.TestCase):
    
    def setUp(self):
        """Создание временной базы данных для тестирования"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        # Инициализируем базу данных
        with app.app_context():
            conn = sqlite3.connect(app.config['DATABASE'])
            # Создадим минимальную схему только для теста
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                );
            ''')
            conn.commit()
            conn.close()
        
    def tearDown(self):
        """Закрытие и удаление временной базы данных"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_get_db(self):
        """Проверка функции get_db"""
        with app.app_context():
            db = get_db()
            # Проверяем, что возвращается объект соединения с базой данных
            self.assertIsNotNone(db)
            # Проверяем, что можно выполнить запрос
            cursor = db.execute('SELECT 1')
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
    
    def test_close_db(self):
        """Проверка функции close_db"""
        with app.app_context():
            db = get_db()
            # Проверяем, что соединение открыто (можем выполнить запрос)
            cursor = db.execute('SELECT 1')
            self.assertEqual(cursor.fetchone()[0], 1)
            
            # Закрываем соединение
            close_db()
            
            # Проверяем, что соединение закрыто
            try:
                db.execute('SELECT 1')
                # Если запрос выполнится, соединение не закрыто - это ошибка
                self.fail("Соединение не было закрыто")
            except sqlite3.ProgrammingError:
                # Если возникла ошибка sqlite3.ProgrammingError, это значит 
                # что соединение было закрыто - тест пройден
                pass

    def test_get_db_reuses_connection(self):
        """Проверка, что get_db повторно использует существующее соединение"""
        with app.app_context():
            db1 = get_db()
            db2 = get_db()
            # В одном контексте должен возвращаться один и тот же объект
            self.assertIs(db1, db2)

if __name__ == '__main__':
    unittest.main() 