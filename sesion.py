from flask import Blueprint, session

# Crear un Blueprint
sesion_bp = Blueprint('sesion', __name__)

@sesion_bp.route('/')
def index():
    # Obtener los datos de la sesión
    session_data = {
        'key': session.get('key', 'No data'),
        'user_id': session.get('user_id', 'No user ID')  # Obtener el id_usuario de la sesión
    }
    # Mostrar los datos de la sesión
    return f'Sesión configurada con base de datos: {session_data}'

