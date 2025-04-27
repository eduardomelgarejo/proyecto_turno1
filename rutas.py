from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, Flask
from flask_login import login_user, login_required, logout_user, current_user
from models import db, Usuario,TurnoProfesional, Profesional, FichaPaciente, HistorialAtencion, Box, DisponibilidadBox, Reserva, Chat
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit
from flask import get_flashed_messages
from flask_socketio import join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app)

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
            return redirect(url_for('main.dashboard'))

        # Si las credenciales son incorrectas, mostrar mensaje de error
        flash('Usuario o contraseña incorrectos', 'error')
        return redirect(url_for('main.login'))

    # Limpiar mensajes flash anteriores
    get_flashed_messages()
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
    if not current_user.is_authenticated:
        flash('Por favor inicie sesión para acceder a esta página', 'error')
        return redirect(url_for('main.login'))

    if current_user.tipo_usuario == 'admin':
        return render_template('panel_admin.html')
    elif current_user.tipo_usuario == 'profesional':
        return render_template('panel_profesional.html')
    elif current_user.tipo_usuario == 'paciente':
        return render_template('panel_paciente.html')
    elif current_user.tipo_usuario == 'ambos':
        return render_template('panel_ambos.html')
    else:
        flash('Tipo de usuario no reconocido', 'error')
        return redirect(url_for('main.login'))


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
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Obtener todos los turnos con información del profesional
        turnos = db.session.query(TurnoProfesional, Profesional, Usuario).join(
            Usuario, TurnoProfesional.id_usuario == Usuario.id_usuario
        ).join(
            Profesional, Usuario.id_usuario == Profesional.id_usuario
        ).order_by(TurnoProfesional.fecha.desc(), TurnoProfesional.hora_entrada.asc()).all()
        
        print(f"Turnos encontrados: {len(turnos)}")  # Debug
        for turno, prof, user in turnos:
            print(f"Turno: {turno.id_turno}, Profesional: {user.nombre_completo}, Fecha: {turno.fecha}")  # Debug
        
        return render_template('gestionar_turnos.html', turnos=turnos)
    except Exception as e:
        print(f"Error al obtener turnos: {str(e)}")  # Debug
        flash(f'Error al obtener los turnos: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/eliminar_turno/<int:id_turno>', methods=['GET'])
def eliminar_turno(id_turno):
    turno = TurnoProfesional.query.get(id_turno)
    if turno:
        db.session.delete(turno)
        db.session.commit()
    return redirect(url_for('main.gestionar_turnos'))

@main_bp.route('/agendar_turno', methods=['GET', 'POST'])
@login_required
def agendar_turno():
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            id_usuario = request.form['id_usuario']
            fecha = request.form['fecha']
            hora_entrada = request.form['hora_entrada']
            hora_salida = request.form['hora_salida']

            print(f"Datos recibidos: id_usuario={id_usuario}, fecha={fecha}, hora_entrada={hora_entrada}, hora_salida={hora_salida}")  # Debug

            # Convertir la fecha y horas a objetos datetime
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            hora_entrada_obj = datetime.strptime(hora_entrada, '%H:%M').time()
            hora_salida_obj = datetime.strptime(hora_salida, '%H:%M').time()

            # Validar que no haya conflictos de horarios
            conflicto = TurnoProfesional.query.filter_by(
                fecha=fecha_obj,
                id_usuario=id_usuario
            ).filter(
                (TurnoProfesional.hora_entrada <= hora_salida_obj) & 
                (TurnoProfesional.hora_salida >= hora_entrada_obj)
            ).first()

            if conflicto:
                flash('El horario seleccionado ya está ocupado', 'error')
                return redirect(url_for('main.agendar_turno'))

            # Crear el nuevo turno
            nuevo_turno = TurnoProfesional(
                id_usuario=id_usuario,
                fecha=fecha_obj,
                hora_entrada=hora_entrada_obj,
                hora_salida=hora_salida_obj
            )

            print(f"Creando turno: {nuevo_turno.__dict__}")  # Debug

            db.session.add(nuevo_turno)
            db.session.commit()

            print("Turno guardado exitosamente")  # Debug

            flash('Turno agendado exitosamente', 'success')
            return redirect(url_for('main.gestionar_turnos'))

        except Exception as e:
            db.session.rollback()
            print(f"Error al agendar turno: {str(e)}")  # Debug
            flash(f'Error al agendar el turno: {str(e)}', 'error')
            return redirect(url_for('main.agendar_turno'))

    # Si es un GET, mostramos el formulario
    profesionales = db.session.query(Profesional, Usuario).join(
        Usuario, Profesional.id_usuario == Usuario.id_usuario
    ).all()
    return render_template('agendar_turno.html', profesionales=profesionales, hoy=datetime.now().strftime('%Y-%m-%d'))

# Ruta para atender pacientes (panel profesional)
@main_bp.route('/atender_paciente')
@login_required
def atender_paciente():
    if current_user.tipo_usuario != 'profesional':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    fecha = request.args.get('fecha')
    estado = request.args.get('estado')
    
    # Obtener el profesional asociado al usuario actual
    profesional = Profesional.query.filter_by(id_usuario=current_user.id_usuario).first()
    if not profesional:
        flash('No se encontró el perfil profesional', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Consulta base para las reservas del profesional
    query = Reserva.query.filter_by(id_profesional=profesional.id_profesional)
    
    # Aplicar filtros si se proporcionan
    if fecha:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        query = query.filter_by(fecha=fecha_obj)
    if estado:
        query = query.filter_by(estado=estado)
    
    # Obtener las reservas
    reservas = query.order_by(Reserva.fecha, Reserva.hora).all()
    
    # Preparar los datos para la plantilla
    citas = []
    for reserva in reservas:
        paciente = Usuario.query.get(reserva.id_paciente)
        if paciente:
            citas.append({
                'id': reserva.id_reserva,
                'paciente': paciente.nombre_completo,
                'fecha': reserva.fecha,
                'hora': reserva.hora,
                'estado': reserva.estado,
                'motivo': getattr(reserva, 'motivo_consulta', 'No especificado')
            })
    
    return render_template('atender_paciente.html', citas=citas, fecha_hoy=datetime.now())

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

@main_bp.route('/descargar_historial_pdf')
@login_required
def descargar_historial_pdf():
    if current_user.tipo_usuario != 'paciente':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))

    historial = HistorialAtencion.query.filter_by(id_paciente=current_user.id_usuario).all()

    # Generar PDF
    from flask import make_response
    from io import BytesIO
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 750, "Historial de Atenciones")
    y = 720
    for atencion in historial:
        p.drawString(100, y, f"Fecha: {atencion.fecha}, Detalle: {atencion.detalle}")
        y -= 20

    p.showPage()
    p.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=historial_atenciones.pdf'

    return response

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
        return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
    
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
            return jsonify({'success': False, 'message': 'El nombre de usuario ya está en uso'})

        # Verificar si el correo ya existe
        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({'success': False, 'message': 'El correo electrónico ya está en uso'})

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

        return jsonify({'success': True, 'message': '¡Profesional registrado exitosamente!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al registrar el profesional: {str(e)}'})

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

@main_bp.route('/obtener_eventos_box/<int:box_id>')
@login_required
def obtener_eventos_box(box_id):
    try:
        # Obtener todos los agendamientos del box
        agendamientos = DisponibilidadBox.query.filter_by(id_box=box_id).all()
        
        eventos = []
        for agendamiento in agendamientos:
            # Obtener el profesional asociado
            profesional = Profesional.query.filter_by(id_usuario=agendamiento.id_profesional).first()
            if profesional:
                eventos.append({
                    'fecha': agendamiento.fecha.strftime('%Y-%m-%d'),
                    'hora_inicio': agendamiento.hora_inicio.strftime('%H:%M'),
                    'hora_fin': agendamiento.hora_fin.strftime('%H:%M'),
                    'box_id': agendamiento.id_box,
                    'profesional_id': agendamiento.id_profesional,
                    'profesional_nombre': profesional.usuario.nombre_completo,
                    'estado': 'ocupado'
                })
        
        return jsonify({'success': True, 'eventos': eventos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/agendar_box', methods=['POST'])
@login_required
def agendar_box():
    if current_user.tipo_usuario != 'admin':
        return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
    
    try:
        # Obtener datos del agendamiento
        data = request.get_json()
        box_id = data.get('box_id')
        fecha = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data.get('hora_inicio'), '%H:%M').time()
        hora_fin = datetime.strptime(data.get('hora_fin'), '%H:%M').time()
        profesional_id = data.get('profesional_id')

        # Verificar que todos los campos necesarios estén presentes
        if not all([box_id, fecha, hora_inicio, hora_fin, profesional_id]):
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'})

        # Verificar si el box está disponible en ese horario
        conflicto = DisponibilidadBox.query.filter_by(
            id_box=box_id,
            fecha=fecha
        ).filter(
            (DisponibilidadBox.hora_inicio <= hora_inicio) & (DisponibilidadBox.hora_fin >= hora_inicio) |
            (DisponibilidadBox.hora_inicio <= hora_fin) & (DisponibilidadBox.hora_fin >= hora_fin) |
            (DisponibilidadBox.hora_inicio >= hora_inicio) & (DisponibilidadBox.hora_fin <= hora_fin)
        ).first()

        if conflicto:
            return jsonify({'success': False, 'message': 'El box ya está ocupado en ese horario'})

        # Crear nuevo agendamiento
        nuevo_agendamiento = DisponibilidadBox(
            id_box=box_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            id_profesional=profesional_id
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

@main_bp.route('/chat_paciente')
@login_required
def chat_paciente():
    if current_user.tipo_usuario not in ['paciente', 'ambos']:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener lista de profesionales
    profesionales = Profesional.query.join(Usuario).all()
    return render_template('chat_paciente.html', profesionales=profesionales)

@main_bp.route('/chat_profesional')
@login_required
def chat_profesional():
    if current_user.tipo_usuario not in ['profesional', 'ambos']:
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener lista de pacientes
    pacientes = Usuario.query.filter_by(tipo_usuario='paciente').all()
    return render_template('chat_profesional.html', pacientes=pacientes)

@main_bp.route('/chat/mensajes/<int:usuario_id>')
@login_required
def obtener_mensajes(usuario_id):
    # Obtener mensajes entre el usuario actual y el usuario especificado
    mensajes = Chat.query.filter(
        ((Chat.id_emisor == current_user.id_usuario) & (Chat.id_receptor == usuario_id)) |
        ((Chat.id_emisor == usuario_id) & (Chat.id_receptor == current_user.id_usuario))
    ).order_by(Chat.fecha_envio.asc()).all()
    
    return jsonify([{
        'id': msg.id_chat,
        'contenido': msg.mensaje,
        'fecha_hora': msg.fecha_envio.strftime('%Y-%m-%d %H:%M:%S'),
        'id_remitente': msg.id_emisor
    } for msg in mensajes])

@main_bp.route('/chat/enviar', methods=['POST'])
@login_required
def enviar_mensaje():
    data = request.get_json()
    nuevo_mensaje = Chat(
        id_emisor=current_user.id_usuario,
        id_receptor=data['id_destinatario'],
        mensaje=data['contenido'],
        fecha_envio=datetime.now()
    )
    db.session.add(nuevo_mensaje)
    db.session.commit()
    
    # Emitir el mensaje a través de Socket.IO
    socketio.emit('receive_message', {
        'message': data['contenido'],
        'sender': 'profesional' if current_user.tipo_usuario == 'profesional' else 'paciente',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, room=f"chat_{data['id_destinatario']}")
    
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f"chat_{current_user.id_usuario}")

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f"chat_{current_user.id_usuario}")

@socketio.on('send_message')
def handle_send_message(data):
    if not current_user.is_authenticated:
        return
    
    nuevo_mensaje = Chat(
        id_emisor=current_user.id_usuario,
        id_receptor=data['profesional_id'],
        mensaje=data['message'],
        fecha_envio=datetime.now()
    )
    db.session.add(nuevo_mensaje)
    db.session.commit()
    
    emit('receive_message', {
        'message': data['message'],
        'sender': 'profesional' if current_user.tipo_usuario == 'profesional' else 'paciente',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, room=f"chat_{data['profesional_id']}")

@main_bp.route('/cambiar_turno/<int:id_turno>', methods=['GET', 'POST'])
@login_required
def cambiar_turno(id_turno):
    # Verificar que el usuario sea paciente
    if current_user.tipo_usuario != 'paciente':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))

    turno = TurnoProfesional.query.get(id_turno)
    if not turno:
        flash('Turno no encontrado', 'warning')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        nueva_fecha = request.form['fecha']
        nueva_hora_entrada = request.form['hora_entrada']
        nueva_hora_salida = request.form['hora_salida']

        # Validar que no haya conflictos de horarios
        conflicto = TurnoProfesional.query.filter_by(fecha=nueva_fecha, hora_entrada=nueva_hora_entrada).first()
        if conflicto:
            flash('El horario seleccionado ya está ocupado', 'warning')
            return redirect(url_for('main.cambiar_turno', id_turno=id_turno))

        # Actualizar el turno
        turno.fecha = nueva_fecha
        turno.hora_entrada = nueva_hora_entrada
        turno.hora_salida = nueva_hora_salida
        db.session.commit()
        flash('Turno actualizado con éxito', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('cambiar_turno.html', turno=turno)

@main_bp.route('/descargar_ficha_paciente_pdf/<int:id_paciente>')
@login_required
def descargar_ficha_paciente_pdf(id_paciente):
    # Verificar que el usuario sea paciente
    if current_user.tipo_usuario != 'paciente':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener el paciente y su ficha
    paciente = Usuario.query.get_or_404(id_paciente)
    ficha = FichaPaciente.query.filter_by(id_usuario=id_paciente).first()

    # Generar PDF
    from flask import make_response
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.units import inch
    import os

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []

    # Estilo personalizado para títulos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )

    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db')
    )

    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )

    # Agregar logo
    logo_path = os.path.join('static', 'images', 'NextFlow_Logo_Titulo-preview.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5*inch, height=0.75*inch)
        story.append(img)
        story.append(Spacer(1, 20))

    # Título principal
    story.append(Paragraph("Ficha del Paciente", title_style))
    story.append(Spacer(1, 20))

    # Información Personal
    story.append(Paragraph("Información Personal", subtitle_style))
    
    # Crear tabla para información personal
    personal_data = [
        ["RUT:", f"{paciente.rut}-{paciente.dv}"],
        ["Nombre:", paciente.nombre_completo],
        ["Correo:", paciente.correo],
        ["Teléfono:", paciente.telefono],
        ["Dirección:", paciente.direccion],
        ["Fecha de Nacimiento:", paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'No especificada']
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))

    # Información Médica
    story.append(Paragraph("Información Médica", subtitle_style))
    
    # Crear tabla para información médica
    medical_data = [
        ["Antecedentes Médicos:", ficha.antecedentes_medicos if ficha else 'No registrado'],
        ["Alergias:", ficha.alergias if ficha else 'No registrado'],
        ["Medicamentos Actuales:", ficha.medicamentos_actuales if ficha else 'No registrado'],
        ["Observaciones:", ficha.observaciones if ficha else 'No registrado']
    ]
    
    medical_table = Table(medical_data, colWidths=[2*inch, 4*inch])
    medical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
    ]))
    
    story.append(medical_table)
    story.append(Spacer(1, 20))

    # Pie de página
    story.append(Paragraph("Este documento fue generado automáticamente por el sistema NextFlow", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.gray)))
    story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.gray)))

    # Construir el PDF
    doc.build(story)

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=ficha_paciente_{id_paciente}.pdf'

    return response

@main_bp.route('/descargar_perfil_medico_pdf/<int:id_profesional>')
@login_required
def descargar_perfil_medico_pdf(id_profesional):
    if current_user.tipo_usuario != 'admin':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))

    profesional = Profesional.query.get_or_404(id_profesional)

    # Generar PDF
    from flask import make_response
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.units import inch
    import os

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []

    # Estilo personalizado para títulos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )

    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db')
    )

    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )

    # Agregar logo
    logo_path = os.path.join('static', 'images', 'NextFlow_Logo_Titulo-preview.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=1.5*inch, height=0.75*inch)
        story.append(img)
        story.append(Spacer(1, 20))

    # Título principal
    story.append(Paragraph("Perfil del Profesional", title_style))
    story.append(Spacer(1, 20))

    # Información Personal
    story.append(Paragraph("Información Personal", subtitle_style))
    
    # Crear tabla para información personal
    personal_data = [
        ["Nombre:", profesional.usuario.nombre_completo],
        ["Correo:", profesional.usuario.correo],
        ["Teléfono:", profesional.usuario.telefono],
        ["Especialidad:", profesional.especialidad]
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))

    # Información Profesional
    story.append(Paragraph("Información Profesional", subtitle_style))
    
    # Crear tabla para información profesional
    professional_data = [
        ["Perfil:", profesional.perfil],
        ["Certificación:", profesional.certificacion if profesional.certificacion else 'No especificada']
    ]
    
    professional_table = Table(professional_data, colWidths=[2*inch, 4*inch])
    professional_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
    ]))
    
    story.append(professional_table)
    story.append(Spacer(1, 20))

    # Pie de página
    story.append(Paragraph("Este documento fue generado automáticamente por el sistema NextFlow", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.gray)))
    story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, textColor=colors.gray)))

    # Construir el PDF
    doc.build(story)

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=perfil_medico_{id_profesional}.pdf'

    return response

@main_bp.route('/agendar_cita_paciente')
@login_required
def agendar_cita_paciente():
    if current_user.tipo_usuario != 'paciente':
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Obtener profesionales con sus datos de usuario
    profesionales = Profesional.query.join(Usuario).all()
    
    # Obtener la fecha mínima (mañana)
    fecha_minima = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('agendar_cita_paciente.html', 
                         profesionales=profesionales,
                         fecha_minima=fecha_minima)

@main_bp.route('/obtener_horas_disponibles/<int:profesional_id>/<fecha>')
@login_required
def obtener_horas_disponibles(profesional_id, fecha):
    try:
        # Obtener las horas ocupadas del profesional en la fecha especificada
        citas_ocupadas = Reserva.query.filter_by(
            id_profesional=profesional_id,
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date()
        ).all()

        # Horas disponibles (de 9:00 a 18:00)
        horas_disponibles = []
        hora_inicio = datetime.strptime('09:00', '%H:%M')
        hora_fin = datetime.strptime('18:00', '%H:%M')
        
        while hora_inicio < hora_fin:
            hora_str = hora_inicio.strftime('%H:%M')
            # Verificar si la hora está ocupada
            if not any(cita.hora.strftime('%H:%M') == hora_str for cita in citas_ocupadas):
                horas_disponibles.append(hora_str)
            hora_inicio += timedelta(minutes=30)  # Intervalos de 30 minutos

        return jsonify({'success': True, 'horas': horas_disponibles})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/agendar_cita', methods=['POST'])
@login_required
def agendar_cita():
    if current_user.tipo_usuario != 'paciente':
        return jsonify({'success': False, 'message': 'No tienes permisos para realizar esta acción'})
    
    try:
        data = request.get_json()
        profesional_id = data.get('profesional_id')
        fecha = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
        hora = datetime.strptime(data.get('hora'), '%H:%M').time()
        motivo = data.get('motivo')

        # Verificar si ya existe una cita en ese horario
        cita_existente = Reserva.query.filter_by(
            id_profesional=profesional_id,
            fecha=fecha,
            hora=hora
        ).first()

        if cita_existente:
            return jsonify({'success': False, 'message': 'El horario seleccionado ya está ocupado'})

        # Crear nueva reserva
        nueva_reserva = Reserva(
            id_paciente=current_user.id_usuario,
            id_profesional=profesional_id,
            fecha=fecha,
            hora=hora,
            estado='pendiente',
            motivo_consulta=motivo
        )

        db.session.add(nueva_reserva)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Cita agendada con éxito'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al agendar la cita: {str(e)}'})




