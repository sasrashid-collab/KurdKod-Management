from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, Company, User, ActivityLog
from translation_service import setup_i18n
import uuid, os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
setup_i18n(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def log_action(action):
    ip = request.remote_addr
    user_id = current_user.id if current_user.is_authenticated else None
    log = ActivityLog(user_id=user_id, action=action, ip_address=ip)
    db.session.add(log)
    db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        license_key = request.form.get('license_key', '').strip()

        user = User.query.filter_by(username=username, is_deleted=False).first()
        if not user or not user.check_password(password):
            flash('invalid_credentials', 'error')
            return redirect(url_for('login'))

        if not user.company.verify_license(license_key, app.config['SECRET_KEY']):
            flash('invalid_license', 'error')
            return redirect(url_for('login'))

        if not user.is_active or not user.company.is_active:
            flash('account_inactive', 'error')
            return redirect(url_for('login'))

        login_user(user)
        log_action('login_success')
        flash('welcome', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register-company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        comp_name = request.form.get('company_name', '').strip()
        admin_user = request.form.get('admin_username', '').strip()
        admin_pass = request.form.get('admin_password', '')

        if not all([comp_name, admin_user, admin_pass]):
            flash('fill_fields', 'error')
            return redirect(url_for('register_company'))

        if Company.query.filter_by(name=comp_name).first():
            flash('company_exists', 'error')
            return redirect(url_for('register_company'))

        license_key = f"KMG1-{uuid.uuid4().hex[:16].upper()}-{2026}"
        company = Company(name=comp_name)
        company.set_license(license_key, app.config['SECRET_KEY'])
        db.session.add(company)
        db.session.commit()

        admin = User(username=admin_user, role='بەڕێوەبەری گشتی', company_id=company.id)
        admin.set_password(admin_pass)
        db.session.add(admin)
        db.session.commit()

        log_action(f'company_created: {comp_name}')
        flash('company_success', 'success')
        session['temp_license'] = license_key  # بۆ نیشاندان دوای تۆمارکردن
        return redirect(url_for('login'))
    return render_template('register_company.html')

@app.route('/dashboard')
@login_required
def dashboard():
    users_count = User.query.filter_by(company_id=current_user.company.id, is_deleted=False).count()
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(5).all()
    temp_license = session.pop('temp_license', None)
    return render_template('dashboard.html', users_count=users_count, logs=logs, temp_license=temp_license)

@app.route('/logout')
@login_required
def logout():
    log_action('logout')
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-lang/<lang>')
@login_required
def change_lang(lang):
    if lang in ['ku', 'ar', 'en']:
        current_user.preferred_language = lang
        db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

def init_db():
    with app.app_context():
        db.create_all()
        if not Company.query.filter_by(name='K-Kood').first():
            c = Company(name='K-Kood')
            c.set_license('KMG1-DEMO-2026-TEST', app.config['SECRET_KEY'])
            db.session.add(c)
            db.session.commit()
            admin = User(username='admin', role='بەڕێوەبەری گشتی', company_id=c.id, preferred_language='ku')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ داتابەیس و هەژماری تاقیکردنەوە دروستکرا.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
