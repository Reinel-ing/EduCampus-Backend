# Documentación API - Curso

## Endpoints

### Crear Curso

- **POST** `/cursos/`
- Crea un nuevo curso.
- Body:
  - nombre: str
  - cupo_estudiante: int
  - horario: lista (JSON)
  - id_docente: int
  - estado: bool
- Respuesta:
  - id_curso: int
  - nombre: str
  - cupo_estudiante: int
  - horario: lista (JSON)
  - id_docente: int
  - estado: bool

### Listar Cursos

- **GET** `/cursos/`
- Devuelve todos los cursos.
- Respuesta: lista de cursos con todos los campos, incluyendo `id_curso`.

### Obtener Curso por ID

- **GET** `/cursos/{curso_id}`
- Devuelve los datos de un curso específico.
- Respuesta:
  - id_curso: int
  - nombre: str
  - cupo_estudiante: int
  - horario: lista (JSON)
  - id_docente: int
  - estado: bool

### Actualizar Curso

- **PUT** `/cursos/{curso_id}`
- Actualiza los datos de un curso.
- Body: campos editables
- Respuesta: curso actualizado con todos los campos, incluyendo `id_curso`.

### Eliminar Curso

- **DELETE** `/cursos/{curso_id}`
- Elimina un curso.

### Consultar Estudiantes del Curso

- **GET** `/cursos/{curso_id}/estudiantes`
- Devuelve los IDs de los estudiantes inscritos en el curso.
- Respuesta: lista de `id_estudiante`.

### Verificar Cupo

- **GET** `/cursos/{curso_id}/verificar-cupo`
- Devuelve el cupo total, inscritos y cupos disponibles.
- Respuesta:
  - cupo: int
  - inscritos: int
  - disponible: int

### Ver Cursos por Docente

- **GET** `/cursos/por-docente/{docente_id}`
- Devuelve los cursos asignados a un docente.
- Respuesta: lista de cursos con todos los campos, incluyendo `id_curso`.

### Ver Próximas Clases del Docente

- **GET** `/cursos/proximas-clases/{docente_id}`
- Devuelve las clases del docente programadas para el día actual.
- Filtra automáticamente según el día de la semana actual.
- Respuesta:

```json
[
  {
    "id_curso": 1,
    "nombre_curso": "Cálculo I",
    "dia": "Lunes",
    "hora": "08:00-10:00",
    "cupo_estudiante": 30
  }
]
```

### Ver Cursos por Estudiante

- **GET** `/cursos/por-estudiante/{estudiante_id}`
- Devuelve todos los cursos en los que está inscrito un estudiante, incluyendo información del docente.
- Respuesta:

```json
[
  {
    "id_curso": 1,
    "nombre": "Cálculo I",
    "cupo_estudiante": 30,
    "horario": [
      { "dia": "Lunes", "hora": "08:00-10:00" },
      { "dia": "Miércoles", "hora": "08:00-10:00" }
    ],
    "estado": true,
    "docente": {
      "id_docente": 1,
      "nombres": "Carlos",
      "apellidos": "Pérez",
      "correo": "carlos.perez@vortal.edu",
      "especialidad": "Matemáticas"
    }
  }
]
```

### Obtener Horario de Estudiante

- **GET** `/cursos/horario/{estudiante_id}`
- Devuelve todos los horarios de los cursos del estudiante, expandidos por cada sesión.
- Solo incluye cursos activos.
- Respuesta:

```json
[
  {
    "id_curso": 1,
    "nombre_curso": "Cálculo I",
    "dia": "Lunes",
    "hora": "08:00-10:00"
  },
  {
    "id_curso": 1,
    "nombre_curso": "Cálculo I",
    "dia": "Miércoles",
    "hora": "08:00-10:00"
  },
  {
    "id_curso": 2,
    "nombre_curso": "Física General",
    "dia": "Martes",
    "hora": "10:00-12:00"
  }
]
```
