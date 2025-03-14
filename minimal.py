print("Hello, World!")

# Проверка импортов
import os
print(f"Текущая директория: {os.getcwd()}")

import sqlite3
print("SQLite импортирован успешно")

# Проверка существования файлов
if os.path.exists('schema.sql'):
    print("Файл schema.sql существует")
else:
    print("Файл schema.sql НЕ существует")

if os.path.exists('coding_platform.db'):
    print("Файл coding_platform.db существует")
else:
    print("Файл coding_platform.db НЕ существует") 