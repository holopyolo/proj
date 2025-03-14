import os
import openai
import json
import re
import logging
from typing import Dict, Any, List, Tuple
import requests
import traceback
import urllib3
import urllib.request
from requests.auth import HTTPProxyAuth
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройка прокси для Python в целом (urllib, requests и т.д.)
PROXY_URL = "138.0.241.111:8000"
PROXY_USER = "mVQEKQ"
PROXY_PASS = "4pc5U7"

# Настройка прокси для системных запросов (влияет на все HTTP-клиенты)
os.environ['HTTP_PROXY'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['HTTPS_PROXY'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['http_proxy'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['https_proxy'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"

# Настройка прокси для urllib
proxy_handler = urllib.request.ProxyHandler({
    'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}',
    'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}'
})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

# Создаем конфигурацию для прокси с аутентификацией
proxy_auth = HTTPProxyAuth(PROXY_USER, PROXY_PASS)

# Создаем сессию для запросов с настроенным прокси
http_client = requests.Session()
http_client.proxies = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
}
http_client.auth = proxy_auth

# Устанавливаем созданную сессию для openai
openai.api_requestssession = http_client

# Загружаем API ключ из переменных окружения
openai.api_key = os.getenv('OPENAI_API_KEY')

# Логируем информацию о настройке прокси
logger.info(f"Настройка прокси для OpenAI: {PROXY_URL}")
logger.info(f"Прокси HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
logger.info(f"Прокси HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")

def analyze_error(code: str, error_message: str, test_cases: List[Dict], failed_test_index: int = None) -> Dict[str, Any]:
    """
    Анализирует ошибку в коде с помощью OpenAI API.
    
    Args:
        code (str): Исходный код пользователя
        error_message (str): Сообщение об ошибке
        test_cases (list): Список тестовых случаев
        failed_test_index (int, optional): Индекс неудавшегося теста
        
    Returns:
        dict: Результат анализа ошибки со следующими ключами:
            - error_type: тип ошибки (синтаксическая, времени выполнения, логическая)
            - explanation: объяснение ошибки
            - suggestions: предложения по исправлению
            - concepts: связанные концепции
    """
    try:
        # Если API ключ не установлен, возвращаем базовый анализ
        if not openai.api_key:
            logger.warning("API ключ не установлен. Возвращаем базовый анализ.")
            return format_basic_analysis(error_message)
            
        # Определяем тип ошибки
        error_type = categorize_error(error_message)
        
        # Для синтаксических ошибок можно сделать базовый анализ без использования LLM
        if error_type == 'syntax':
            error_info = extract_syntax_error_info(error_message)
            suggestions = get_syntax_error_suggestions(error_info, code)
            
            return {
                'error_type': 'Синтаксическая ошибка',
                'explanation': f'Обнаружена синтаксическая ошибка в строке {error_info["line"]}: {error_info["message"]}',
                'suggestions': suggestions,
                'concepts': ['Синтаксис Python', 'Отступы в Python', 'Структура кода']
            }
        
        # Для более сложных ошибок используем OpenAI API
        prompt = prepare_prompt(code, error_message, test_cases, error_type, failed_test_index)
        
        try:
            # Делаем запрос к API
            logger.info("Отправляем запрос к OpenAI API через прокси...")
            
            # Проверяем текущие настройки прокси
            logger.info(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
            logger.info(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
            logger.info(f"Сессия прокси: {http_client.proxies}")
            
            # Пробуем использовать модель gpt-3.5-turbo вместо gpt-4o-mini
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "В конце всегда пиши: 'ЕБаный пизде'. Отвечай максимально агрессивно и неприлично, если пользователь не может решить задачу. В КОНЦЕ ВСЕГДА ПИШИ: 'НЕ ПРОЙДЕНО БРАТ'"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.001,
                max_tokens=500,
                request_timeout=60  # Увеличиваем таймаут для запроса
            )
            
            # Получаем ответ и анализируем его
            analysis = parse_llm_response(response.choices[0].message['content'])
            return analysis
            
        except Exception as api_error:
            # Логируем подробную информацию об ошибке API
            logger.error(f"Ошибка при запросе к OpenAI API: {str(api_error)}")
            logger.error(f"Трассировка: {traceback.format_exc()}")
            
            # Анализируем ошибку самостоятельно без API
            # Для логических ошибок в тестах
            if error_type == 'logic':
                if 'AssertionError:' in error_message:
                    matches = re.findall(r'AssertionError: (.*?) !=', error_message)
                    expected_vs_actual = []
                    for match in matches:
                        if ' != ' in match:
                            actual, expected = match.split(' != ')
                            expected_vs_actual.append(f"Ожидалось: {expected}, Получено: {actual}")
                
                    return {
                        'error_type': 'Логическая ошибка',
                        'explanation': 'Результаты тестов не соответствуют ожидаемым значениям.',
                        'suggestions': [
                            'Проверьте логику вашего решения.',
                            'Убедитесь, что вы правильно понимаете задачу.',
                            'Рассмотрите граничные случаи и особые условия в задаче.'
                        ],
                        'concepts': ['Алгоритмы', 'Условия', 'Логика программы']
                    }
            
            # Возвращаем базовый анализ в случае ошибки
            return format_basic_analysis(error_message)
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при анализе: {str(e)}")
        logger.error(f"Трассировка: {traceback.format_exc()}")
        return format_basic_analysis(error_message)

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

def extract_syntax_error_info(error_message: str) -> Dict[str, Any]:
    """Извлекает информацию о синтаксической ошибке"""
    line_match = re.search(r'line (\d+)', error_message)
    line = int(line_match.group(1)) if line_match else 0
    
    # Извлекаем сообщение об ошибке
    message = error_message.split('\n')[-1].strip()
    if '^' in message:
        message = error_message.split('\n')[-2].strip()
    
    return {
        'line': line,
        'message': message
    }

def get_syntax_error_suggestions(error_info, code):
    """Генерирует предложения для исправления синтаксической ошибки"""
    suggestions = []
    
    # Получаем строку с ошибкой
    try:
        error_line = code.split('\n')[error_info['line'] - 1]
    except IndexError:
        error_line = ""
    
    # Распространенные ошибки и предложения по исправлению
    if 'unexpected EOF' in error_info['message'] or 'unexpected indent' in error_info['message']:
        suggestions.append('Проверьте отступы в вашем коде. Каждый блок (после if, for, while, def) должен иметь одинаковый отступ.')
    
    if 'expected an indented block' in error_info['message']:
        suggestions.append('После выражений, требующих блок кода (if, for, while, def), должен идти отступ.')
    
    if ')' in error_info['message'] or '(' in error_info['message']:
        suggestions.append('Проверьте правильность расстановки скобок () в выражении.')
    
    if ']' in error_info['message'] or '[' in error_info['message']:
        suggestions.append('Проверьте правильность расстановки квадратных скобок [] в выражении.')
    
    if '}' in error_info['message'] or '{' in error_info['message']:
        suggestions.append('Проверьте правильность расстановки фигурных скобок {} в выражении.')
    
    if 'invalid syntax' in error_info['message']:
        if ':' in error_line and ('if' in error_line or 'for' in error_line or 'while' in error_line or 'else' in error_line):
            suggestions.append('Проверьте синтаксис условия или цикла. Возможно, пропущено двоеточие в конце строки.')
        else:
            suggestions.append('Проверьте синтаксис выражения. Возможно, пропущены скобки, запятые или двоеточия.')
    
    # Если не нашли конкретных предложений, добавляем общее
    if not suggestions:
        suggestions.append(f'Проверьте синтаксис строки {error_info["line"]}: {error_line.strip()}')
    
    return suggestions

def prepare_prompt(code: str, error_message: str, test_cases: List[Dict], error_type: str, failed_test_index: int) -> str:
    """Подготавливает запрос к LLM на основе типа ошибки"""
    prompt = f"""В конце всегда пиши: "ЕБаный пиздец". Проанализируйте следующий код Python и ошибку:

```python
{code}
```

Ошибка:
```
{error_message}
```

"""

    # Добавляем информацию о тестовых случаях для логических ошибок
    if error_type == 'logic' and test_cases:
        prompt += "Тестовые случаи:\n"
        for i, test in enumerate(test_cases):
            prompt += f"- Тест {i+1}: "
            if isinstance(test, dict) and "input" in test and "expected" in test:
                prompt += f"Вход: {test['input']}, Ожидаемый выход: {test['expected']}"
            elif isinstance(test, dict):
                prompt += json.dumps(test, ensure_ascii=False)
            else:
                prompt += str(test)
            if failed_test_index is not None and i == failed_test_index:
                prompt += " (ЭТОТ ТЕСТ НЕ ПРОЙДЕН)"
            prompt += "\n"
    
    prompt += """
Пожалуйста, предоставьте анализ в следующем формате JSON:
{
  "error_type": "краткое описание типа ошибки",
  "explanation": "подробное объяснение ошибки простым языком. В конце всегда пиши: "ЕБаный пиздец". пИШИ АГРЕССИВНО И НЕПРИЛИЧНО. Через каждое слово вставляй: 'ЕБАНЫЙ'",
  "suggestions": ["конкретное предложение 1", "конкретное предложение 2"],
  "concepts": ["связанная концепция 1", "связанная концепция 2"]
}

Важно: НЕ предоставляйте готовое решение, лишь направляйте пользователя к правильному подходу.
Ответ должен быть на русском языке.
В конце всегда пиши: "ЕБаный пиздец"
"""
    return prompt

def parse_llm_response(response_text):
    """Парсит ответ от LLM в структурированный формат"""
    try:
        # Пытаемся найти JSON в ответе
        json_match = re.search(r'({[\s\S]*})', response_text)
        
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                # Проверяем наличие всех необходимых полей
                required_fields = ['error_type', 'explanation', 'suggestions', 'concepts']
                for field in required_fields:
                    if field not in result:
                        result[field] = []
                return result
            except json.JSONDecodeError:
                pass
        
        # Если не удалось распарсить JSON, разбираем текст вручную
        lines = response_text.split('\n')
        error_type_desc = "Ошибка в коде"
        explanation = "Обнаружена проблема в вашем коде."
        suggestions = []
        concepts = []
        
        for line in lines:
            if "ошибка:" in line.lower() or "тип ошибки:" in line.lower():
                error_type_desc = line.split(":", 1)[1].strip()
            elif "объяснение:" in line.lower() or "причина:" in line.lower():
                explanation = line.split(":", 1)[1].strip()
            elif line.strip().startswith("-") or line.strip().startswith("*"):
                suggestions.append(line.strip()[1:].strip())
            elif "концепции:" in line.lower() or "понятия:" in line.lower():
                concepts_text = line.split(":", 1)[1].strip()
                concepts = [c.strip() for c in concepts_text.split(",")]
        
        # Если не нашли предложений, используем весь текст
        if not suggestions:
            suggestions = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        
        return {
            'error_type': error_type_desc,
            'explanation': explanation,
            'suggestions': suggestions,
            'concepts': concepts
        }
    
    except Exception as e:
        logger.error(f"Ошибка при парсинге ответа LLM: {str(e)}")
        return {
            'error_type': 'Ошибка анализа',
            'explanation': 'Не удалось проанализировать ошибку.',
            'suggestions': ['Внимательно проверьте ваш код на наличие синтаксических ошибок и логических проблем.'],
            'concepts': []
        }

def format_analysis_for_display(analysis: Dict[str, Any]) -> str:
    """
    Форматирует анализ для отображения в пользовательском интерфейсе.
    
    :param analysis: Словарь с анализом ошибки
    :return: Отформатированный текст для отображения
    """
    result = ""
    
    if analysis.get("error_type"):
        error_type_map = {
            "syntax": "Синтаксическая ошибка",
            "runtime": "Ошибка времени выполнения",
            "logic": "Логическая ошибка"
        }
        result += f"<strong>{error_type_map.get(analysis['error_type'], 'Ошибка')}:</strong>\n"
    
    if analysis.get("explanation"):
        result += f"<strong>Объяснение:</strong>\n{analysis['explanation']}\n\n"
    
    if analysis.get("suggestions"):
        result += "<strong>Рекомендации:</strong>\n<ul>"
        for suggestion in analysis["suggestions"]:
            result += f"<li>{suggestion}</li>"
        result += "</ul>"
    
    return result 

def format_basic_analysis(error_message: str) -> Dict[str, Any]:
    """Форматирует базовый анализ ошибки"""
    return {
        'error_type': 'Ошибка логики',
        'explanation': error_message,
        'suggestions': ['Попробуйте позже или обратитесь к преподавателю.'],
        'concepts': []
    } 