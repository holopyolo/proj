import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from functools import wraps
# asdas
# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from decorators import teacher_required, admin_required

class TestDecorators(unittest.TestCase):
    
    def test_decorator_structure(self):
        """Проверка, что декораторы корректно структурированы"""
        # Просто проверяем, что декораторы определены как функции
        self.assertTrue(callable(teacher_required))
        self.assertTrue(callable(admin_required))
    
    def test_teacher_required_returns_function(self):
        """Проверка, что teacher_required возвращает функцию"""
        @teacher_required
        def dummy():
            pass
            
        self.assertTrue(callable(dummy))
    
    def test_admin_required_returns_function(self):
        """Проверка, что admin_required возвращает функцию"""
        @admin_required
        def dummy():
            pass
            
        self.assertTrue(callable(dummy))
    
    def test_decorator_preserves_function_name(self):
        """Проверка, что декоратор сохраняет имя функции"""
        @teacher_required
        def my_test_function():
            """Тестовая функция"""
            return "test"
            
        # Проверяем, что имя функции и документация сохраняются
        self.assertEqual(my_test_function.__name__, "my_test_function")
        self.assertEqual(my_test_function.__doc__, "Тестовая функция")

if __name__ == '__main__':
    unittest.main() 