from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db
from rutas import main_bp  # Importamos el blueprint
from flask_session import Session

# Inicializar la aplicación
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Inicializar el administrador de sesiones
login_manager = LoginManager()
login_manager.init_app(app)

# Registrar el blueprint
app.register_blueprint(main_bp)

# Configurar Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Cargar el usuario actual
@login_manager.user_loader
def load_user(user_id):
    from models import Usuario  # Importamos Usuario aquí para evitar problemas de importación circular
    return Usuario.query.get(int(user_id))

# Iniciar la aplicación
if __name__ == '__main__':
    try:
        with app.app_context(): # Contexto de la aplicación
            db.create_all() # Crear todas las tablas de la base de datos
        app.run(debug=True) # Iniciar la aplicación en modo de desarrollo
    except SystemExit as e:
        print("⚠️ La aplicación se cerró con SystemExit:", e) # Manejar la excepción SystemExit
    except Exception as e:
        print("⚠️ Error al iniciar la app:", e) # Manejar cualquier otra excepción
