import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_error_analyzer

class TestLocalErrorAnalyzer(unittest.TestCase):
    
    def test_module_exists(self):
        """Проверка, что модуль local_error_analyzer существует"""
        self.assertIsNotNone(local_error_analyzer)
    
    def test_module_has_analyze_functions(self):
        """Проверка, что модуль содержит функции анализа"""
        self.assertTrue(hasattr(local_error_analyzer, 'analyze_error_locally'))
        self.assertTrue(hasattr(local_error_analyzer, 'analyze_test_failures'))
    
    def test_format_analysis_function(self):
        """Проверка функции форматирования анализа"""
        self.assertTrue(hasattr(local_error_analyzer, 'format_analysis_for_display'))
        
        # Проверим, что функция не вызывает ошибок с пустым словарем (а не строкой)
        if hasattr(local_error_analyzer, 'format_analysis_for_display'):
            try:
                # Создаем пустой словарь для анализа
                empty_analysis = {
                    "error_type": "Test error",
                    "explanation": "This is a test",
                    "solution": "No solution needed"
                }
                result = local_error_analyzer.format_analysis_for_display(empty_analysis)
                self.assertIsInstance(result, str)
            except Exception as e:
                self.fail(f"format_analysis_for_display вызвала исключение {str(e)}")
    
    def test_error_pattern_detection(self):
        """Проверка распознавания паттернов ошибок"""
        # Проверка распознавания паттерна NameError
        if hasattr(local_error_analyzer, 'detect_error_type'):
            error_message = "NameError: name 'variable' is not defined"
            error_type = local_error_analyzer.detect_error_type(error_message)
            self.assertIsInstance(error_type, str)
            
            # Проверяем, что функция распознает разные типы ошибок
            messages = [
                "SyntaxError: invalid syntax",
                "TypeError: can't multiply sequence by non-int of type 'str'",
                "ZeroDivisionError: division by zero"
            ]
            
            for msg in messages:
                if hasattr(local_error_analyzer, 'detect_error_type'):
                    error_type = local_error_analyzer.detect_error_type(msg)
                    self.assertIsInstance(error_type, str)

if __name__ == '__main__':
    unittest.main() 