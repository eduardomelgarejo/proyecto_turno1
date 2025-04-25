import os

class Config:
    # Clave secreta para la sesión
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    # URI para la base de datos (ajusta los datos reales de conexión)
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/PlataformaSalud'
    
    # Desactiva el seguimiento de modificaciones (ahorra memoria)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de correo para notificaciones o recuperación de contraseña
    MAIL_SERVER = 'smtp.gmail.com' # Servidor de correo
    MAIL_PORT = 587 # Puerto de correo
    MAIL_USE_TLS = True # Usar TLS
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'tu_correo@gmail.com' # Correo de recuperación
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'tu_contraseña_segura' # Contraseña de recuperación
