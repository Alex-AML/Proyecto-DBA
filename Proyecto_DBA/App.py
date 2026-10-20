from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import io
from Models import db, User
from Forms import LoginForm

# Configurar la carpeta estática como 'Static' (con mayúscula)
app = Flask(__name__, static_folder='Static')
app.config['SECRET_KEY'] = 'clave-super-segura-cambiar-en-produccion'
# Cambia estos datos por los de tu PostgreSQL local
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost/vicar_db'
# Para desarrollo local con SQLite sin necesidad de configurar PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vicar.db'
# ^^^^Para desarrollo local con SQLite sin necesidad de configurar PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'Login'
login_manager.login_message = 'Por favor inicie sesión para acceder.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Autenticación ----------
@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if current_user.is_authenticated:
        return redirect(url_for('Dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'Bienvenido {user.username}', 'success')
            return redirect(url_for('Dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('Login.html', form=form)

@app.route('/Logout')
@login_required
def Logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('Login'))

@app.route('/')
@login_required
def Dashboard():
    total_vehicles = Vehicle.query.count()
    total_drivers = Driver.query.count()
    active_rentals = Rental.query.filter(Rental.end_date.is_(None)).count()
    pending_maintenance = Maintenance.query.filter(Maintenance.next_maintenance_date >= datetime.today()).count()
    return render_template('Dashboard.html',
                           total_vehicles=total_vehicles,
                           total_drivers=total_drivers,
                           active_rentals=active_rentals,
                           pending_maintenance=pending_maintenance)

# ---------- Crear tablas y usuario admin por defecto ----------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado: admin / admin123")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
