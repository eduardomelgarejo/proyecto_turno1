from flask import Flask, session, request
from flask_login import LoginManager
from config import Config
from models import db, Usuario  # Importar Usuario aquí
from rutas import main_bp, socketio  # Importamos el blueprint y socketio
from flask_session import Session
from sesion import sesion_bp  # Importar el Blueprint

# Inicializar la aplicación
app = Flask(__name__)
app.config.from_object(Config)

# Configurar Flask-Session para usar SQLAlchemy
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db

# Inicializar la base de datos
db.init_app(app)

# Inicializar la sesión
Session(app)

# Inicializar el administrador de sesiones
login_manager = LoginManager()
login_manager.init_app(app)

# Registrar los blueprints
app.register_blueprint(main_bp)
app.register_blueprint(sesion_bp)

# Cargar el usuario actual
@login_manager.user_loader
def load_user(user_id):
    from models import Usuario  # Importación diferida para evitar problemas de importación circular
    return Usuario.query.get(int(user_id))

def authenticate_user():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = Usuario.query.filter_by(nombre_usuario=username).first()
    if user and user.check_password(password):
        return user
    return None

@app.route('/login', methods=['POST'])
def login():
    user = authenticate_user()
    if user:
        session['user_id'] = user.id_usuario  # Almacenar el id_usuario en la sesión
        return 'Usuario autenticado'
    return 'Error de autenticación'

# Iniciar la aplicación
if __name__ == '__main__':
    try:
        with app.app_context():  # Contexto de la aplicación 
            db.create_all()  # Crear todas las tablas de nuevo
        socketio.run(app, debug=True)  # Iniciar la aplicación con Socket.IO
    except SystemExit as e:
        print("⚠️ La aplicación se cerró con SystemExit:", e)  # Manejar la excepción SystemExit
    except Exception as e:
        print("⚠️ Error al iniciar la app:", e)  # Manejar cualquier otra excepción
