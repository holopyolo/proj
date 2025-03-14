import sqlite3
import os
import json
from werkzeug.security import generate_password_hash
import hashlib

SAMPLE_PROBLEMS = [
    {
        "title": "Сумма двух чисел",
        "description": """# Сумма двух чисел

Напишите функцию `sum_two_numbers(a, b)`, которая принимает два числа и возвращает их сумму.

## Пример:
```python
sum_two_numbers(5, 3)  # Должно вернуть 8
sum_two_numbers(-1, 1)  # Должно вернуть 0
sum_two_numbers(0, 0)  # Должно вернуть 0
```

## Примечания:
- Функция должна работать с целыми и дробными числами
""",
        "topic": "Основы",
        "difficulty": "Легкая",
        "test_cases": """[
            {"input": [5, 3], "expected": 8},
            {"input": [-1, 1], "expected": 0},
            {"input": [0, 0], "expected": 0},
            {"input": [2.5, 3.5], "expected": 6.0}
        ]""",
        "initial_code": """def sum_two_numbers(a, b):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Максимум из трех чисел",
        "description": """# Максимум из трех чисел

Напишите функцию `find_max(a, b, c)`, которая принимает три числа и возвращает наибольшее из них.

## Пример:
```python
find_max(5, 3, 9)  # Должно вернуть 9
find_max(5, 5, 1)  # Должно вернуть 5
find_max(-1, -5, -3)  # Должно вернуть -1
```

## Примечания:
- Если несколько чисел равны максимальному, верните любое из них
""",
        "topic": "Основы",
        "difficulty": "Легкая",
        "test_cases": """[
            {"input": [5, 3, 9], "expected": 9},
            {"input": [5, 5, 1], "expected": 5},
            {"input": [-1, -5, -3], "expected": -1},
            {"input": [0, 0, 0], "expected": 0}
        ]""",
        "initial_code": """def find_max(a, b, c):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Проверка на палиндром",
        "description": """# Проверка на палиндром

Напишите функцию `is_palindrome(text)`, которая принимает строку и проверяет, является ли она палиндромом.
Палиндром — это строка, которая читается одинаково слева направо и справа налево.

## Пример:
```python
is_palindrome("radar")  # Должно вернуть True
is_palindrome("hello")  # Должно вернуть False
is_palindrome("А роза упала на лапу Азора")  # Должно вернуть True
```

## Примечания:
- Функция должна игнорировать регистр букв
- Функция должна игнорировать пробелы и знаки препинания
""",
        "topic": "Строки",
        "difficulty": "Средняя",
        "test_cases": """[
            {"input": ["radar"], "expected": True},
            {"input": ["hello"], "expected": False},
            {"input": ["А роза упала на лапу Азора"], "expected": True},
            {"input": ["Madam, I'm Adam"], "expected": True},
            {"input": [""], "expected": True}
        ]""",
        "initial_code": """def is_palindrome(text):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Числа Фибоначчи",
        "description": """# Числа Фибоначчи

Напишите функцию `fibonacci(n)`, которая возвращает n-ое число Фибоначчи.
Последовательность Фибоначчи определяется так: первые два числа равны 0 и 1, а каждое последующее равно сумме двух предыдущих.

## Пример:
```python
fibonacci(0)  # Должно вернуть 0
fibonacci(1)  # Должно вернуть 1
fibonacci(6)  # Должно вернуть 8 (последовательность: 0, 1, 1, 2, 3, 5, 8)
```

## Примечания:
- Используйте нумерацию с нуля: fibonacci(0) = 0, fibonacci(1) = 1, ...
- Для больших n старайтесь использовать эффективный алгоритм
""",
        "topic": "Алгоритмы",
        "difficulty": "Средняя",
        "test_cases": """[
            {"input": [0], "expected": 0},
            {"input": [1], "expected": 1},
            {"input": [6], "expected": 8},
            {"input": [10], "expected": 55}
        ]""",
        "initial_code": """def fibonacci(n):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Реализация стека",
        "description": """# Реализация стека

Реализуйте класс `Stack`, который имеет следующие методы:
- `push(item)` - добавляет элемент в стек
- `pop()` - удаляет и возвращает верхний элемент стека, если стек пустой, вызывает IndexError
- `peek()` - возвращает верхний элемент стека без удаления, если стек пустой, вызывает IndexError
- `is_empty()` - возвращает True, если стек пустой, иначе False
- `size()` - возвращает количество элементов в стеке

## Пример:
```python
stack = Stack()
stack.push(1)
stack.push(2)
stack.peek()  # Должно вернуть 2
stack.pop()  # Должно вернуть 2
stack.size()  # Должно вернуть 1
stack.is_empty()  # Должно вернуть False
stack.pop()  # Должно вернуть 1
stack.is_empty()  # Должно вернуть True
```

## Примечания:
- Используйте только встроенные структуры данных (список, словарь и т.д.)
""",
        "topic": "Структуры данных",
        "difficulty": "Средняя",
        "test_cases": """[
            {
                "input": [
                    ["push", 1],
                    ["push", 2],
                    ["peek"],
                    ["pop"],
                    ["size"],
                    ["is_empty"],
                    ["pop"],
                    ["is_empty"]
                ],
                "expected": [None, None, 2, 2, 1, False, 1, True]
            }
        ]""",
        "initial_code": """class Stack:
    def __init__(self):
        # Инициализация стека
        pass
    
    def push(self, item):
        # Добавление элемента в стек
        pass
    
    def pop(self):
        # Удаление и возврат верхнего элемента
        pass
    
    def peek(self):
        # Просмотр верхнего элемента без удаления
        pass
    
    def is_empty(self):
        # Проверка, пуст ли стек
        pass
    
    def size(self):
        # Возвращает размер стека
        pass

# Для тестирования - НЕ ИЗМЕНЯЙТЕ этот код
def test_stack(operations):
    stack = Stack()
    results = []
    
    for op in operations:
        if op[0] == "push":
            results.append(stack.push(op[1]))
        elif op[0] == "pop":
            results.append(stack.pop())
        elif op[0] == "peek":
            results.append(stack.peek())
        elif op[0] == "is_empty":
            results.append(stack.is_empty())
        elif op[0] == "size":
            results.append(stack.size())
    
    return results
"""
    },
    {
        "title": "Сортировка пузырьком",
        "description": """# Сортировка пузырьком

Реализуйте функцию `bubble_sort(array)`, которая сортирует массив целых чисел методом пузырька по возрастанию.

## Алгоритм сортировки пузырьком:
1. Проходим по массиву и сравниваем соседние элементы.
2. Если текущий элемент больше следующего, меняем их местами.
3. Повторяем, пока массив не будет отсортирован.

## Пример:
```python
bubble_sort([5, 3, 8, 6, 7, 2])  # Должно вернуть [2, 3, 5, 6, 7, 8]
bubble_sort([])  # Должно вернуть []
bubble_sort([1])  # Должно вернуть [1]
```

## Примечания:
- Функция должна изменять исходный массив и возвращать его
- Постарайтесь оптимизировать алгоритм, чтобы избежать лишних проходов
""",
        "topic": "Алгоритмы",
        "difficulty": "Сложная",
        "test_cases": """[
            {"input": [[5, 3, 8, 6, 7, 2]], "expected": [2, 3, 5, 6, 7, 8]},
            {"input": [[]], "expected": []},
            {"input": [[1]], "expected": [1]},
            {"input": [[9, 8, 7, 6, 5]], "expected": [5, 6, 7, 8, 9]},
            {"input": [[1, 2, 3, 4, 5]], "expected": [1, 2, 3, 4, 5]}
        ]""",
        "initial_code": """def bubble_sort(array):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Подсчет частоты слов",
        "description": """# Подсчет частоты слов

Напишите функцию `count_words(text)`, которая принимает строку текста и возвращает словарь, где ключи - это слова, а значения - количество их появлений в тексте.

## Пример:
```python
count_words("кот собака кот кошка")  # Должно вернуть {"кот": 2, "собака": 1, "кошка": 1}
count_words("яблоко груша яблоко банан апельсин яблоко")  # Должно вернуть {"яблоко": 3, "груша": 1, "банан": 1, "апельсин": 1}
```

## Примечания:
- Считайте, что слова разделены пробелами
- Игнорируйте регистр букв (яблоко и Яблоко считаются одним словом)
- Игнорируйте знаки препинания (если они прилегают к словам)
""",
        "topic": "Строки",
        "difficulty": "Средняя",
        "test_cases": """[
            {"input": ["кот собака кот кошка"], "expected": {"кот": 2, "собака": 1, "кошка": 1}},
            {"input": ["яблоко груша яблоко банан апельсин яблоко"], "expected": {"яблоко": 3, "груша": 1, "банан": 1, "апельсин": 1}},
            {"input": ["Привет, мир! Привет, программирование."], "expected": {"привет": 2, "мир": 1, "программирование": 1}},
            {"input": [""], "expected": {}}
        ]""",
        "initial_code": """def count_words(text):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Факториал числа",
        "description": """# Факториал числа

Напишите функцию `factorial(n)`, которая вычисляет факториал числа n.
Факториал числа n (обозначается как n!) - это произведение всех положительных целых чисел, меньших или равных n.

## Пример:
```python
factorial(0)  # Должно вернуть 1 (по определению)
factorial(1)  # Должно вернуть 1
factorial(5)  # Должно вернуть 120 (5 * 4 * 3 * 2 * 1)
```

## Примечания:
- Функция должна работать для n в диапазоне от 0 до 20
- Можно использовать как рекурсивный, так и итеративный подход
""",
        "topic": "Рекурсия",
        "difficulty": "Легкая",
        "test_cases": """[
            {"input": [0], "expected": 1},
            {"input": [1], "expected": 1},
            {"input": [5], "expected": 120},
            {"input": [10], "expected": 3628800}
        ]""",
        "initial_code": """def factorial(n):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Проверка на простое число",
        "description": """# Проверка на простое число

Напишите функцию `is_prime(n)`, которая проверяет, является ли число n простым.
Простое число - это натуральное число больше 1, которое не имеет положительных делителей, кроме 1 и самого себя.

## Пример:
```python
is_prime(2)  # Должно вернуть True
is_prime(4)  # Должно вернуть False
is_prime(17)  # Должно вернуть True
```

## Примечания:
- Функция должна работать для n до 10^6
- Попробуйте реализовать эффективный алгоритм проверки
- По определению, числа 0 и 1 НЕ являются простыми
""",
        "topic": "Математика",
        "difficulty": "Средняя",
        "test_cases": """[
            {"input": [2], "expected": true},
            {"input": [4], "expected": false},
            {"input": [17], "expected": true},
            {"input": [1], "expected": false},
            {"input": [97], "expected": true},
            {"input": [100], "expected": false}
        ]""",
        "initial_code": """def is_prime(n):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Обратная польская нотация",
        "description": """# Обратная польская нотация

Реализуйте функцию `evaluate_rpn(expression)`, которая вычисляет выражение, записанное в обратной польской нотации (постфиксной записи).

В обратной польской нотации операторы следуют за операндами. Например:
- `"2 3 +"` означает `2 + 3 = 5`
- `"4 5 * 2 +"` означает `4 * 5 + 2 = 22`

## Пример:
```python
evaluate_rpn("2 3 +")  # Должно вернуть 5
evaluate_rpn("4 5 * 2 +")  # Должно вернуть 22
evaluate_rpn("3 4 + 5 *")  # Должно вернуть 35
```

## Примечания:
- Поддерживаемые операции: +, -, *, / (целочисленное деление)
- Все элементы в выражении разделены пробелами
- Гарантируется, что выражение корректно и всегда даёт целочисленный результат
""",
        "topic": "Структуры данных",
        "difficulty": "Сложная",
        "test_cases": """[
            {"input": ["2 3 +"], "expected": 5},
            {"input": ["4 5 * 2 +"], "expected": 22},
            {"input": ["3 4 + 5 *"], "expected": 35},
            {"input": ["5 1 2 + 4 * + 3 -"], "expected": 14},
            {"input": ["10 2 /"], "expected": 5}
        ]""",
        "initial_code": """def evaluate_rpn(expression):
    # Ваш код здесь
    pass
"""
    },
    {
        "title": "Поиск общего предка в бинарном дереве",
        "description": """# Поиск наименьшего общего предка в бинарном дереве поиска

Напишите функцию `lowest_common_ancestor(root, p, q)`, которая находит наименьшего общего предка (LCA) двух узлов в бинарном дереве поиска.

Наименьший общий предок - это узел, который является наиболее глубоким общим предком p и q.

Класс `TreeNode` уже определен. Вы будете работать с бинарным деревом поиска, где для каждого узла:
- Все узлы в левом поддереве имеют значения меньше значения узла
- Все узлы в правом поддереве имеют значения больше значения узла

## Пример:
```
      6
    /   \\
   2     8
  / \\   / \\
 0   4  7   9
    / \\
   3   5
```

```python
lowest_common_ancestor(root, 2, 8)  # Должно вернуть 6
lowest_common_ancestor(root, 2, 4)  # Должно вернуть 2
```

## Примечания:
- Все значения узлов уникальны
- Гарантируется, что p и q существуют в дереве
- В BST (бинарном дереве поиска) можно использовать свойства упорядоченности для более эффективного решения
""",
        "topic": "Деревья",
        "difficulty": "Сложная",
        "test_cases": """[
            {
                "input": [
                    {"type": "tree", "value": [6, 2, 8, 0, 4, 7, 9, null, null, 3, 5]},
                    2,
                    8
                ],
                "expected": 6
            },
            {
                "input": [
                    {"type": "tree", "value": [6, 2, 8, 0, 4, 7, 9, null, null, 3, 5]},
                    2,
                    4
                ],
                "expected": 2
            },
            {
                "input": [
                    {"type": "tree", "value": [6, 2, 8, 0, 4, 7, 9, null, null, 3, 5]},
                    3,
                    5
                ],
                "expected": 4
            }
        ]""",
        "initial_code": """class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def lowest_common_ancestor(root, p, q):
    # Ваш код здесь
    pass

# Вспомогательная функция для создания дерева из списка
def build_tree(values):
    if not values or values[0] is None:
        return None
    
    root = TreeNode(values[0])
    queue = [root]
    i = 1
    
    while queue and i < len(values):
        node = queue.pop(0)
        
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    
    return root

# Функция для тестирования
def test_lca(tree_values, p_val, q_val):
    root = build_tree(tree_values)
    
    # Ищем узлы p и q
    p_node = find_node(root, p_val)
    q_node = find_node(root, q_val)
    
    if not p_node or not q_node:
        return None
    
    lca = lowest_common_ancestor(root, p_val, q_val)
    return lca

# Функция для поиска узла по значению
def find_node(root, val):
    if not root:
        return None
    if root.val == val:
        return root
    
    left = find_node(root.left, val)
    if left:
        return left
    
    return find_node(root.right, val)
"""
    }
]

def init_db_with_samples():
    """Инициализирует базу данных с примерами задач"""
    
    db_file = 'coding_platform.db'
    schema_file = 'schema.sql'
    
    # Выводим отладочную информацию
    print(f"[init_db] Начинаем инициализацию базы данных {db_file}...")
    
    # Проверяем, существует ли файл схемы
    if not os.path.exists(schema_file):
        print(f"[init_db] ОШИБКА: Файл схемы {schema_file} не найден!")
        return False
    
    # Проверяем, существует ли файл базы данных
    if os.path.exists(db_file):
        try:
            print(f"[init_db] База данных {db_file} уже существует. Удаляем её для переинициализации...")
            os.remove(db_file)
            print(f"[init_db] Файл {db_file} удалён успешно.")
        except PermissionError:
            print(f"[init_db] Не удалось удалить файл базы данных. Файл используется другим процессом.")
            print(f"[init_db] Создаем новую базу данных с другим именем...")
            db_file = 'coding_platform_new.db'
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    print(f"[init_db] Файл {db_file} удалён успешно.")
                except Exception as e:
                    print(f"[init_db] Не удалось удалить файл {db_file}: {str(e)}")
                    return False
    
    # Создаем базу данных и подключаемся к ней
    conn = None
    try:
        # Подключаемся к базе данных
        print(f"[init_db] Создаем новую базу данных {db_file}...")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Читаем и выполняем схему из файла
        print(f"[init_db] Читаем схему из файла {schema_file}...")
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        print(f"[init_db] Применяем схему к базе данных...")
        conn.executescript(schema)
        
        # Создаем пользователей по умолчанию
        print(f"[init_db] Создаем пользователей по умолчанию...")
        users = [
            ('admin', 'admin', 'admin'),  # username, password, role
            ('teacher', 'teacher', 'teacher')
        ]
        
        for username, password, role in users:
            # Хеширование пароля
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(f"[init_db] Создаем пользователя: {username} с ролью {role}")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
        
        # Добавляем примеры задач
        print(f"[init_db] Добавляем примеры задач...")
        for i, problem in enumerate(SAMPLE_PROBLEMS, 1):
            print(f"[init_db] Добавляем задачу {i}/{len(SAMPLE_PROBLEMS)}: {problem['title']}")
            cursor.execute(
                """
                INSERT INTO problems 
                (title, description, topic, difficulty, test_cases, initial_code, created_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    problem['title'],
                    problem['description'],
                    problem['topic'],
                    problem['difficulty'],
                    problem['test_cases'],
                    problem['initial_code'],
                    1  # created_by (admin user id)
                )
            )
        
        # Сохраняем изменения
        print(f"[init_db] Сохраняем изменения в базе данных...")
        conn.commit()
        print(f"[init_db] База данных {db_file} успешно инициализирована с примерами задач и пользователями.")

        # Проверяем, создали ли мы новую базу данных с другим именем
        if db_file != 'coding_platform.db':
            print(f"[init_db] ВНИМАНИЕ: Создана новая база данных с именем {db_file}")
            print(f"[init_db] Для использования этой базы данных измените параметр DATABASE в app.py")
        
        return True
    except Exception as e:
        print(f"[init_db] ОШИБКА при инициализации базы данных: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# Если этот файл запущен напрямую, выполняем инициализацию
if __name__ == "__main__":
    print("Запуск инициализации базы данных...")
    success = init_db_with_samples()
    if success:
        print("Инициализация успешно завершена!")
    else:
        print("Инициализация завершилась с ошибкой.") 