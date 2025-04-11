import unittest
import sys
import os
import re

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_error_analyzer import (
    analyze_error_locally, 
    categorize_error,
    analyze_syntax_error,
    analyze_runtime_error,
    analyze_logic_error,
    analyze_test_failures,
    format_analysis_for_display
)

class TestErrorAnalyzer(unittest.TestCase):
    """Тесты для функций в модуле local_error_analyzer.py"""
    
    def test_categorize_error(self):
        """Тест функции categorize_error"""
        # Синтаксические ошибки
        syntax_error = "  File 'test.py', line 5\n    if x == 1\n            ^\nSyntaxError: invalid syntax"
        self.assertEqual(categorize_error(syntax_error), 'syntax')
        
        # Ошибки времени выполнения
        runtime_error = "Traceback (most recent call last):\n  File 'test.py', line 3, in <module>\n    print(1/0)\nZeroDivisionError: division by zero"
        self.assertEqual(categorize_error(runtime_error), 'runtime')
        
        # Логические ошибки
        logic_error = "AssertionError: 5 != 10"
        self.assertEqual(categorize_error(logic_error), 'logic')
        
        # Неизвестные ошибки должны считаться логическими
        unknown_error = "Some unknown error occurred"
        self.assertEqual(categorize_error(unknown_error), 'logic')

    def test_analyze_syntax_error(self):
        """Тест функции analyze_syntax_error"""
        # Код с синтаксической ошибкой
        code = """def test_function():
    if x == 1
        print("x is one")
"""
        
        # Сообщение об ошибке
        error_message = """  File "test.py", line 2
    if x == 1
            ^
SyntaxError: invalid syntax"""
        
        # Анализируем ошибку
        result = analyze_syntax_error(code, error_message)
        
        # Проверяем результаты
        self.assertEqual(result['error_type'], 'Синтаксическая ошибка')
        self.assertIn('объяснение', result.keys(), case_fold=True)  # 'explanation' или 'Объяснение'
        self.assertIn('suggestions', result.keys(), case_fold=True)  # 'suggestions' или 'Рекомендации'
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreater(len(result['suggestions']), 0)

    def test_analyze_runtime_error(self):
        """Тест функции analyze_runtime_error"""
        # Код с ошибкой времени выполнения
        code = """def test_function():
    x = 5
    y = 0
    return x / y
"""
        
        # Сообщение об ошибке
        error_message = """Traceback (most recent call last):
  File "test.py", line 4, in test_function
    return x / y
ZeroDivisionError: division by zero"""
        
        # Анализируем ошибку
        result = analyze_runtime_error(code, error_message)
        
        # Проверяем результаты
        self.assertIn('ZeroDivisionError', result['error_type'])
        self.assertIn('объяснение', result.keys(), case_fold=True)
        self.assertIn('suggestions', result.keys(), case_fold=True)
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreater(len(result['suggestions']), 0)

    def test_analyze_logic_error(self):
        """Тест функции analyze_logic_error"""
        # Код с логической ошибкой
        code = """def add(a, b):
    return a - b  # Ошибка: вычитание вместо сложения
"""
        
        # Сообщение об ошибке
        error_message = """AssertionError: 0 != 5"""
        
        # Анализируем ошибку
        result = analyze_logic_error(code, error_message)
        
        # Проверяем результаты
        self.assertEqual(result['error_type'], 'Логическая ошибка')
        self.assertIn('объяснение', result.keys(), case_fold=True)
        self.assertIn('suggestions', result.keys(), case_fold=True)
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreater(len(result['suggestions']), 0)

    def test_analyze_test_failures(self):
        """Тест функции analyze_test_failures"""
        # Сообщение об ошибке в тестах
        error_message = """FFFF ====================================================================== 
FAIL: test_case_1 (__main__.TestSolution) 
---------------------------------------------------------------------- 
Traceback (most recent call last): 
  File "/tmp/tmpbkhpbvvj.py", line 12, in test_case_1 
    self.assertEqual(result, 9) 
AssertionError: 7 != 9 
====================================================================== 
FAIL: test_case_2 (__main__.TestSolution) 
---------------------------------------------------------------------- 
Traceback (most recent call last): 
  File "/tmp/tmpbkhpbvvj.py", line 16, in test_case_2 
    self.assertEqual(result, 5) 
AssertionError: 7 != 5"""
        
        # Анализируем ошибку
        result = analyze_test_failures(error_message)
        
        # Проверяем результаты
        self.assertEqual(result['error_type'], 'Ошибка в тестах')
        self.assertIn('объяснение', result.keys(), case_fold=True)
        self.assertIn('suggestions', result.keys(), case_fold=True)
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreater(len(result['suggestions']), 0)
        
        # Проверяем, что анализатор распознает паттерн "одинаковое значение для разных тестов"
        self.assertTrue(any("7" in s for s in result['suggestions']))

    def test_format_analysis_for_display(self):
        """Тест функции format_analysis_for_display"""
        # Создаем тестовый анализ
        analysis = {
            'error_type': 'Тестовая ошибка',
            'explanation': 'Объяснение тестовой ошибки',
            'suggestions': ['Рекомендация 1', 'Рекомендация 2'],
            'concepts': ['Концепция 1', 'Концепция 2']
        }
        
        # Форматируем анализ
        formatted = format_analysis_for_display(analysis)
        
        # Проверяем результаты
        self.assertIsInstance(formatted, str)
        self.assertIn('Тестовая ошибка', formatted)
        self.assertIn('Объяснение', formatted)
        self.assertIn('Рекомендации', formatted)
        self.assertIn('Рекомендация 1', formatted)
        self.assertIn('Рекомендация 2', formatted)
        self.assertIn('Концепция 1', formatted)
        self.assertIn('Концепция 2', formatted)
        
    def test_analyze_error_locally(self):
        """Тест функции analyze_error_locally"""
        # Код с синтаксической ошибкой
        code = """def test_function()
    print("Hello, world!")
"""
        
        # Сообщение об ошибке
        error_message = """  File "test.py", line 1
    def test_function()
                      ^
SyntaxError: expected ':'"""
        
        # Анализируем ошибку
        result = analyze_error_locally(code, error_message)
        
        # Проверяем результаты
        self.assertEqual(result['error_type'], 'Синтаксическая ошибка')
        self.assertIn('объяснение', result.keys(), case_fold=True)
        self.assertIn('suggestions', result.keys(), case_fold=True)
        self.assertIsInstance(result['suggestions'], list)

if __name__ == '__main__':
    unittest.main() 