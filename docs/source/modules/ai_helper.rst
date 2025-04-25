ai_helper - Модуль анализа ошибок с помощью AI
========================================

Модуль содержит функции для анализа ошибок в коде пользователя с использованием OpenAI API.

.. automodule:: ai_helper
   :members:
   :undoc-members:
   :show-inheritance:

Основные функции
-------------

.. code-block:: python

   def analyze_error(code, error_message, test_cases):
       """
       Анализирует ошибку в коде пользователя.
       
       Args:
           code (str): Код пользователя
           error_message (str): Сообщение об ошибке
           test_cases (list): Список тестовых случаев
           
       Returns:
           dict: Анализ ошибки с рекомендациями
       """

   def get_error_type(error_message):
       """
       Определяет тип ошибки.
       
       Args:
           error_message (str): Сообщение об ошибке
           
       Returns:
           str: Тип ошибки (синтаксическая, времени выполнения, логическая)
       """

Взаимодействие с OpenAI API
------------------------

.. code-block:: python

   def generate_openai_prompt(code, error_message, test_cases):
       """
       Формирует запрос к OpenAI API.
       
       Args:
           code (str): Код пользователя
           error_message (str): Сообщение об ошибке
           test_cases (list): Список тестовых случаев
           
       Returns:
           str: Текст запроса
       """

   def call_openai_api(prompt):
       """
       Отправляет запрос к OpenAI API.
       
       Args:
           prompt (str): Текст запроса
           
       Returns:
           str: Ответ от API
       """

   def parse_openai_response(response):
       """
       Обрабатывает ответ от OpenAI API.
       
       Args:
           response (str): Ответ от API
           
       Returns:
           dict: Структурированный анализ ошибки
       """ 