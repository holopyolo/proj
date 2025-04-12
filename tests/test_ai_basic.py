import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ai_helper

class TestAiBasic(unittest.TestCase):
    
    def test_module_exists(self):
        """Проверка, что модуль ai_helper существует"""
        self.assertIsNotNone(ai_helper)
    
    def test_format_analysis_for_display_with_empty_input(self):
        """Проверка обработки пустого анализа"""
        # Этот тест не требует API, а просто проверяет обработку граничного случая
        # Пустой словарь должен вернуть хотя бы какую-то строку, а не вызывать ошибку
        result = ai_helper.format_analysis_for_display({})
        self.assertIsInstance(result, str)
    
    def test_module_functions_exist(self):
        """Проверка наличия основных функций в модуле"""
        # Проверяем, что основные функции существуют
        self.assertTrue(hasattr(ai_helper, 'analyze_error'))
        self.assertTrue(hasattr(ai_helper, 'format_analysis_for_display'))
    
    @patch('ai_helper.requests')
    def test_proxy_setup(self, mock_requests):
        """Проверка настройки прокси без вызова реального API"""
        # Замокаем метод get, чтобы он не выполнялся реально
        mock_response = MagicMock()
        mock_response.json.return_value = {"ip": "127.0.0.1"}
        mock_requests.get.return_value = mock_response
        
        # Проверяем, что модуль имеет атрибуты для настройки прокси
        if hasattr(ai_helper, 'setup_openai_proxy'):
            # Если функция существует, проверяем что она не вызывает исключений
            try:
                ai_helper.setup_openai_proxy()
                # Тест пройден, если исключений не было
                self.assertTrue(True)  
            except Exception as e:
                # Тест не пройден, если возникло исключение
                self.fail(f"setup_openai_proxy вызвала исключение {str(e)}")

if __name__ == '__main__':
    unittest.main() 