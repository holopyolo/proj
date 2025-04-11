import subprocess
import tempfile
import os
import json
import re
from typing import Dict, Any, List, Optional
from ai_helper import analyze_error, format_analysis_for_display
from datetime import datetime, timedelta
import ai_helper
import traceback
from flask import Markup
import logging
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Импортируем модули анализа ошибок
try:
    from local_error_analyzer import analyze_test_failures, analyze_error_locally, format_analysis_for_display as local_format
    OPENAI_AVAILABLE = True
except ImportError as e:
    OPENAI_AVAILABLE = False
    logging.error(f"Ошибка импорта модулей анализа ошибок: {str(e)}")

def run_code(code: str, test_cases: List[Dict] = None) -> Dict[str, Any]:
    """
    Запускает код пользователя и выполняет тесты, если они предоставлены.
    
    Args:
        code (str): Исходный код пользователя
        test_cases (list, optional): Список тестовых случаев
        
    Returns:
        dict: Результат с ключами success, output, error и др.
    """
    # Инициализируем результат
    result = {
        'success': False,
        'output': '',
        'error': None
    }
    
    # Определяем команду для запуска Python
    python_cmd = determine_python_command()
    if not python_cmd:
        result['error'] = 'Не удалось найти интерпретатор Python на сервере. Обратитесь к администратору.'
        return result
    
    # Сохраняем код во временный файл
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as tmp_file:
        tmp_file.write(code)
        code_path = tmp_file.name
    
    try:
        # Если тесты не предоставлены, просто запускаем код
        if not test_cases:
            proc = subprocess.run(
                [python_cmd, code_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            result['output'] = proc.stdout
            
            if proc.returncode != 0:
                result['error'] = proc.stderr
            else:
                result['success'] = True
        else:
            # Генерируем код для тестирования
            test_code = generate_test_code(code, test_cases)
            
            # Создаем временный файл для тестов
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as test_file:
                test_file.write(test_code)
                test_path = test_file.name
            
            try:
                # Запускаем тесты
                proc = subprocess.run(
                    [python_cmd, test_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Сохраняем результаты
                result['output'] = proc.stdout
                
                if proc.returncode != 0:
                    result['error'] = proc.stderr
                else:
                    result['success'] = True
            finally:
                # Удаляем временный файл с тестами
                if os.path.exists(test_path):
                    os.unlink(test_path)
    except subprocess.TimeoutExpired:
        result['error'] = 'Превышено время выполнения (10 секунд). Возможно, в вашем коде есть бесконечный цикл.'
    except Exception as e:
        result['error'] = f'Произошла ошибка при выполнении кода: {str(e)}'
        logger.error(f"Ошибка при выполнении кода: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # Удаляем временный файл с кодом
        if os.path.exists(code_path):
            os.unlink(code_path)
    
    return result

def determine_python_command() -> str:
    """
    Определяет доступную команду интерпретатора Python в системе.
    
    Returns:
        str: Команда для запуска Python или None, если интерпретатор не найден
    """
    # Список возможных команд для запуска Python
    possible_commands = ['python3', 'python', 'py', sys.executable]
    
    for cmd in possible_commands:
        try:
            # Проверяем, доступна ли команда
            subprocess.run([cmd, '--version'], capture_output=True, text=True)
            return cmd
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    # Если ни одна команда не сработала, возвращаем путь к текущему интерпретатору
    return sys.executable if os.path.exists(sys.executable) else None

def find_failed_test_index(error_message: str) -> Optional[int]:
    """
    Извлекает индекс неудавшегося теста из сообщения об ошибке.
    
    Args:
        error_message (str): Сообщение об ошибке
        
    Returns:
        int/None: Индекс неудавшегося теста или None, если не удалось определить
    """
    # Ищем сообщения вида "FAIL: test_case_1 (test_solution.TestSolution)"
    match = re.search(r'FAIL: test_case_(\d+)', error_message)
    if match:
        return int(match.group(1)) - 1  # Индексы с нуля
    
    return None

def generate_test_code(code: str, test_cases: List[Dict]) -> str:
    """
    Генерирует код для тестирования на основе пользовательского кода и тестовых случаев.
    
    Args:
        code (str): Исходный код пользователя
        test_cases (list): Список тестовых случаев
        
    Returns:
        str: Сгенерированный тестовый код
    """
    # Начало тестового кода
    test_code = code + "\n\n"
    test_code += "import unittest\n"
    test_code += "import sys\n\n"
    test_code += "class TestSolution(unittest.TestCase):\n"
    
    # Добавляем тест-кейсы
    for i, test_case in enumerate(test_cases):
        test_code += f"    def test_case_{i+1}(self):\n"
        
        # Различные форматы тестовых случаев
        if isinstance(test_case, dict) and 'input' in test_case and 'expected' in test_case:
            # Извлекаем имя функции из кода пользователя
            func_match = re.search(r'def\s+(\w+)\s*\(', code)
            func_name = func_match.group(1) if func_match else "solution"
            
            # Форматируем входные данные в зависимости от их типа
            if isinstance(test_case['input'], list):
                input_str = ', '.join(repr(x) for x in test_case['input'])
                test_code += f"        result = {func_name}({input_str})\n"
            else:
                test_code += f"        result = {func_name}({repr(test_case['input'])})\n"
            
            test_code += f"        self.assertEqual(result, {repr(test_case['expected'])})\n\n"
    
    # Код для запуска тестов
    test_code += "if __name__ == '__main__':\n"
    test_code += "    unittest.main()\n"
    
    return test_code

def validate_test_cases(test_cases: List[Dict]) -> bool:
    """
    Проверяет правильность формата тестовых случаев.
    
    Args:
        test_cases (list): Список тестовых случаев
        
    Returns:
        bool: Валидны ли тесты
    """
    if not test_cases or not isinstance(test_cases, list):
        return False
        
    try:
        for test in test_cases:
            if not isinstance(test, dict) or not all(key in test for key in ['input', 'output', 'description']):
                return False
        return True
    except:
        return False

def analyze_error_with_llm(code: str, error: str, test_cases: List[Dict] = None, failed_test_index: int = None) -> str:
    """
    Анализирует ошибку с помощью модели машинного обучения и форматирует результат для отображения.
    
    Args:
        code (str): Исходный код пользователя
        error (str): Сообщение об ошибке
        test_cases (list, optional): Список тестовых случаев
        failed_test_index (int, optional): Индекс неудавшегося теста
        
    Returns:
        str: Отформатированный HTML-анализ ошибки
    """
    try:
        if test_cases is None:
            test_cases = []
            
        # Находим первый неудачный тест
        failed_test_index = None
        if 'FAIL: test_case_' in error:
            match = re.search(r'FAIL: test_case_(\d+)', error)
            if match:
                failed_test_index = int(match.group(1)) - 1
        
        # Проверяем доступность OpenAI
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                # Пробуем использовать OpenAI
                logger.info("Пытаемся использовать OpenAI API для анализа ошибки...")
                analysis = ai_helper.analyze_error(code, error, test_cases, failed_test_index)
                formatted_analysis = ai_helper.format_analysis_for_display(analysis)
                logger.info("Анализ ошибки с помощью OpenAI API успешно выполнен")
                return Markup(formatted_analysis)
            except Exception as api_err:
                # Если OpenAI недоступен, используем локальный анализатор
                logger.error(f"Ошибка при использовании OpenAI API: {str(api_err)}")
                logger.info("Переключаемся на локальный анализатор...")
        
        # Использование локального анализатора
        logger.info("Используем локальный анализатор ошибок...")
        if 'self.assertEqual' in error and 'AssertionError' in error:
            analysis = analyze_test_failures(error)
        else:
            analysis = analyze_error_locally(code, error, test_cases)
            
        formatted_analysis = local_format(analysis)
        logger.info("Локальный анализ ошибки успешно выполнен")
        return Markup(formatted_analysis)
        
    except Exception as e:
        logger.error(f"Ошибка при анализе ошибки: {str(e)}")
        logger.error(traceback.format_exc())
        # Возвращаем базовое сообщение об ошибке
        return Markup(f"<strong>Ошибка при анализе:</strong><br>{error}")

def format_datetime(dt):
    """
    Форматирует дату и время в удобочитаемый вид.
    """
    if not dt:
        return ""
    
    now = datetime.now()
    today = now.date()
    dt_date = dt.date() if hasattr(dt, 'date') else dt.date
    
    if dt_date == today:
        return f"Сегодня в {dt.strftime('%H:%M')}"
    elif dt_date == today - timedelta(days=1):
        return f"Вчера в {dt.strftime('%H:%M')}"
    else:
        return dt.strftime('%d.%m.%Y %H:%M') 