app - Основной модуль приложения
============================

Основной модуль приложения содержит маршруты Flask, обработчики запросов и логику взаимодействия пользователя с платформой.

.. automodule:: app
   :members:
   :undoc-members:
   :show-inheritance:

Основные маршруты
--------------

Главная страница
~~~~~~~~~~~~~~

.. code-block:: python

   @app.route('/')
   def index():
       # Отображение списка задач

Страница задачи
~~~~~~~~~~~~~

.. code-block:: python

   @app.route('/problem/<int:problem_id>')
   def problem(problem_id):
       # Отображение страницы задачи с редактором кода

Проверка решения
~~~~~~~~~~~~~

.. code-block:: python

   @app.route('/submit', methods=['POST'])
   def submit_solution():
       # Обработка отправленного пользователем решения

Авторизация
~~~~~~~~~

.. code-block:: python

   @app.route('/login', methods=['GET', 'POST'])
   def login():
       # Авторизация пользователя

   @app.route('/register', methods=['GET', 'POST'])
   def register():
       # Регистрация нового пользователя

   @app.route('/logout')
   def logout():
       # Выход из системы

Администрирование
~~~~~~~~~~~~~~

.. code-block:: python

   @app.route('/add_problem', methods=['GET', 'POST'])
   @admin_required
   def add_problem():
       # Добавление новой задачи

   @app.route('/edit_problem/<int:problem_id>', methods=['GET', 'POST'])
   @admin_required
   def edit_problem(problem_id):
       # Редактирование существующей задачи

   @app.route('/admin/initialize_samples')
   @admin_required
   def initialize_samples():
       # Инициализация примеров задач 