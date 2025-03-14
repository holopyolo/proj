from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from datetime import datetime
import subprocess
import json
from dotenv import load_dotenv
from utils import run_code, analyze_error_with_llm, validate_test_cases, format_datetime
from decorators import teacher_required, admin_required
from init_db import init_db_with_samples, SAMPLE_PROBLEMS
import hashlib
import logging
import traceback

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['DATABASE'] = 'coding_platform.db'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Функции для работы с БД
def get_db():
    """Возвращает соединение с базой данных"""
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(
                app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            db.row_factory = sqlite3.Row
        except sqlite3.OperationalError as e:
            # Если не удалось подключиться к основной базе, попробуем альтернативную
            if 'database is locked' in str(e) and app.config['DATABASE'] == 'coding_platform.db':
                alt_db = 'coding_platform_new.db'
                if os.path.exists(alt_db):
                    print(f"Основная база данных заблокирована. Пробуем использовать альтернативную базу {alt_db}")
                    app.config['DATABASE'] = alt_db
                    db = g._database = sqlite3.connect(
                        app.config['DATABASE'],
                        detect_types=sqlite3.PARSE_DECLTYPES
                    )
                    db.row_factory = sqlite3.Row
                else:
                    # Если альтернативной нет, создаем новую базу данных
                    try:
                        print("Создаем новую базу данных...")
                        db = g._database = sqlite3.connect(
                            alt_db,
                            detect_types=sqlite3.PARSE_DECLTYPES
                        )
                        db.row_factory = sqlite3.Row
                        app.config['DATABASE'] = alt_db
                        
                        # Инициализируем новую базу данных
                        init_db_with_samples()
                    except Exception as err:
                        print(f"Не удалось создать новую базу данных: {err}")
                        raise
            else:
                raise  # Если ошибка не связана с блокировкой, пробрасываем исключение дальше
    return db

def close_db(e=None):
    """Закрывает соединение с базой данных по завершении запроса"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Инициализирует базу данных с примерами задач"""
    try:
        # Вместо отдельной инициализации используем функцию с примерами
        return init_db_with_samples()
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {str(e)}")
        return False

@app.teardown_appcontext
def teardown_db(e=None):
    close_db()

# Класс для работы с Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    """Загружает пользователя из базы данных"""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

# Модели данных
def get_all_problems():
    db = get_db()
    problems = db.execute('SELECT * FROM problems').fetchall()
    return problems

def get_problem(problem_id):
    db = get_db()
    problem = db.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    return problem

def add_problem_to_db(title, description, topic, difficulty, test_cases, initial_code, created_by):
    db = get_db()
    db.execute(
        'INSERT INTO problems (title, description, topic, difficulty, test_cases, initial_code, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (title, description, topic, difficulty, test_cases, initial_code, created_by)
    )
    db.commit()

def delete_problem(problem_id):
    db = get_db()
    db.execute('DELETE FROM problems WHERE id = ?', (problem_id,))
    db.commit()

def update_problem(problem_id, title, description, topic, difficulty, test_cases, initial_code):
    db = get_db()
    db.execute(
        'UPDATE problems SET title = ?, description = ?, topic = ?, difficulty = ?, test_cases = ?, initial_code = ? WHERE id = ?',
        (title, description, topic, difficulty, test_cases, initial_code, problem_id)
    )
    db.commit()

def get_user_solutions(user_id):
    db = get_db()
    solutions = db.execute('''
        SELECT s.*, p.title, p.topic, p.difficulty 
        FROM solutions s
        JOIN problems p ON s.problem_id = p.id
        WHERE s.user_id = ?
        ORDER BY s.submitted_at DESC
    ''', (user_id,)).fetchall()
    return solutions

def add_solution(user_id, problem_id, code, status, error_message=None):
    db = get_db()
    db.execute(
        'INSERT INTO solutions (user_id, problem_id, code, status, submitted_at, error_message) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, problem_id, code, status, datetime.now(), error_message)
    )
    db.commit()

# Маршруты
@app.route('/')
def index():
    """Главная страница с списком задач"""
    db = get_db()
    
    # Отладочная информация
    count = db.execute('SELECT COUNT(*) FROM problems').fetchone()[0]
    print(f"Количество задач в базе данных при загрузке главной страницы: {count}")
    
    # Получаем доступные темы и уровни сложности
    topics = db.execute('SELECT DISTINCT topic FROM problems ORDER BY topic').fetchall()
    difficulties = db.execute('SELECT DISTINCT difficulty FROM problems ORDER BY CASE difficulty ' +
                             'WHEN "Легкая" THEN 1 ' +
                             'WHEN "Средняя" THEN 2 ' +
                             'WHEN "Сложная" THEN 3 ' +
                             'ELSE 4 END').fetchall()
    
    # Отладка выбранных фильтров
    topic = request.args.get('topic', '')
    difficulty = request.args.get('difficulty', '')
    search = request.args.get('search', '')
    print(f"Фильтры: тема='{topic}', сложность='{difficulty}', поиск='{search}'")
    
    # Базовый запрос
    query = 'SELECT * FROM problems WHERE 1=1'
    params = []
    
    # Добавляем условия фильтрации
    if topic:
        query += ' AND topic = ?'
        params.append(topic)
    
    if difficulty:
        query += ' AND difficulty = ?'
        params.append(difficulty)
    
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend(['%' + search + '%', '%' + search + '%'])
    
    # Выполняем запрос с фильтрацией
    print(f"SQL запрос: {query}, параметры: {params}")
    problems = db.execute(query + ' ORDER BY difficulty, title', params).fetchall()
    
    # Отладка результатов
    print(f"Найдено задач с заданными фильтрами: {len(problems) if problems else 0}")
    if problems:
        for p in problems:
            print(f"ID: {p['id']}, Название: {p['title']}, Тема: {p['topic']}, Сложность: {p['difficulty']}")
    
    return render_template('index.html', 
                          problems=problems, 
                          topics=topics, 
                          difficulties=difficulties,
                          selected_topic=topic,
                          selected_difficulty=difficulty,
                          search=search)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа в систему"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user:
            # Проверяем пароль с обоими методами хеширования для совместимости
            if check_password_hash(user['password_hash'], password) or user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
                user_obj = User(user['id'], user['username'], user['role'])
                login_user(user_obj)
                flash('Вы успешно вошли в систему!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        db = get_db()
        
        # Проверка существования пользователя
        existing_user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return render_template('register.html')
        
        # Проверка пароля
        if password != password_confirm:
            flash('Пароли не совпадают', 'danger')
            return render_template('register.html')
        
        if len(password) < 4:
            flash('Пароль должен содержать не менее 4 символов', 'danger')
            return render_template('register.html')
        
        # Создание нового пользователя
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
            (username, hashed_password, 'user')
        )
        db.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem(problem_id):
    """Страница задачи с возможностью отправки решения"""
    db = get_db()
    problem = db.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        flash('Задача не найдена', 'danger')
        return redirect(url_for('index'))
    
    # История решений пользователя для этой задачи
    user_solutions = []
    if current_user.is_authenticated:
        user_solutions = db.execute(
            'SELECT * FROM solutions WHERE user_id = ? AND problem_id = ? ORDER BY submitted_at DESC',
            (current_user.id, problem_id)
        ).fetchall()
    
    return render_template('problem.html', 
                          problem=problem, 
                          user_solutions=user_solutions,
                          format_datetime=format_datetime)

@app.route('/submit_solution/<int:problem_id>', methods=['POST'])
def submit_solution(problem_id):
    """Обрабатывает отправку решения пользователя для конкретной задачи."""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    user_code = request.form.get('code', '')
    
    # Получаем задачу из базы данных
    db = get_db()
    problem = db.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        flash('Задача не найдена!', 'danger')
        return redirect(url_for('tasks'))
    
    # Получаем тестовые случаи для задачи
    test_cases = json.loads(problem['test_cases'])
    
    # Запускаем код и проверяем результаты
    try:
        result = run_code(user_code, test_cases)
        
        # Обрабатываем успешное выполнение
        if result.get('success', False):
            # Сохраняем решение в базе данных
            db.execute(
                'INSERT INTO solutions (user_id, problem_id, code, status, submitted_at) VALUES (?, ?, ?, ?, ?)',
                (current_user.id, problem_id, user_code, 'success', datetime.now())
            )
            db.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Поздравляем! Ваше решение успешно прошло все тесты.',
                'output': result.get('output', '')
            })
        
        # Обрабатываем частичный успех или ошибку
        else:
            # Если есть сообщение об ошибке, анализируем его
            if result.get('error'):
                try:
                    # Анализируем ошибку
                    logger.info("Анализируем ошибку в коде...")
                    error_analysis = analyze_error_with_llm(user_code, result.get('error', ''), test_cases)
                    result['analysis'] = error_analysis
                    logger.info("Анализ ошибки успешно выполнен")
                except Exception as e:
                    logger.error(f"Ошибка при анализе: {str(e)}")
                    logger.error(traceback.format_exc())
                    result['analysis'] = f'<div class="alert alert-danger">Ошибка при анализе: {str(e)}</div>'
            
            # Сохраняем неудачное решение в базе данных
            db.execute(
                'INSERT INTO solutions (user_id, problem_id, code, status, error, submitted_at) VALUES (?, ?, ?, ?, ?, ?)',
                (current_user.id, problem_id, user_code, 'error', result.get('error', ''), datetime.now())
            )
            db.commit()
            
            return jsonify({
                'status': 'error',
                'message': 'Решение не прошло тесты.',
                'output': result.get('output', ''),
                'error': result.get('error', ''),
                'analysis': result.get('analysis', '')
            })
    
    except Exception as e:
        # Логируем непредвиденную ошибку
        logger.error(f"Необработанная ошибка при проверке решения: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Сохраняем информацию об ошибке
        db.execute(
            'INSERT INTO solutions (user_id, problem_id, code, status, error, submitted_at) VALUES (?, ?, ?, ?, ?, ?)',
            (current_user.id, problem_id, user_code, 'error', str(e), datetime.now())
        )
        db.commit()
        
        return jsonify({
            'status': 'error',
            'message': 'Произошла ошибка при обработке вашего решения.',
            'error': str(e)
        })

@app.route('/run_tests/<int:problem_id>', methods=['POST'])
def run_tests(problem_id):
    """Запускает тесты для решения, не сохраняя результат."""
    user_code = request.form.get('code', '')
    
    # Получаем задачу и тестовые случаи
    db = get_db()
    problem = db.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        return jsonify({
            'status': 'error',
            'message': 'Задача не найдена!'
        })
    
    test_cases = json.loads(problem['test_cases'])
    
    # Запускаем код и проверяем результаты
    try:
        result = run_code(user_code, test_cases)
        
        # Если есть ошибка, анализируем её
        if not result.get('success', False) and result.get('error'):
            try:
                # Анализируем ошибку
                logger.info("Анализируем ошибку в коде (запуск тестов)...")
                error_analysis = analyze_error_with_llm(user_code, result.get('error', ''), test_cases)
                result['analysis'] = error_analysis
                logger.info("Анализ ошибки успешно выполнен")
            except Exception as e:
                logger.error(f"Ошибка при анализе: {str(e)}")
                logger.error(traceback.format_exc())
                result['analysis'] = f'<div class="alert alert-danger">Ошибка при анализе: {str(e)}</div>'
        
        # Формируем сообщение о результатах
        message = 'Все тесты пройдены!' if result.get('success', False) else 'Тесты не пройдены.'
        
        return jsonify({
            'status': 'success' if result.get('success', False) else 'error',
            'message': message,
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'analysis': result.get('analysis', '')
        })
    
    except Exception as e:
        # Логируем ошибку
        logger.error(f"Необработанная ошибка при запуске тестов: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'status': 'error',
            'message': 'Произошла ошибка при запуске тестов.',
            'error': str(e)
        })

@app.route('/my_solutions')
@login_required
def my_solutions():
    """Страница с историей решений пользователя"""
    db = get_db()
    
    # Получаем решения пользователя с информацией о задачах
    solutions = db.execute('''
        SELECT s.*, p.title as problem_title, p.difficulty
        FROM solutions s
        JOIN problems p ON s.problem_id = p.id
        WHERE s.user_id = ?
        ORDER BY s.submitted_at DESC
    ''', (current_user.id,)).fetchall()
    
    return render_template('my_solutions.html', 
                          solutions=solutions,
                          format_datetime=format_datetime)

@app.route('/add_problem', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_problem():
    """Страница добавления новой задачи"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        topic = request.form['topic']
        difficulty = request.form['difficulty']
        test_cases = request.form['test_cases']
        initial_code = request.form['initial_code']
        
        # Проверяем формат тестовых случаев
        try:
            json.loads(test_cases)
        except json.JSONDecodeError:
            flash('Ошибка в формате тестовых случаев. Проверьте JSON-формат.', 'danger')
            return render_template('add_problem.html', 
                                  title=title, 
                                  description=description,
                                  topic=topic,
                                  difficulty=difficulty,
                                  test_cases=test_cases,
                                  initial_code=initial_code)
        
        # Добавление задачи в базу данных
        db = get_db()
        db.execute(
            'INSERT INTO problems (title, description, topic, difficulty, test_cases, initial_code, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, topic, difficulty, test_cases, initial_code, current_user.id)
        )
        db.commit()
        
        flash('Задача успешно добавлена!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_problem.html')

@app.route('/edit_problem/<int:problem_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_problem(problem_id):
    """Страница редактирования задачи"""
    db = get_db()
    problem = db.execute('SELECT * FROM problems WHERE id = ?', (problem_id,)).fetchone()
    
    if not problem:
        flash('Задача не найдена', 'danger')
        return redirect(url_for('index'))
    
    # Проверяем права доступа (администраторы могут редактировать любые задачи,
    # учителя - только свои)
    if current_user.role != 'admin' and problem['created_by'] != current_user.id:
        flash('У вас нет прав для редактирования этой задачи', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        topic = request.form['topic']
        difficulty = request.form['difficulty']
        test_cases = request.form['test_cases']
        initial_code = request.form['initial_code']
        
        # Проверяем формат тестовых случаев
        try:
            json.loads(test_cases)
        except json.JSONDecodeError:
            flash('Ошибка в формате тестовых случаев. Проверьте JSON-формат.', 'danger')
            return render_template('edit_problem.html', problem=problem)
        
        # Обновление задачи в базе данных
        db.execute(
            'UPDATE problems SET title = ?, description = ?, topic = ?, difficulty = ?, test_cases = ?, initial_code = ? WHERE id = ?',
            (title, description, topic, difficulty, test_cases, initial_code, problem_id)
        )
        db.commit()
        
        flash('Задача успешно обновлена!', 'success')
        return redirect(url_for('problem', problem_id=problem_id))
    
    return render_template('edit_problem.html', problem=problem)

@app.route('/delete_problem/<int:problem_id>', methods=['POST'])
@login_required
@admin_required
def delete_problem_route(problem_id):
    problem = get_problem(problem_id)
    if not problem:
        flash('Задача не найдена')
        return redirect(url_for('index'))
    
    delete_problem(problem_id)
    
    flash('Задача успешно удалена')
    return redirect(url_for('index'))

@app.route('/admin/initialize_samples', methods=['GET', 'POST'])
@login_required
@admin_required
def initialize_samples():
    """Инициализация базы данных с примерами задач"""
    if request.method == 'POST':
        try:
            # Закрываем текущее соединение с базой данных
            db = getattr(g, '_database', None)
            if db is not None:
                db.close()
                g._database = None
            
            # Вызываем функцию инициализации из init_db.py
            success = init_db_with_samples()
            
            if success:
                flash('База данных успешно инициализирована с примерами задач!', 'success')
            else:
                flash('Ошибка при инициализации базы данных. Проверьте лог сервера.', 'danger')
                
        except Exception as e:
            flash(f'Ошибка при инициализации базы данных: {str(e)}', 'danger')
        
        return redirect(url_for('index'))
    
    return render_template('initialize_samples.html')

@app.route('/about')
def about():
    """Страница с информацией о проекте"""
    return render_template('about.html')

if __name__ == '__main__':
    # Проверяем, существует ли база данных, если нет - создаем и инициализируем с примерами задач
    if not os.path.exists(app.config['DATABASE']):
        print("База данных не найдена. Инициализируем с примерами задач...")
        with app.app_context():
            if init_db():
                print("База данных создана и инициализирована с примерами задач.")
            else:
                print("Ошибка при инициализации базы данных с примерами.")
                # Проверяем, не была ли создана альтернативная база данных
                if os.path.exists('coding_platform_new.db'):
                    print("Найдена альтернативная база данных. Используем её.")
                    app.config['DATABASE'] = 'coding_platform_new.db'
    
    # Проверяем количество задач в базе данных при запуске
    with app.app_context():
        try:
            db = get_db()
            count = db.execute('SELECT COUNT(*) FROM problems').fetchone()[0]
            print(f"Количество задач в базе данных: {count}")
            
            # Выводим список задач для отладки
            problems = db.execute('SELECT id, title, topic, difficulty FROM problems').fetchall()
            if problems:
                print("Список задач в базе данных:")
                for p in problems:
                    print(f"ID: {p['id']}, Название: {p['title']}, Тема: {p['topic']}, Сложность: {p['difficulty']}")
            else:
                print("В базе данных нет задач.")
        except Exception as e:
            print(f"Ошибка при проверке базы данных: {str(e)}")
    
    app.run(debug=True) 