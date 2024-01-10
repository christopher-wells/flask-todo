# app.py
from flask import Flask, render_template, request
from flask_mail import Mail, Message
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
mail = Mail(app)
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.title

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        email = request.form['email']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d %H:%M:%S')
        task = Task(title=title, description=description, email=email, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        msg = Message('Task Reminder', sender='your_email@gmail.com', recipients=[email])
        msg.body = 'You have a new task: ' + title
        mail.send(msg)
        return render_template('index.html', tasks=Task.query.all())
    else:
        return render_template('add_task.html')

@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.email = request.form['email']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d %H:%M:%S')
        db.session.commit()
        msg = Message('Task Reminder', sender='your_email@gmail.com', recipients=[task.email])
        msg.body = 'Your task has been updated: ' + task.title
        mail.send(msg)
        return render_template('index.html', tasks=Task.query.all())
    else:
        return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return render_template('index.html', tasks=Task.query.all())

def check_due_dates():
    for task in Task.query.all():
        if task.due_date <= datetime.now():
            msg = Message('Task Reminder', sender='your_email@gmail.com', recipients=[task.email])
            msg.body = 'Your task is due: ' + task.title
            mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
