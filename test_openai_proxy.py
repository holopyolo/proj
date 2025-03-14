import os
import sys
import openai
import json
import requests
import logging
import urllib.request
from requests.auth import HTTPProxyAuth
import traceback

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройка прокси для Python в целом
PROXY_URL = "138.0.241.111:8000"
PROXY_USER = "mVQEKQ"
PROXY_PASS = "4pc5U7"

# Настройка прокси для системных запросов (влияет на все HTTP-клиенты)
os.environ['HTTP_PROXY'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['HTTPS_PROXY'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['http_proxy'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['https_proxy'] = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

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
if not openai.api_key:
    logger.error("API ключ не найден. Проверьте переменную OPENAI_API_KEY.")
    exit(1)

# Логируем информацию о настройке прокси
logger.info(f"Настройка прокси для OpenAI: {PROXY_URL}")
logger.info(f"Прокси HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
logger.info(f"Прокси HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
logger.info(f"Сессия прокси: {http_client.proxies}")

# Сначала проверим соединение с прокси
try:
    logger.info("Проверка соединения с прокси-сервером...")
    proxy_test = requests.get('https://httpbin.org/ip', proxies=http_client.proxies, timeout=10)
    logger.info(f"Ответ от proxy-сервера: {proxy_test.json()}")
    logger.info(f"Заголовки ответа: {proxy_test.headers}")
    
    with open("proxy_connection_test.txt", "w", encoding="utf-8") as f:
        f.write(f"Статус: {proxy_test.status_code}\n")
        f.write(f"IP через прокси: {proxy_test.json()}\n")
        f.write(f"Заголовки: {json.dumps(dict(proxy_test.headers), indent=2)}\n")
    
    logger.info("Соединение с прокси-сервером установлено успешно")
except Exception as e:
    logger.error(f"Ошибка при проверке соединения с прокси: {str(e)}")
    with open("proxy_connection_error.txt", "w", encoding="utf-8") as f:
        f.write(f"Ошибка при проверке соединения с прокси: {str(e)}\n")
        f.write(f"Трассировка: {traceback.format_exc()}\n")

# Теперь тестируем OpenAI
try:
    logger.info("Тестирование подключения к OpenAI API через прокси...")
    
    # Пробуем две разные модели
    for model in ["gpt-3.5-turbo", "text-davinci-003"]:
        try:
            logger.info(f"Тестирование модели: {model}")
            
            if model == "gpt-3.5-turbo":
                # Простой запрос к API для проверки подключения (чат-модель)
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Вы - помощник для тестирования."},
                        {"role": "user", "content": "Привет! Это тестовое сообщение для проверки подключения через прокси."}
                    ],
                    temperature=0.5,
                    max_tokens=100,
                    request_timeout=60
                )
                
                # Получаем ответ
                response_text = response.choices[0].message['content']
            else:
                # Для устаревших моделей используем Completion API
                response = openai.Completion.create(
                    model=model,
                    prompt="Привет! Это тестовое сообщение для проверки подключения через прокси.",
                    temperature=0.5,
                    max_tokens=100,
                    request_timeout=60
                )
                
                # Получаем ответ
                response_text = response.choices[0].text
            
            # Записываем результат в файл
            with open(f"proxy_test_result_{model}.txt", "w", encoding="utf-8") as f:
                f.write(f"Успешное подключение к OpenAI API через прокси с моделью {model}!\n\n")
                f.write(f"Ответ от API:\n{response_text}\n\n")
                f.write(f"Полный ответ API:\n{json.dumps(response, default=str, indent=2)}")
            
            logger.info(f"Тест модели {model} успешно завершен.")
            print(f"Тест модели {model} успешно завершен. Результат записан в файл proxy_test_result_{model}.txt")
            
        except Exception as model_error:
            logger.error(f"Ошибка при тестировании модели {model}: {str(model_error)}")
            with open(f"proxy_test_error_{model}.txt", "w", encoding="utf-8") as f:
                f.write(f"Ошибка при тестировании модели {model}: {str(model_error)}\n\n")
                f.write(f"Трассировка: {traceback.format_exc()}\n")
    
except Exception as e:
    error_message = f"Общая ошибка при подключении к OpenAI API: {str(e)}"
    logger.error(error_message)
    logger.error(f"Трассировка: {traceback.format_exc()}")
    
    # Записываем ошибку в файл
    with open("proxy_test_error.txt", "w", encoding="utf-8") as f:
        f.write(f"{error_message}\n\n")
        f.write(f"Трассировка: {traceback.format_exc()}\n\n")
        f.write("Проверьте правильность настроек прокси и API ключа.")
    
    print(f"Тест не удался. Подробности в файле proxy_test_error.txt") 