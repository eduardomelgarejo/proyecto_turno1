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

### 🩺 Panel Profesional
- [ ] Agregar rutas a los dos primeros botones del panel.


## 📈 Escalabilidad (Futuras mejoras)

- [ ] Validar la certificación del médico.
    (pagina web para verificar certificado https://certificados.mineduc.cl/certificados-web/mvc/validar/ingresarCodigo)
- [ ] Asistente virtual integrado.
- [ ] Recordatorio de citas:
- [ ] Envío de mensajes a correo o WhatsApp (Twilio para Whatsapp y Flask_Mail para Correo).
