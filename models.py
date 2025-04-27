from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime

# Inicializar la base de datos
db = SQLAlchemy()   

class Usuario(UserMixin, db.Model): # Modelo de usuario
    __tablename__ = 'Usuarios' # Nombre de la tabla
    id_usuario = db.Column(db.Integer, primary_key=True) # ID del usuario
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False) # Nombre de usuario
    contraseña = db.Column(db.String(255), nullable=False) # Contraseña
    nombre_completo = db.Column(db.String(100)) # Nombre completo
    correo = db.Column(db.String(100)) # Correo
    telefono = db.Column(db.String(20)) # Teléfono
    direccion = db.Column(db.Text) # Dirección
    fecha_nacimiento = db.Column(db.Date) # Fecha de nacimiento
    rut = db.Column(db.String(10), unique=True)  # Campo para el RUT sin guion
    dv = db.Column(db.String(1))  # Campo para el dígito verificador
    tipo_usuario = db.Column(db.Enum('paciente', 'profesional', 'ambos', 'admin'), nullable=False) # Tipo de usuario

    # Método para establecer la contraseña
    def set_password(self, password):
        self.contraseña = generate_password_hash(password)

    # Método para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.contraseña, password)

    # Requerido por Flask-Login
    def get_id(self):
        return str(self.id_usuario)

    # Estos ya los provee UserMixin, pero si quieres sobreescribirlos:
    def is_active(self):
        return True

    # Requerido por Flask-Login
    def is_authenticated(self):
        return True



# Modelo de profesional
class Profesional(db.Model):
    __tablename__ = 'Profesionales' # Nombre de la tabla
    id_profesional = db.Column(db.Integer, primary_key=True) # ID del profesional
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario'), unique=True) # ID del usuario
    especialidad = db.Column(db.String(100)) # Especialidad
    perfil = db.Column(db.Text) # Perfil
    certificacion = db.Column(db.String(255)) # Certificación del médico
    
    # Relación con el modelo Usuario
    usuario = db.relationship('Usuario', backref=db.backref('profesional', uselist=False))

# Modelo de ficha de paciente
class FichaPaciente(db.Model):
    __tablename__ = 'FichaPaciente' # Nombre de la tabla
    id_ficha = db.Column(db.Integer, primary_key=True) # ID de la ficha
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario'), unique=True) # ID del usuario
    rut = db.Column(db.String(12), unique=True) # Rut
    antecedentes_medicos = db.Column(db.Text) # Antecedentes médicos
    alergias = db.Column(db.Text) # Alergias
    medicamentos_actuales = db.Column(db.Text) # Medicamentos actuales
    observaciones = db.Column(db.Text) # Observaciones
    fecha_creacion = db.Column(db.Date) # Fecha de creación

# Modelo de turno de profesional
class TurnoProfesional(db.Model):
    __tablename__ = 'TurnosProfesionales' # Nombre de la tabla
    id_turno = db.Column(db.Integer, primary_key=True) # ID del turno
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del usuario
    fecha = db.Column(db.Date) # Fecha
    hora_entrada = db.Column(db.Time) # Hora de entrada
    hora_salida = db.Column(db.Time) # Hora de salida
    
    # Relación con el modelo Usuario
    usuario = db.relationship('Usuario', backref=db.backref('turnos', lazy='dynamic'))

class SolicitudCambioTurno(db.Model):
    __tablename__ = 'SolicitudCambioTurno' # Nombre de la tabla
    id_solicitud = db.Column(db.Integer, primary_key=True) # ID de la solicitud
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del usuario
    motivo = db.Column(db.Text) # Motivo
    fecha_solicitud = db.Column(db.DateTime) # Fecha de solicitud
    estado = db.Column(db.String(20)) # Estado

class HistorialAtencion(db.Model):
    __tablename__ = 'HistorialAtenciones' # Nombre de la tabla
    id_atencion = db.Column(db.Integer, primary_key=True) # ID de la atención
    id_paciente = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del paciente
    id_profesional = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del profesional
    fecha = db.Column(db.Date) # Fecha
    motivo = db.Column(db.Text) # Motivo
    diagnostico = db.Column(db.Text) # Diagnóstico
    tratamiento = db.Column(db.Text) # Tratamiento

class AlertaReserva(db.Model):
    __tablename__ = 'AlertasReserva' # Nombre de la tabla
    id_alerta = db.Column(db.Integer, primary_key=True) # ID de la alerta
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del usuario
    tipo_alerta = db.Column(db.String(50)) # Tipo de alerta
    mensaje = db.Column(db.Text) # Mensaje
    fecha = db.Column(db.DateTime) # Fecha

class Chat(db.Model):
    __tablename__ = 'Chat' # Nombre de la tabla
    id_chat = db.Column(db.Integer, primary_key=True) # ID del chat
    id_emisor = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del emisor
    id_receptor = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del receptor
    mensaje = db.Column(db.Text) # Mensaje
    fecha_envio = db.Column(db.DateTime)

class Box(db.Model):
    __tablename__ = 'Boxes' # Nombre de la tabla
    id_box = db.Column(db.Integer, primary_key=True) # ID del box
    tipo_box = db.Column(db.String(100)) # Tipo de box
    capacidad = db.Column(db.Integer) # Capacidad
    equipamiento = db.Column(db.Text) # Equipamiento
    disponible = db.Column(db.Boolean) # Disponible
    id_profesional = db.Column(db.Integer, db.ForeignKey('Profesionales.id_profesional'))

class DisponibilidadBox(db.Model):
    __tablename__ = 'DisponibilidadBox' # Nombre de la tabla
    id_disponibilidad = db.Column(db.Integer, primary_key=True) # ID de la disponibilidad
    id_box = db.Column(db.Integer, db.ForeignKey('Boxes.id_box')) # ID del box
    fecha = db.Column(db.Date) # Fecha
    hora_inicio = db.Column(db.Time) # Hora de inicio
    hora_fin = db.Column(db.Time) # Hora de fin

class CentroAyuda(db.Model):
    __tablename__ = 'CentroAyuda' # Nombre de la tabla
    id_ayuda = db.Column(db.Integer, primary_key=True) # ID de la ayuda
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del usuario
    tipo_solicitud = db.Column(db.String(50)) # Tipo de solicitud
    mensaje = db.Column(db.Text) # Mensaje
    fecha = db.Column(db.DateTime) # Fecha
    estado = db.Column(db.String(20)) # Estado

class Reserva(db.Model):
    __tablename__ = 'Reservas' # Nombre de la tabla
    id_reserva = db.Column(db.Integer, primary_key=True) # ID de la reserva
    id_paciente = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del paciente
    id_profesional = db.Column(db.Integer, db.ForeignKey('Usuarios.id_usuario')) # ID del profesional
    fecha = db.Column(db.Date) # Fecha
    hora = db.Column(db.Time) # Hora
    estado = db.Column(db.String(20)) # Estado

