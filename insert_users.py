from models import db, Usuario
from app import app

# Crear nuevos usuarios
usuarios = [
    Usuario(nombre_usuario='usuario1', nombre_completo='Usuario Uno', correo='usuario1@example.com', telefono='123456789', tipo_usuario='paciente', rut='12345678', dv='9'),
    Usuario(nombre_usuario='usuario2', nombre_completo='Usuario Dos', correo='usuario2@example.com', telefono='987654321', tipo_usuario='profesional', rut='87654321', dv='0'),
    Usuario(nombre_usuario='usuario3', nombre_completo='Usuario Tres', correo='usuario3@example.com', telefono='1122334455', tipo_usuario='admin', rut='11223344', dv='1')
]

# Insertar usuarios en la base de datos
with app.app_context():
    for usuario in usuarios:
        usuario.set_password('password123')  # Establecer una contraseña por defecto
        db.session.add(usuario)
    db.session.commit()

print("Usuarios insertados con éxito.") 