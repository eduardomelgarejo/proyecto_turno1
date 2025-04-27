import requests
from models import db, Usuario
from app import app
from flask import request

# Crear nuevos usuarios
usuarios = [
    Usuario(nombre_usuario='paciente', nombre_completo='paciente demo', correo='paciente@example.com', telefono='123456789', tipo_usuario='paciente', rut='12345678', dv='9'),
    Usuario(nombre_usuario='doctor', nombre_completo='doctor demo', correo='doctor@example.com', telefono='987654321', tipo_usuario='profesional', rut='87654321', dv='0'),
    Usuario(nombre_usuario='admin', nombre_completo='admin', correo='admin@example.com', telefono='1122334455', tipo_usuario='admin', rut='11223344', dv='1')
]

# Insertar usuarios en la base de datos
with app.app_context():
    for usuario in usuarios:
        usuario.set_password('contraseña123')  # Establecer una contraseña por defecto
        db.session.add(usuario)
    db.session.commit()

print("Usuarios insertados con éxito.")

@app.route('/validar-certificado', methods=['GET', 'POST'])
def validar_certificado():
    if request.method == 'POST':
        codigo = request.form.get('codigo_verificacion')
        try:
            # Enviar el código al servidor del Ministerio de Educación con un User-Agent
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.post(
                'https://certificados.mineduc.cl/certificados-web/mvc/validar/ingresarCodigo',
                data={'codigo_verificacion': codigo},
                headers=headers
            )
            # Manejar la respuesta
            if response.ok:
                return f"Respuesta del servidor: {response.text}"
            else:
                return f"Error al validar el certificado: {response.status_code} - {response.text}", 500
        except requests.exceptions.RequestException as e:
            return f"Error de conexión: {e}", 500
    return render_template('validar_certificado.html')

