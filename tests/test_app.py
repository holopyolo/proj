import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app
from app import get_db

class TestApp(unittest.TestCase):
    """Тесты для Flask-приложения"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем временную базу данных для тестов
        self.db_fd, flask_app.app.config['DATABASE'] = tempfile.mkstemp()
        flask_app.app.config['TESTING'] = True
        self.app = flask_app.app.test_client()
        
        # Инициализируем базу данных
        with flask_app.app.app_context():
            flask_app.init_db()
            
            # Добавляем тестового пользователя
            db = get_db()
            db.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                ('testuser', 'test@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'user')
            )
            
            # Добавляем тестовую задачу
            db.execute(
                'INSERT INTO problems (title, description, topic, difficulty, test_cases, initial_code) VALUES (?, ?, ?, ?, ?, ?)',
                ('Test Problem', 
                 'Write a function that adds two numbers', 
                 'Basics', 
                 'Easy', 
                 json.dumps([{'input': '2, 3', 'expected': '5'}, {'input': '0, 0', 'expected': '0'}]),
                 'def add(a, b):\n    # Write your code here\n    pass')
            )
            db.commit()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        os.close(self.db_fd)
        os.unlink(flask_app.app.config['DATABASE'])

    def test_index(self):
        """Тест главной страницы"""
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('Coding Platform', data)

    def test_login_page(self):
        """Тест страницы входа"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('Login', data)
        self.assertIn('form', data.lower())
        self.assertIn('username', data.lower())
        self.assertIn('password', data.lower())

    def test_login_functionality(self):
        """Тест функциональности входа"""
        # Успешный вход
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': '123456'  # Соответствует хешу, добавленному в setUp
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        
        # Неправильный пароль
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Неправильное имя пользователя или пароль', data)

    def test_register_page(self):
        """Тест страницы регистрации"""
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('Register', data)
        self.assertIn('form', data.lower())
        self.assertIn('username', data.lower())
        self.assertIn('password', data.lower())
        self.assertIn('confirm_password', data.lower())

    def test_register_functionality(self):
        """Тест функциональности регистрации"""
        # Успешная регистрация
        response = self.app.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что пользователь добавлен в базу данных
        with flask_app.app.app_context():
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ?', ('newuser',)).fetchone()
            self.assertIsNotNone(user)
            self.assertEqual(user['email'], 'new@example.com')

    def test_problems_page(self):
        """Тест страницы с задачами"""
        response = self.app.get('/problems')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('Test Problem', data)
        self.assertIn('Basics', data)
        self.assertIn('Easy', data)

    def test_problem_detail_page(self):
        """Тест страницы с деталями задачи"""
        # Получаем ID тестовой задачи
        with flask_app.app.app_context():
            db = get_db()
            problem_id = db.execute('SELECT id FROM problems').fetchone()['id']
        
        response = self.app.get(f'/problem/{problem_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('Test Problem', data)
        self.assertIn('Write a function', data)
        self.assertIn('def add', data)

    @patch('app.run_code')
    def test_run_code_endpoint(self, mock_run_code):
        """Тест эндпоинта для запуска кода"""
        # Мокаем функцию run_code
        mock_run_code.return_value = {
            'success': True,
            'output': 'Hello, world!',
            'error': None
        }
        
        # Выполняем запрос
        response = self.app.post('/run_code', json={
            'code': 'print("Hello, world!")'
        })
        
        # Проверяем ответ
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertEqual(data['output'], 'Hello, world!')
        self.assertIsNone(data['error'])
        
        # Проверяем, что функция run_code была вызвана с правильными аргументами
        mock_run_code.assert_called_once_with('print("Hello, world!")', None)

    @patch('app.run_code')
    def test_submit_solution(self, mock_run_code):
        """Тест отправки решения"""
        # Требуется аутентификация, поэтому сначала входим
        self.app.post('/login', data={
            'username': 'testuser',
            'password': '123456'
        }, follow_redirects=True)
        
        # Получаем ID тестовой задачи
        with flask_app.app.app_context():
            db = get_db()
            problem_id = db.execute('SELECT id FROM problems').fetchone()['id']
        
        # Мокаем функцию run_code
        mock_run_code.return_value = {
            'success': True,
            'output': 'Tests passed',
            'error': None
        }
        
        # Отправляем решение
        response = self.app.post(f'/submit_solution/{problem_id}', json={
            'code': 'def add(a, b):\n    return a + b'
        }, follow_redirects=True)
        
        # Проверяем ответ
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])
        
        # Проверяем, что решение было сохранено в базе данных
        with flask_app.app.app_context():
            db = get_db()
            solution = db.execute('SELECT * FROM solutions WHERE problem_id = ?', (problem_id,)).fetchone()
            self.assertIsNotNone(solution)
            self.assertEqual(solution['code'], 'def add(a, b):\n    return a + b')
            self.assertEqual(solution['status'], 'success')

if __name__ == '__main__':
    unittest.main() 