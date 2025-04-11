import unittest
import sys
import os

# Добавляем корневую директорию проекта в sys.path для импорта модулей
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def run_tests():
    """Запускает все тесты из директории tests"""
    # Загружаем все тесты из директории tests
    test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    
    # Запускаем тесты
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Выводим результаты
    print(f"\n{'='*50}")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - (len(result.errors) + len(result.failures))}")
    print(f"Ошибок: {len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"{'='*50}")
    
    # Возвращаем код завершения (0 - успех, 1 - ошибка)
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests()) 