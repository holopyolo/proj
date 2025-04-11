import unittest
import sys
import os
import tempfile
from datetime import datetime, timedelta

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import run_code, generate_test_code, find_failed_test_index, format_datetime, determine_python_command, validate_test_cases

class TestUtils(unittest.TestCase):
    """Тесты для функций в модуле utils.py"""
    
    def test_format_datetime(self):
        """Тест функции format_datetime"""
        # Тестируем форматирование текущей даты
        now = datetime.now()
        formatted = format_datetime(now)
        self.assertIsInstance(formatted, str)
        
        # Тестируем форматирование вчерашней даты
        yesterday = datetime.now() - timedelta(days=1)
        formatted_yesterday = format_datetime(yesterday)
        self.assertIn("вчера", formatted_yesterday.lower())
        
        # Тестируем форматирование даты недельной давности
        week_ago = datetime.now() - timedelta(days=7)
        formatted_week_ago = format_datetime(week_ago)
        self.assertIsInstance(formatted_week_ago, str)
    
    def test_determine_python_command(self):
        """Тест функции determine_python_command"""
        # Проверяем, что функция возвращает строку с командой
        command = determine_python_command()
        self.assertIsInstance(command, str)
        self.assertIsNotNone(command)
        
        # Проверяем, что команда работает
        import subprocess
        try:
            result = subprocess.run([command, "--version"], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0)
            self.assertIn("Python", result.stdout + result.stderr)
        except Exception as e:
            self.fail(f"Команда {command} не работает: {str(e)}")
    
    def test_validate_test_cases(self):
        """Тест функции validate_test_cases"""
        # Валидные тестовые случаи
        valid_test_cases = [
            {'input': '5', 'expected': '10'},
            {'input': '0', 'expected': '0'}
        ]
        
        # Невалидные тестовые случаи (отсутствует ключ 'input')
        invalid_test_cases = [
            {'expected': '10'},
            {'inp': '5', 'expected': '0'}
        ]
        
        # Проверяем валидные тестовые случаи
        result = validate_test_cases(valid_test_cases)
        self.assertTrue(result)
        
        # Проверяем невалидные тестовые случаи
        result = validate_test_cases(invalid_test_cases)
        self.assertFalse(result)
    
    def test_find_failed_test_index(self):
        """Тест функции find_failed_test_index"""
        # Сообщение с ошибкой, содержащее информацию о неудачном тесте
        error_message = """======================================================================
FAIL: test_case_3 (test_solution.TestSolution)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/tmp/tmpfile.py", line 20, in test_case_3
    self.assertEqual(result, -1)
AssertionError: 1 != -1
"""
        
        # Проверяем, что функция правильно находит индекс неудачного теста
        index = find_failed_test_index(error_message)
        self.assertEqual(index, 2)  # индекс 2 соответствует test_case_3 (с нуля)
        
        # Проверяем случай, когда нет информации о неудачном тесте
        empty_error_message = "Some error occurred but no test case info"
        index = find_failed_test_index(empty_error_message)
        self.assertIsNone(index)
    
    def test_generate_test_code(self):
        """Тест функции generate_test_code"""
        # Пример кода пользователя
        user_code = """def multiply(a, b):
    return a * b
"""
        
        # Тестовые случаи
        test_cases = [
            {'input': '2, 3', 'expected': '6'},
            {'input': '0, 5', 'expected': '0'}
        ]
        
        # Генерируем тестовый код
        test_code = generate_test_code(user_code, test_cases)
        
        # Проверяем, что сгенерированный код содержит нужные компоненты
        self.assertIn("import unittest", test_code)
        self.assertIn("class TestSolution(unittest.TestCase):", test_code)
        self.assertIn("def test_case_1(self):", test_code)
        self.assertIn("def test_case_2(self):", test_code)
        self.assertIn("unittest.main()", test_code)
    
    def test_run_code_basic(self):
        """Тест функции run_code для простого кода без тестов"""
        # Простой код, который выводит сообщение
        simple_code = 'print("Hello, world!")'
        
        # Запускаем код
        result = run_code(simple_code)
        
        # Проверяем результаты
        self.assertTrue('success' in result)
        self.assertTrue('output' in result)
        self.assertEqual(result['output'].strip(), "Hello, world!")
        self.assertIsNone(result['error'])
    
    def test_run_code_with_error(self):
        """Тест функции run_code с кодом, содержащим ошибку"""
        # Код с синтаксической ошибкой
        error_code = 'print("Missing closing parenthesis"'
        
        # Запускаем код
        result = run_code(error_code)
        
        # Проверяем результаты
        self.assertFalse(result['success'])
        self.assertTrue('error' in result)
        self.assertIsNotNone(result['error'])
    
    def test_run_code_with_tests(self):
        """Тест функции run_code с тестами"""
        # Код функции
        code = """def add(a, b):
    return a + b
"""
        
        # Тестовые случаи
        test_cases = [
            {'input': '2, 3', 'expected': '5'},
            {'input': '0, 0', 'expected': '0'}
        ]
        
        # Запускаем код с тестами
        result = run_code(code, test_cases)
        
        # Проверяем результаты
        self.assertTrue(result['success'])
        self.assertIsNone(result['error'])

if __name__ == '__main__':
    unittest.main() 