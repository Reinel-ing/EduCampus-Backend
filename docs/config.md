# Documentación API - Configuración

## Endpoints

### Crear Configuración

- **POST** `/configuracion/`
- Crea la configuración del sistema.
- Body:
  - nombre_institucion: str
  - email_contacto: str
  - ano_academico: str
- Respuesta:
  - id: int
  - nombre_institucion: str
  - email_contacto: str
  - ano_academico: str

### Obtener Configuración

- **GET** `/configuracion/`
- Devuelve la configuración actual.
- Respuesta: todos los campos de configuración.

### Actualizar Configuración

- **PUT** `/configuracion/`
- Actualiza la configuración.
- Body: campos editables
- Respuesta: configuración actualizada.
