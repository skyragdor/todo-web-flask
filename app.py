from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Файл для збереження задач
TASKS_FILE = 'tasks.json'


def load_tasks():
    """Завантажує задачі з файлу"""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_tasks(tasks):
    """Зберігає задачі у файл"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    """Головна сторінка"""
    tasks = load_tasks()

    # Статистика
    total = len(tasks)
    completed = len([t for t in tasks if t['completed']])
    pending = total - completed

    return render_template('index.html',
                           tasks=tasks,
                           total=total,
                           completed=completed,
                           pending=pending)


@app.route('/add', methods=['POST'])
def add_task():
    """Додає нову задачу"""
    title = request.form.get('title', '').strip()
    priority = request.form.get('priority', '2')

    if title:
        tasks = load_tasks()
        task = {
            'id': len(tasks) + 1,
            'title': title,
            'priority': int(priority),
            'completed': False,
            'created': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        tasks.append(task)
        save_tasks(tasks)

    return redirect(url_for('index'))


@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    """Позначає задачу як виконану"""
    tasks = load_tasks()

    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            if task['completed']:
                task['completed_date'] = datetime.now().strftime("%d.%m.%Y %H:%M")
            else:
                task.pop('completed_date', None)
            break

    save_tasks(tasks)
    return redirect(url_for('index'))


@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Видаляє задачу"""
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return redirect(url_for('index'))


@app.route('/clear-completed')
def clear_completed():
    """Видаляє всі виконані задачі"""
    tasks = load_tasks()
    tasks = [t for t in tasks if not t['completed']]
    save_tasks(tasks)
    return redirect(url_for('index'))


@app.route('/api/tasks')
def api_tasks():
    """API endpoint для отримання задач"""
    tasks = load_tasks()
    return jsonify(tasks)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)