import unittest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

class TestAppBasic(unittest.TestCase):
    
    def setUp(self):
        """Set up a test client"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
    
    def test_app_exists(self):
        """Проверка, что экземпляр Flask-приложения существует"""
        self.assertIsNotNone(app)
    
    def test_app_in_testing_mode(self):
        """Проверка, что приложение находится в режиме тестирования"""
        self.assertTrue(app.config['TESTING'])
    
    def test_about_page(self):
        """Проверка, что страница About доступна"""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
    
    def test_nonexistent_page(self):
        """Проверка, что несуществующая страница возвращает 404"""
        response = self.client.get('/nonexistent_page')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main() 