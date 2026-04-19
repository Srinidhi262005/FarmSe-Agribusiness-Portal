
# app/task.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Task
from app.forms import TaskForm

task_bp = Blueprint('task', __name__)  # Blueprint name 'task'

# Define the task planner route and give it an endpoint name 'task_planner'
@task_bp.route('/planner', methods=['GET', 'POST'])
def task_planner():
    form = TaskForm()
    if form.validate_on_submit():
        title = form.title.data
        due_date = form.due_date.data
        description = form.description.data
        new_task = Task(title=title, due_date=due_date, description=description)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('task.task_planner'))  # The name matches the blueprint's route name
    tasks = Task.query.all()
    return render_template('task_planner.html', form=form, tasks=tasks)

