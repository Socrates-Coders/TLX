from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from forms import RegistrationForm, LoginForm, TimeLogForm, RequestChangeForm, GenerateReportForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(150), unique=True, nullable=False)
        password_hash = db.Column(db.String(128), nullable=False)

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    class TimeLog(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        end_time = db.Column(db.DateTime, nullable=True)
        duration = db.Column(db.Interval, nullable=True)

        def calculate_duration(self):
            if self.start_time and self.end_time:
                self.duration = self.end_time - self.start_time

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/time_log', methods=['GET', 'POST'])
    @login_required
    def time_log():
        form = TimeLogForm()
        return render_template('time_log.html', form=form)

    @app.route('/request_change', methods=['GET', 'POST'])
    @login_required
    def request_change():
        form = RequestChangeForm()
        return render_template('request_change.html', form=form)

    @app.route('/schedule', methods=['GET', 'POST'])
    @login_required
    def schedule():
        # Assuming current_user has an attribute 'id' that corresponds to employee_id in Schedule
        now = datetime.now()
        start_of_week = now - timedelta(days=now.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Query schedules for the current week
        schedules = Schedule.query.filter(
            Schedule.employee_id == current_user.id,
            Schedule.start_time >= start_of_week,
            Schedule.end_time <= end_of_week
        ).all()

        return render_template('schedule.html', schedules=schedules)

    @app.route('/generate_report')
    @login_required
    def generate_report():
        form = GenerateReportForm()
        return render_template('generate_report.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
