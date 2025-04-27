# PROYECTO NEXTFLOW

Plataforma web de gestión médica desarrollada en Flask. Este sistema permite agendamiento de turnos, manejo de fichas médicas, atención profesional y administración de boxes médicos.

## 🚧 Funcionalidades Pendientes

### 🔄 Pacientes
- [ ] Cambio de turno del paciente.
- [ ] Visualización y actualización de los turnos del paciente.
- [ ] Historial de atención:
  - [ ] Verificar si funciona correctamente.
  - [ ] Que sea escalable y se pueda descargar en PDF (WeasyPrint).
- [ ] Alerta de reserva o cambio de hora. 

### 🛠️ Panel de Administración
- [ ] Validación del calendario:
  - [ ] Asegurar que no existan topones entre horarios.
- [ ] Ingreso y registro de boxes médicos.

### 🩺 Panel Profesional
- [ ] Agregar rutas a los dos primeros botones del panel.


### 🔐 Seguridad
- [ ] Implementar token de sesión utilizando `Flask-Session`.
- [ ] (realizado pero con dudad)

---

## 📈 Escalabilidad (Futuras mejoras)

- [ ] Validar la certificación del médico.
- [ ] Asistente virtual integrado.
- [ ] Recordatorio de citas:
- [ ] Envío de mensajes a correo o WhatsApp (Twilio para Whatsapp y Flask_Mail para Correo).
