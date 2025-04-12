# Tests for Coding Platform

This directory contains tests for the Coding Platform application. The tests are organized by module:

- `test_utils.py`: Тесты для вспомогательных функций
- `debug_test.py`: Простой тест для проверки работы тестового фреймворка
- `test_decorators.py`: Тесты для декораторов приложения
- `test_app_basic.py`: Базовые тесты Flask-приложения
- `test_ai_basic.py`: Базовые тесты модуля AI-помощника
- `test_local_error_analyzer.py`: Тесты модуля анализа ошибок
- `test_db_basics.py`: Базовые тесты функций работы с базой данных

## Running the Tests

Вы можете запустить все тесты с помощью:

```bash
python -m tests.run_tests
```

Или запустить отдельные тестовые модули:

```bash
python -m unittest tests.test_utils
python -m unittest tests.debug_test
python -m unittest tests.test_decorators
python -m unittest tests.test_app_basic
python -m unittest tests.test_ai_basic
python -m unittest tests.test_local_error_analyzer
python -m unittest tests.test_db_basics
```

## Test Setup

Тесты используют фреймворк unittest Python и не требуют внешних баз данных или сервисов. Большинство тестов используют моки или временные объекты вместо реальных внешних зависимостей.

## Adding New Tests

При добавлении новой функциональности в приложение, обязательно добавляйте соответствующие тесты. Следуйте этим рекомендациям:

1. Используйте информативные имена тестов, объясняющие что именно тестируется
2. При необходимости используйте методы `setUp` и `tearDown` для инициализации и очистки тестового окружения
3. Делайте тесты простыми и сосредоточенными на единственной функциональности
4. Убедитесь, что тесты выполняются независимо друг от друга
5. Для внешних зависимостей используйте моки (mock) вместо реальных вызовов API

Примечание: Более сложные интеграционные тесты были удалены из-за проблем совместимости с текущей кодовой базой. Текущие тесты проверяют только базовую функциональность и не требуют сложной настройки окружения. 