Установка
=========

Требования
--------

* Python 3.8+
* SQLite3
* OpenAI API ключ (для анализа ошибок)

Установка с Git
------------

1. Клонируйте репозиторий:

.. code-block:: bash

    git clone <repository-url>
    cd coding-platform

2. Создайте виртуальное окружение и активируйте его:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # для Linux/Mac
    venv\Scripts\activate     # для Windows

3. Установите зависимости:

.. code-block:: bash

    pip install -r requirements.txt

4. Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные:

.. code-block:: text

    SECRET_KEY=your-secret-key
    OPENAI_API_KEY=your-openai-api-key

Конфигурация
-----------

Система использует файл `.env` для хранения конфиденциальных настроек:

* `SECRET_KEY`: Секретный ключ для Flask-приложения и безопасности сессий
* `OPENAI_API_KEY`: API-ключ для OpenAI, используемый для анализа ошибок

Инициализация базы данных
-----------------------

При первом запуске приложения база данных будет создана автоматически. Для загрузки примеров задач:

1. Запустите приложение
2. Войдите как администратор (логин: admin, пароль: admin)
3. Перейдите по адресу `/admin/initialize_samples`

Запуск приложения
--------------

Для запуска приложения выполните:

.. code-block:: bash

    python app.py

Приложение будет доступно по адресу `http://localhost:5000`. 