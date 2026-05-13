# Documentación API - Autenticación

## Endpoints

### Iniciar Sesión

- **POST** `/auth/login`
- Permite el inicio de sesión para docentes y estudiantes.
- El sistema busca primero en la tabla de docentes, luego en estudiantes.
- Asigna automáticamente el rol correspondiente.

**Body:**

```json
{
  "correo": "usuario@ejemplo.com",
  "contraseña": "password123"
}
```

**Respuesta Exitosa (Docente):**

```json
{
  "id": 1,
  "nombres": "Carlos",
  "apellidos": "Pérez",
  "correo": "carlos.perez@vortal.edu",
  "rol": "docente",
  "especialidad": "Matemáticas",
  "telefono": null,
  "estado": true
}
```

**Respuesta Exitosa (Estudiante):**

```json
{
  "id": 1,
  "nombres": "Ana",
  "apellidos": "Martínez",
  "correo": "ana.martinez@estudiante.edu",
  "rol": "estudiante",
  "especialidad": null,
  "telefono": "0991234567",
  "estado": true
}
```

**Respuesta Error (401 Unauthorized):**

```json
{
  "detail": "Credenciales incorrectas"
}
```

---

# Documentación API - Reportes

## Endpoints

### Reporte de Asistencia General

- **GET** `/reportes/asistencia-general`
- Devuelve estadísticas generales de asistencia.

**Respuesta:**

```json
{
  "porcentaje_asistencia": 85.5,
  "total_estudiantes": 120,
  "total_cursos": 15,
  "total_registros": 450
}
```

### Reporte de Rendimiento Académico

- **GET** `/reportes/rendimiento-academico`
- Devuelve estadísticas de rendimiento académico.

**Respuesta:**

```json
{
  "promedio_general": 78.5,
  "alto_rendimiento": 45,
  "requieren_apoyo": 12,
  "tasa_aprobacion": 85.5
}
```

### Reporte de Usuarios Activos

- **GET** `/reportes/usuarios-activos`
- Devuelve estadísticas de usuarios activos en el sistema.

**Respuesta:**

```json
{
  "usuarios_activos": 128,
  "total_estudiantes": 120,
  "total_docentes": 8,
  "nuevos_usuarios": 15
}
```

### Reporte Completo

- **GET** `/reportes/completo`
- Devuelve todos los reportes en una sola respuesta.

**Respuesta:**

```json
{
  "asistencia_general": {
    "porcentaje_asistencia": 85.5,
    "total_estudiantes": 120,
    "total_cursos": 15,
    "total_registros": 450
  },
  "rendimiento_academico": {
    "promedio_general": 78.5,
    "alto_rendimiento": 45,
    "requieren_apoyo": 12,
    "tasa_aprobacion": 85.5
  },
  "usuarios_activos": {
    "usuarios_activos": 128,
    "total_estudiantes": 120,
    "total_docentes": 8,
    "nuevos_usuarios": 15
  }
}
```
