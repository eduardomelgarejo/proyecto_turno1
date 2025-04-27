from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import Box, db
import os

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/PlataformaSalud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la aplicación
db.init_app(app)

def insertar_box(tipo_box, capacidad, equipamiento, disponible, id_profesional=None):
    """
    Función para insertar un nuevo box médico en la base de datos
    """
    try:
        nuevo_box = Box(
            tipo_box=tipo_box,
            capacidad=capacidad,
            equipamiento=equipamiento,
            disponible=disponible,
            id_profesional=id_profesional
        )
        
        with app.app_context():
            db.session.add(nuevo_box)
            db.session.commit()
            print(f"Box médico insertado exitosamente: {tipo_box}")
            return True
    except Exception as e:
        print(f"Error al insertar el box médico: {str(e)}")
        return False

if __name__ == "__main__":
    # Ejemplo de uso
    boxes_ejemplo = [
        {
            "tipo_box": "Consulta General",
            "capacidad": 2,
            "equipamiento": "Estetoscopio, tensiómetro, camilla",
            "disponible": True,
            "id_profesional": None
        },
        {
            "tipo_box": "Urgencias",
            "capacidad": 3,
            "equipamiento": "Monitor cardíaco, desfibrilador, camilla de emergencia",
            "disponible": True,
            "id_profesional": None
        }
    ]
    
    for box in boxes_ejemplo:
        insertar_box(
            tipo_box=box["tipo_box"],
            capacidad=box["capacidad"],
            equipamiento=box["equipamiento"],
            disponible=box["disponible"],
            id_profesional=box["id_profesional"]
        ) 