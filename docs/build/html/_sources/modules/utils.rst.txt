utils - Модуль утилит
====================

Модуль содержит вспомогательные функции для работы с кодом пользователя, проверки решений и взаимодействия с базой данных.

.. automodule:: utils
   :members:
   :undoc-members:
   :show-inheritance:

Работа с кодом пользователя
------------------------

.. code-block:: python

   def run_code(code, input_data):
       """
       Запускает код пользователя с указанными входными данными.
       
       Args:
           code (str): Код пользователя
           input_data (str): Входные данные для кода
           
       Returns:
           tuple: (stdout, stderr, exit_code)
       """

   def check_solution(code, test_cases):
       """
       Проверяет решение пользователя на тестовых случаях.
       
       Args:
           code (str): Код пользователя
           test_cases (list): Список тестовых случаев
           
       Returns:
           dict: Результаты проверки
       """

Функции для работы с базой данных
-----------------------------

.. code-block:: python

   def get_db_connection():
       """
       Возвращает соединение с базой данных.
       
       Returns:
           sqlite3.Connection: Соединение с базой данных
       """

   def get_problem(problem_id):
       """
       Получает информацию о задаче по ID.
       
       Args:
           problem_id (int): ID задачи
           
       Returns:
           dict: Информация о задаче
       """

   def get_user_solutions(user_id):
       """
       Получает список решений пользователя.
       
       Args:
           user_id (int): ID пользователя
           
       Returns:
           list: Список решений пользователя
       """ 