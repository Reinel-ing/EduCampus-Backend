# Documentación API - Asistencia

## Endpoints

### Registrar Asistencia

- **POST** `/asistencia/`
- Registra la asistencia de un estudiante en un curso para una fecha específica.
- Valida que no exista asistencia duplicada para el mismo día.
- Body:
  - id_estudiante: int
  - id_curso: int
  - fecha: date (formato: "YYYY-MM-DD")
  - estado: bool (true = presente, false = ausente)
- Respuesta:
  - id_asistencia: int
  - id_estudiante: int
  - id_curso: int
  - fecha: date
  - estado: bool

### Editar Asistencia

- **PUT** `/asistencia/{asistencia_id}`
- Actualiza el estado de asistencia.
- Body:
  - estado: bool (opcional)
- Respuesta: asistencia actualizada con todos los campos.

### Asistencia por Estudiante

- **GET** `/asistencia/por-estudiante/{estudiante_id}`
- Devuelve todos los registros de asistencia de un estudiante.
- Respuesta: lista de asistencias con todos los campos.

### Asistencia por Curso

- **GET** `/asistencia/por-curso/{curso_id}`
- Devuelve todos los registros de asistencia de un curso.
- Respuesta: lista de asistencias con todos los campos.

### Porcentaje de Asistencia

- **GET** `/asistencia/porcentaje-estudiante/{estudiante_id}/{curso_id}`
- Calcula el porcentaje de asistencia de un estudiante en un curso específico.
- Respuesta:

```json
{
  "porcentaje": 85.5
}
```
