База данных
==========

Проект использует SQLite для хранения данных. Основные файлы, отвечающие за работу с базой данных:

* `schema.sql` - схема базы данных
* `init_db.py` - скрипт инициализации БД с примерами

Схема базы данных
--------------

Таблица пользователей (users)
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT UNIQUE NOT NULL,
       password TEXT NOT NULL,
       role TEXT NOT NULL DEFAULT 'user'
   );

Содержит информацию о пользователях системы:

* `id` - уникальный идентификатор пользователя
* `username` - имя пользователя (логин)
* `password` - хешированный пароль
* `role` - роль пользователя (user, teacher, admin)

Таблица задач (problems)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE problems (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT NOT NULL,
       difficulty TEXT NOT NULL,
       topic TEXT NOT NULL,
       test_cases TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

Содержит информацию о задачах:

* `id` - уникальный идентификатор задачи
* `title` - название задачи
* `description` - описание задачи
* `difficulty` - уровень сложности (easy, medium, hard)
* `topic` - тема задачи
* `test_cases` - JSON-строка с тестовыми случаями
* `created_at` - время создания задачи

Таблица решений (solutions)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE solutions (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       problem_id INTEGER NOT NULL,
       code TEXT NOT NULL,
       status TEXT NOT NULL,
       error_message TEXT,
       analysis TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users (id),
       FOREIGN KEY (problem_id) REFERENCES problems (id)
   );

Содержит информацию о решениях пользователей:

* `id` - уникальный идентификатор решения
* `user_id` - идентификатор пользователя
* `problem_id` - идентификатор задачи
* `code` - код решения
* `status` - статус решения (passed, failed)
* `error_message` - сообщение об ошибке
* `analysis` - анализ ошибки от LLM
* `created_at` - время создания решения

Инициализация базы данных
----------------------

Инициализация базы данных выполняется через скрипт `init_db.py`, который:

1. Создает таблицы согласно схеме в `schema.sql`
2. Добавляет учетную запись администратора
3. Добавляет примеры задач разной сложности

Примеры задач включают:

* **Легкие задачи**:
  * Сумма чисел
  * Поиск максимального числа
* **Задачи средней сложности**:
  * Проверка на палиндром
  * Числа Фибоначчи
* **Сложные задачи**:
  * Сортировка пузырьком
  * Реализация структуры данных Стек 