import requests
import sys

# Настройка прокси
PROXY_URL = "138.0.241.111:8000"
PROXY_USER = "mVQEKQ"
PROXY_PASS = "4pc5U7"

# Настройка прокси для запросов
proxies = {
    "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}",
    "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_URL}"
}

print("Начинаю тест прокси...")

try:
    # Тестируем подключение к httpbin.org через прокси
    print("Тестирую подключение к httpbin.org...")
    response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
    
    print(f"Статус ответа: {response.status_code}")
    print(f"Ваш IP через прокси: {response.json()}")
    print("Тест прокси успешно завершен!")
    
except Exception as e:
    print(f"Ошибка при тестировании прокси: {str(e)}", file=sys.stderr)
    sys.exit(1) 