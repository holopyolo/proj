import re
import json
import logging
from typing import Dict, Any, List

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_error_locally(code: str, error_message: str, test_cases: List = None) -> Dict[str, Any]:
    """
    Локальный анализатор ошибок (без использования OpenAI API)
    
    Args:
        code: Код пользователя
        error_message: Сообщение об ошибке
        test_cases: Список тестовых случаев (опционально)
        
    Returns:
        dict: Анализ ошибки
    """
    logger.info("Начинаем локальный анализ ошибки")
    
    # Определяем тип ошибки
    error_type = categorize_error(error_message)
    
    # В зависимости от типа ошибки, выполняем разный анализ
    if error_type == 'syntax':
        return analyze_syntax_error(code, error_message)
    elif error_type == 'runtime':
        return analyze_runtime_error(code, error_message)
    elif error_type == 'logic':
        return analyze_logic_error(code, error_message, test_cases)
    else:
        return {
            'error_type': 'Неизвестная ошибка',
            'explanation': error_message,
            'suggestions': ['Внимательно проверьте ваш код на наличие логических ошибок.'],
            'concepts': ['Логика программирования']
        }

def categorize_error(error_message: str) -> str:
    """Определяет тип ошибки на основе сообщения об ошибке"""
    # Синтаксические ошибки
    if any(x in error_message for x in ['SyntaxError', 'IndentationError', 'TabError']):
        return 'syntax'
    
    # Ошибки времени выполнения
    if any(x in error_message for x in ['TypeError', 'ValueError', 'NameError', 'IndexError', 
                                       'KeyError', 'AttributeError', 'ZeroDivisionError']):
        return 'runtime'
    
    # Логические ошибки (когда тесты не проходят)
    if 'AssertionError' in error_message or 'test failed' in error_message.lower():
        return 'logic'
    
    # По умолчанию считаем ошибкой логики
    return 'logic'

def analyze_syntax_error(code: str, error_message: str) -> Dict[str, Any]:
    """Анализирует синтаксическую ошибку"""
    try:
        # Извлекаем информацию о строке и сообщении ошибки
        line_match = re.search(r'line (\d+)', error_message)
        line = int(line_match.group(1)) if line_match else 0
        
        # Извлекаем сообщение об ошибке
        message = error_message.split('\n')[-1].strip()
        if '^' in message:
            message = error_message.split('\n')[-2].strip()
        
        suggestions = []
        
        # Получаем строку с ошибкой, если возможно
        try:
            error_line = code.split('\n')[line - 1]
        except (IndexError, TypeError):
            error_line = ""
            
        # Анализируем распространенные ошибки
        if 'unexpected EOF' in message or 'unexpected indent' in message:
            suggestions.append('Проверьте отступы в вашем коде. Убедитесь, что блоки кода имеют правильные отступы.')
            
        if 'expected an indented block' in message:
            suggestions.append('После выражений if, for, while, def и т.д. должен быть отступ.')
            
        if 'invalid syntax' in message:
            if ':' in error_line and ('if' in error_line or 'for' in error_line or 'while' in error_line):
                suggestions.append('Проверьте синтаксис условия или цикла. Возможно, пропущено двоеточие в конце строки.')
            else:
                suggestions.append('Проверьте синтаксис выражения. Возможно, пропущены запятые, скобки или другие символы.')
                
        if '(' in message or ')' in message:
            suggestions.append('Проверьте правильность расстановки круглых скобок () в выражении.')
            
        if '[' in message or ']' in message:
            suggestions.append('Проверьте правильность расстановки квадратных скобок [] в выражении.')
            
        if '{' in message or '}' in message:
            suggestions.append('Проверьте правильность расстановки фигурных скобок {} в выражении.')
        
        # Если не нашли конкретных предложений, добавляем общее
        if not suggestions:
            suggestions.append(f'Проверьте синтаксис строки {line}: {error_line.strip() if error_line else ""}')
            
        return {
            'error_type': 'Синтаксическая ошибка',
            'explanation': f'В строке {line} обнаружена синтаксическая ошибка: {message}',
            'suggestions': suggestions,
            'concepts': ['Синтаксис Python', 'Правила оформления кода']
        }
    except Exception as e:
        logger.error(f"Ошибка при анализе синтаксической ошибки: {str(e)}")
        return {
            'error_type': 'Синтаксическая ошибка',
            'explanation': 'В коде обнаружена синтаксическая ошибка.',
            'suggestions': ['Внимательно проверьте синтаксис вашего кода.'],
            'concepts': ['Синтаксис Python']
        }

def analyze_runtime_error(code: str, error_message: str) -> Dict[str, Any]:
    """Анализирует ошибку времени выполнения"""
    try:
        # Ищем тип ошибки
        error_type_match = re.search(r'([A-Za-z]+Error)', error_message)
        error_type = error_type_match.group(1) if error_type_match else "Ошибка времени выполнения"
        
        # Ищем строку ошибки
        line_match = re.search(r'line (\d+)', error_message)
        line = int(line_match.group(1)) if line_match else 0
        
        suggestions = []
        explanation = f"Возникла ошибка типа {error_type} при выполнении программы."
        
        # Анализируем различные типы ошибок
        if 'NameError' in error_type:
            name_match = re.search(r"name '(\w+)' is not defined", error_message)
            if name_match:
                var_name = name_match.group(1)
                explanation = f"Переменная или функция '{var_name}' используется, но не определена."
                suggestions = [
                    f"Проверьте, что переменная '{var_name}' определена перед использованием.",
                    "Убедитесь в правильности написания имен переменных и функций (с учетом регистра).",
                    "Если это функция из модуля, проверьте, что модуль импортирован."
                ]
                
        elif 'TypeError' in error_type:
            explanation = "Операция выполняется с несовместимыми типами данных."
            suggestions = [
                "Проверьте типы данных переменных в выражении.",
                "Используйте функции str(), int(), float() для преобразования типов.",
                "Убедитесь, что вы не пытаетесь выполнить операцию между несовместимыми типами."
            ]
            
        elif 'IndexError' in error_type or 'KeyError' in error_type:
            explanation = "Попытка доступа к несуществующему индексу или ключу."
            suggestions = [
                "Проверьте, что индекс не выходит за границы списка или кортежа.",
                "Для словарей убедитесь, что ключ существует, перед доступом к нему.",
                "Используйте условие if key in dict или методы get() для безопасного доступа к словарям.",
                "Для списков проверяйте длину списка перед обращением по индексу."
            ]
            
        elif 'ZeroDivisionError' in error_type:
            explanation = "Попытка деления на ноль."
            suggestions = [
                "Добавьте проверку делителя перед операцией деления.",
                "Используйте конструкцию if divisor != 0: для предотвращения деления на ноль."
            ]
            
        elif 'AttributeError' in error_type:
            attr_match = re.search(r"'[^']+' object has no attribute '(\w+)'", error_message)
            if attr_match:
                attr_name = attr_match.group(1)
                explanation = f"Попытка доступа к несуществующему атрибуту или методу '{attr_name}'."
                suggestions = [
                    f"Проверьте, что объект действительно имеет атрибут или метод '{attr_name}'.",
                    "Убедитесь в правильности написания имени атрибута или метода.",
                    "Проверьте тип объекта перед обращением к его методам."
                ]
            else:
                explanation = "Попытка доступа к несуществующему атрибуту или методу объекта."
                suggestions = [
                    "Проверьте, что объект имеет указанный атрибут или метод.",
                    "Убедитесь в правильности написания имени атрибута или метода."
                ]
                
        # Если мы не нашли конкретных предложений, добавляем общие
        if not suggestions:
            suggestions = [
                "Внимательно прочитайте сообщение об ошибке и найдите указанную строку в вашем коде.",
                "Используйте отладочный вывод (print) для проверки значений переменных.",
                "Проверьте типы данных переменных в выражении."
            ]
            
        return {
            'error_type': error_type,
            'explanation': explanation,
            'suggestions': suggestions,
            'concepts': ['Типы данных Python', 'Обработка ошибок', 'Отладка программ']
        }
    except Exception as e:
        logger.error(f"Ошибка при анализе ошибки времени выполнения: {str(e)}")
        return {
            'error_type': 'Ошибка времени выполнения',
            'explanation': 'При выполнении программы возникла ошибка.',
            'suggestions': ['Внимательно проверьте логику вашего кода и обработку ошибок.'],
            'concepts': ['Отладка программ', 'Обработка исключений']
        }

def analyze_logic_error(code: str, error_message: str, test_cases: List = None) -> Dict[str, Any]:
    """Анализирует логическую ошибку (ошибку в алгоритме)"""
    try:
        suggestions = []
        
        # Ищем несоответствия ожидаемого и фактического результата
        assertion_matches = re.findall(r'AssertionError: (.*?) !=', error_message)
        expected_vs_actual = []
        
        for match in assertion_matches:
            if ' != ' in match:
                actual, expected = match.split(' != ')
                expected_vs_actual.append(f"Ожидалось: {expected}, Получено: {actual}")
        
        if expected_vs_actual:
            expected_vs_actual_str = "\n".join(expected_vs_actual)
            explanation = f"Программа выполняется, но результаты не соответствуют ожидаемым:\n{expected_vs_actual_str}"
        else:
            explanation = "Программа выполняется, но результаты не соответствуют ожидаемым."
            
        # Анализируем особенности ошибки по тестовым случаям
        if 'self.assertEqual' in error_message:
            suggestions.append("Проверьте правильность вычислений в вашей функции.")
            suggestions.append("Убедитесь, что функция возвращает значение правильного типа (int, float, string и т.д.).")
        
        if test_cases:
            suggestions.append("Рассмотрите граничные случаи и особые условия в вашей задаче.")
            suggestions.append("Проверьте логику обработки различных входных данных.")
            
        # Если не нашли конкретных предложений, добавляем общие
        if not suggestions:
            suggestions = [
                "Внимательно прочитайте условие задачи еще раз.",
                "Проверьте логику вашего решения с помощью примеров из условия.",
                "Используйте отладочные выводы (print) для проверки промежуточных результатов."
            ]
            
        return {
            'error_type': 'Логическая ошибка',
            'explanation': explanation,
            'suggestions': suggestions,
            'concepts': ['Алгоритмы', 'Логика программирования', 'Тестирование']
        }
    except Exception as e:
        logger.error(f"Ошибка при анализе логической ошибки: {str(e)}")
        return {
            'error_type': 'Логическая ошибка',
            'explanation': 'Ваша программа не проходит тесты.',
            'suggestions': ['Внимательно проверьте логику вашего кода и требования задачи.'],
            'concepts': ['Алгоритмы', 'Тестирование кода']
        }

def analyze_test_failures(error_message: str) -> Dict[str, Any]:
    """
    Анализирует ошибки в тестах и предлагает рекомендации
    
    Args:
        error_message: Сообщение об ошибке с результатами тестов
        
    Returns:
        dict: Анализ ошибок в тестах
    """
    # Парсим сообщение ошибки
    failures = []
    explanation = "Программа не проходит следующие тесты:\n"
    
    # Извлекаем информацию из AssertionError
    pattern = r'FAIL: (\w+) [\s\S]*?AssertionError: (.*?)$'
    matches = re.findall(pattern, error_message, re.MULTILINE)
    
    for test_name, assert_error in matches:
        failures.append(f"- Тест '{test_name}': {assert_error.strip()}")
    
    if failures:
        explanation += "\n".join(failures)
    else:
        explanation = "Программа не проходит тесты. Проверьте логику вашего решения."
    
    # Формируем базовые рекомендации
    suggestions = [
        "Проверьте логику вашего решения и сравните с требованиями задачи.",
        "Убедитесь, что ваша функция обрабатывает все возможные входные данные.",
        "Проверьте граничные условия (пустые списки, нули, отрицательные числа и т.д.).",
        "Используйте отладочный вывод (print) для проверки промежуточных результатов."
    ]
    
    # Добавляем специфичные рекомендации на основе ошибок
    if any(" != " in failure for failure in failures):
        suggestions.append("Ваша функция возвращает неправильные значения для некоторых тестов.")
    
    # Проверяем конкретные ошибки и даем специфичные рекомендации
    if any("2 != 0" in failure for failure in failures) or any("3 != 0" in failure for failure in failures):
        suggestions = [
            "Ваша функция возвращает само число (2 или 3), когда должна возвращать 0.",
            "Возможно, вам нужно добавить специальное условие для обработки этих случаев.",
            "Проверьте условие задачи на наличие требований по возврату 0 в определенных ситуациях.",
            "Рассмотрите различные случаи, когда функция должна возвращать 0 вместо входного значения."
        ]
    
    if any("5.5 != 6.0" in failure for failure in failures):
        suggestions = [
            "Ваша функция возвращает 5.5, когда должна возвращать 6.0.",
            "Проверьте правильность математических расчетов в вашей функции.",
            "Возможно, вам нужно округлять результат до ближайшего целого числа (round() или math.ceil()).",
            "Убедитесь, что вы используете правильные математические операции (умножение вместо деления)."
        ]
    
    return {
        'error_type': 'Ошибка в тестах',
        'explanation': explanation,
        'suggestions': suggestions,
        'concepts': ['Тестирование', 'Логика программирования', 'Отладка']
    }

def format_analysis_for_display(analysis: Dict[str, Any]) -> str:
    """
    Форматирует анализ для отображения в пользовательском интерфейсе
    
    Args:
        analysis: Словарь с анализом ошибки
        
    Returns:
        str: Отформатированный HTML-текст для отображения
    """
    result = ""
    
    if analysis.get("error_type"):
        result += f"<strong>{analysis['error_type']}:</strong>\n"
    
    if analysis.get("explanation"):
        result += f"<strong>Объяснение:</strong>\n{analysis['explanation']}\n\n"
    
    if analysis.get("suggestions"):
        result += "<strong>Рекомендации:</strong>\n<ul>"
        for suggestion in analysis["suggestions"]:
            result += f"<li>{suggestion}</li>"
        result += "</ul>"
    
    if analysis.get("concepts"):
        result += "<strong>Связанные концепции:</strong>\n<ul>"
        for concept in analysis["concepts"]:
            result += f"<li>{concept}</li>"
        result += "</ul>"
    
    return result

# Пример использования
if __name__ == "__main__":
    # Пример с логической ошибкой в тестах
    test_error = """.FFF ====================================================================== FAIL: test_case_2 (__main__.TestSolution.test_case_2) ---------------------------------------------------------------------- Traceback (most recent call last): File "C:\\Users\\ctoow\\AppData\\Local\\Temp\\tmp3t3f7vae.py", line 19, in test_case_2 self.assertEqual(result, 0) ~~~~~~~~~~~~~~~~^^^^^^^^^^^ AssertionError: 2 != 0 ====================================================================== FAIL: test_case_3 (__main__.TestSolution.test_case_3) ---------------------------------------------------------------------- Traceback (most recent call last): File "C:\\Users\\ctoow\\AppData\\Local\\Temp\\tmp3t3f7vae.py", line 23, in test_case_3 self.assertEqual(result, 0) ~~~~~~~~~~~~~~~~^^^^^^^^^^^ AssertionError: 3 != 0 ====================================================================== FAIL: test_case_4 (__main__.TestSolution.test_case_4) ---------------------------------------------------------------------- Traceback (most recent call last): File "C:\\Users\\ctoow\\AppData\\Local\\Temp\\tmp3t3f7vae.py", line 27, in test_case_4 self.assertEqual(result, 6.0) ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^ AssertionError: 5.5 != 6.0 ---------------------------------------------------------------------- Ran 4 tests in 0.003s FAILED (failures=3)"""
    
    analysis = analyze_test_failures(test_error)
    formatted = format_analysis_for_display(analysis)
    
    print(formatted)
    
    # Сохраняем результат в файл
    with open("local_analysis_result.txt", "w", encoding="utf-8") as f:
        f.write("Результат анализа ошибки:\n\n")
        f.write(json.dumps(analysis, ensure_ascii=False, indent=2))
        f.write("\n\nОтформатированный результат:\n\n")
        f.write(formatted) 