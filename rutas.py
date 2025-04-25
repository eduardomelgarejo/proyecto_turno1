from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from models import db, Usuario,TurnoProfesional, Profesional, FichaPaciente, HistorialAtencion, Box, DisponibilidadBox
from datetime import datetime


# Definimos un blueprint para organizar las rutas
main_bp = Blueprint('main', __name__)

# Ruta de Login
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identificador = request.form['identificador']
        password = request.form['password']

        # Buscar por nombre de usuario o correo
        usuario = Usuario.query.filter(
            (Usuario.nombre_usuario == identificador) | (Usuario.correo == identificador)
        ).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for('main.dashboard'))  # Cambié 'dashboard' para usar el blueprint

        flash("Usuario o contraseña incorrectos.", "danger")  # Mostrar error
        return render_template('login.html')

    return render_template('login.html')


# Ruta de Registro
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        nombre_completo = request.form['nombre_completo']
        correo = request.form['correo']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        tipo_usuario = request.form['tipo_usuario']
        rut = request.form['rut']
        dv = request.form['dv']
        direccion = request.form['direccion']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'warning')
            return redirect(url_for('main.register'))

        # Validar que el nombre de usuario no esté en uso
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El nombre de usuario ya está en uso', 'warning')
            return redirect(url_for('main.register'))

        # Validar que el correo no esté en uso
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo electrónico ya está en uso', 'warning')
            return redirect(url_for('main.register'))

        # Validar que el RUT no esté en uso
        if Usuario.query.filter_by(rut=rut).first():
            flash('El RUT ya está registrado', 'warning')
            return redirect(url_for('main.register'))

        # Crear nuevo usuario
        user = Usuario(
            nombre_usuario=nombre_usuario,
            nombre_completo=nombre_completo,
            correo=correo,
            tipo_usuario=tipo_usuario,
            rut=rut,
            dv=dv,
            direccion=direccion,
            fecha_nacimiento=datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date(),
            telefono=telefono
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Usuario registrado con éxito', 'success')
        return redirect(url_for('main.login'))

    return render_template('registrar_usuario.html')


# Ruta de Dashboard
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.tipo_usuario == 'admin':
        return render_template('panel_admin.html')
    elif current_user.tipo_usuario == 'profesional':
        return render_template('panel_profesional.html')
    elif current_user.tipo_usuario == 'paciente':
        return render_template('panel_paciente.html')
    elif current_user.tipo_usuario == 'ambos':
        return render_template('panel_ambos.html')
    else:
        return "Tipo de usuario no reconocido", 403


# Ruta de Logout
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))  # Cambié 'login' para usar el blueprint


# Ruta Home
@main_bp.route('/')
def home():
    return render_template('Main.html')


# Ruta Main
@main_bp.route('/main')
def main():
    return render_template('Main.html')


# Ruta para gestionar profesionales
@main_bp.route('/gestionar_profesionales')
@login_required
def gestionar_profesionales():
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los profesionales con sus datos de usuario
    profesionales = Profesional.query.join(Usuario).all()
    return render_template('gestionar_profesionales.html', profesionales=profesionales)

@main_bp.route('/gestionar_turnos')
@login_required
def gestionar_turnos():
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los turnos
    turnos = TurnoProfesional.query.all()
    return render_template('gestionar_turnos.html', turnos=turnos)

@main_bp.route('/eliminar_turno/<int:id_turno>', methods=['GET'])
def eliminar_turno(id_turno):
    turno = TurnoProfesional.query.get(id_turno)
    if turno:
        db.session.delete(turno)
        db.session.commit()
    return redirect(url_for('main.gestionar_turnos'))

@main_bp.route('/agendar_turno', methods=['GET', 'POST'])
def agendar_turno():
    if request.method == 'POST':
        id_profesional = request.form['id_usuario']
        fecha = request.form['fecha']
        hora_entrada = request.form['hora_entrada']
        hora_salida = request.form['hora_salida']

        # Crear el nuevo turno
        nuevo_turno = TurnoProfesional(
            id_profesional=id_profesional,
            fecha=fecha,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida
        )
        db.session.add(nuevo_turno)
        db.session.commit()
        return redirect(url_for('main.gestionar_turnos'))

    # Si es un GET, mostramos el formulario
    profesionales = db.session.query(Profesional, Usuario).join(
        Usuario, Profesional.id_usuario == Usuario.id_usuario
    ).all()
    return render_template('agendar_turno.html', profesionales=profesionales)

# Ruta para atender pacientes (panel profesional)
@main_bp.route('/atender_paciente')
@login_required
def atender_paciente():
    # Verificar que el usuario sea profesional
    if current_user.tipo_usuario != 'profesional':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Aquí iría la lógica para mostrar los pacientes a atender
    return render_template('atender_paciente.html')

# Ruta para ver la ficha del paciente
@main_bp.route('/ver_ficha_paciente')
@login_required
def ver_ficha_paciente():
    if current_user.tipo_usuario != 'paciente':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    ficha = FichaPaciente.query.filter_by(id_usuario=current_user.id_usuario).first()
    return render_template('ficha_paciente.html', paciente=current_user, ficha=ficha)

# Ruta para ver el historial de atenciones
@main_bp.route('/historial_atenciones')
@login_required
def historial_atenciones():
    if current_user.tipo_usuario != 'paciente':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    historial = HistorialAtencion.query.filter_by(id_paciente=current_user.id_usuario).all()
    return render_template('historial_atenciones.html', historial=historial)

@main_bp.route('/servicios')
def servicios():
    return render_template('servicios.html')

@main_bp.route('/agendamiento_boxes')
@login_required
def agendamiento_boxes():
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener todos los boxes
    boxes = Box.query.all()
    
    # Obtener profesionales con sus datos de usuario
    profesionales = Profesional.query.join(Usuario).all()
    
    return render_template('agendamiento_boxes.html', boxes=boxes, profesionales=profesionales)

@main_bp.route('/ver_ficha_profesional/<int:id>')
@login_required
def ver_ficha_profesional(id):
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener el profesional y sus datos
    profesional = Profesional.query.get_or_404(id)
    return render_template('ficha_profesional.html', profesional=profesional)

@main_bp.route('/registrar_profesional', methods=['POST'])
@login_required
def registrar_profesional():
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Obtener datos del formulario
        nombre_usuario = request.form['nombre_usuario']
        nombre_completo = request.form['nombre_completo']
        correo = request.form['correo']
        telefono = request.form['telefono']
        contraseña = request.form['contraseña']
        especialidad = request.form['especialidad']
        perfil = request.form['perfil']

        # Verificar si el nombre de usuario ya existe
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            flash('El nombre de usuario ya está en uso', 'warning')
            return redirect(url_for('main.gestionar_profesionales'))

        # Verificar si el correo ya existe
        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo electrónico ya está en uso', 'warning')
            return redirect(url_for('main.gestionar_profesionales'))

        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            nombre_completo=nombre_completo,
            correo=correo,
            telefono=telefono,
            tipo_usuario='profesional'
        )
        nuevo_usuario.set_password(contraseña)
        db.session.add(nuevo_usuario)
        db.session.flush()  # Para obtener el ID del usuario

        # Crear nuevo profesional
        nuevo_profesional = Profesional(
            id_usuario=nuevo_usuario.id_usuario,
            especialidad=especialidad,
            perfil=perfil
        )
        db.session.add(nuevo_profesional)
        db.session.commit()

        flash('¡Profesional registrado exitosamente!', 'success')
        return redirect(url_for('main.gestionar_profesionales'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar el profesional: {str(e)}', 'danger')
        return redirect(url_for('main.gestionar_profesionales'))

@main_bp.route('/editar_profesional/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_profesional(id):
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener el profesional
    profesional = Profesional.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos del usuario
            profesional.usuario.nombre_completo = request.form['nombre_completo']
            profesional.usuario.correo = request.form['correo']
            profesional.usuario.telefono = request.form['telefono']
            
            # Actualizar datos del profesional
            profesional.especialidad = request.form['especialidad']
            profesional.perfil = request.form['perfil']
            
            # Si se proporcionó una nueva contraseña, actualizarla
            if request.form.get('contraseña'):
                profesional.usuario.set_password(request.form['contraseña'])
            
            db.session.commit()
            flash('Profesional actualizado exitosamente', 'success')
            return redirect(url_for('main.gestionar_profesionales'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el profesional: {str(e)}', 'danger')
            return redirect(url_for('main.gestionar_profesionales'))
    
    return render_template('editar_profesional.html', profesional=profesional)

@main_bp.route('/eliminar_profesional/<int:id>', methods=['POST'])
@login_required
def eliminar_profesional(id):
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
    
    try:
        # Obtener el profesional
        profesional = Profesional.query.get_or_404(id)
        
        # Obtener el usuario asociado
        usuario = profesional.usuario
        
        # Eliminar el profesional
        db.session.delete(profesional)
        
        # Eliminar el usuario
        db.session.delete(usuario)
        
        # Guardar los cambios
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profesional eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar el profesional: {str(e)}'})

@main_bp.route('/agendar_box', methods=['POST'])
@login_required
def agendar_box():
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
    
    try:
        # Obtener datos del agendamiento
        data = request.get_json()
        box_id = data.get('box_id')
        fecha = data.get('fecha')
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        profesional_id = data.get('profesional_id')

        # Verificar que todos los campos necesarios estén presentes
        if not all([box_id, fecha, hora_inicio, hora_fin, profesional_id]):
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'})

        # Verificar si el box está disponible en ese horario
        disponibilidad_existente = DisponibilidadBox.query.filter_by(
            id_box=box_id,
            fecha=fecha
        ).filter(
            (DisponibilidadBox.hora_inicio <= hora_inicio) & (DisponibilidadBox.hora_fin >= hora_inicio) |
            (DisponibilidadBox.hora_inicio <= hora_fin) & (DisponibilidadBox.hora_fin >= hora_fin)
        ).first()

        if disponibilidad_existente:
            return jsonify({'success': False, 'message': 'El box ya está ocupado en ese horario'})

        # Crear nuevo agendamiento
        nuevo_agendamiento = DisponibilidadBox(
            id_box=box_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
        db.session.add(nuevo_agendamiento)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Agendamiento realizado con éxito'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al realizar el agendamiento: {str(e)}'})

@main_bp.route('/crear_boxes', methods=['POST'])
@login_required
def crear_boxes():
    # Verificar que el usuario sea administrador
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
    
    try:
        # Crear 5 boxes de ejemplo
        boxes = [
            Box(
                tipo_box='Consulta General',
                capacidad=1,
                equipamiento='Mesa de examen, Silla, Computador',
                disponible=True
            ),
            Box(
                tipo_box='Procedimientos',
                capacidad=2,
                equipamiento='Mesa de procedimientos, Equipamiento médico, Monitor',
                disponible=True
            ),
            Box(
                tipo_box='Urgencias',
                capacidad=3,
                equipamiento='Cama de emergencia, Equipamiento de reanimación, Monitor',
                disponible=True
            ),
            Box(
                tipo_box='Consulta Especializada',
                capacidad=1,
                equipamiento='Mesa de examen, Equipamiento especializado',
                disponible=True
            ),
            Box(
                tipo_box='Procedimientos Menores',
                capacidad=2,
                equipamiento='Mesa de procedimientos, Equipamiento básico',
                disponible=True
            )
        ]
        
        # Agregar los boxes a la base de datos
        for box in boxes:
            db.session.add(box)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Boxes creados exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al crear los boxes: {str(e)}'})

@main_bp.route('/chat_profesional')
@login_required
def chat_profesional():
    return render_template('chat_profesional.html')




