# Documentación API - Docente

## Endpoints

### Crear Docente

- **POST** `/docentes/`
- Crea un nuevo docente.
- Body:
  - nombres: str
  - apellidos: str
  - cedula: str
  - correo: str
  - contraseña: str
  - especialidad: str
  - estado: bool
- Respuesta:
  - id_docente: int
  - nombres: str
  - apellidos: str
  - cedula: str
  - correo: str
  - especialidad: str
  - estado: bool

### Listar Docentes

- **GET** `/docentes/`
- Devuelve todos los docentes.
- Respuesta: lista de docentes con todos los campos, incluyendo `id_docente`.

### Obtener Docente por ID

- **GET** `/docentes/{docente_id}`
- Devuelve los datos de un docente específico.
- Respuesta:
  - id_docente: int
  - nombres: str
  - apellidos: str
  - cedula: str
  - correo: str
  - especialidad: str
  - estado: bool

### Actualizar Docente

- **PUT** `/docentes/{docente_id}`
- Actualiza los datos de un docente.
- Body: campos editables
- Respuesta: docente actualizado con todos los campos, incluyendo `id_docente`.

### Eliminar Docente

- **DELETE** `/docentes/{docente_id}`
- Elimina un docente.

---

# Documentación API - Estudiante

## Endpoints

### Crear Estudiante

- **POST** `/estudiantes/`
- Crea un nuevo estudiante.
- Body:
  - nombres: str
  - apellidos: str
  - cedula: str
  - correo: str
  - contraseña: str
  - telefono: str
  - estado: bool
- Respuesta:
  - id_estudiante: int
  - nombres: str
  - apellidos: str
  - cedula: str
  - correo: str
  - telefono: str
  - estado: bool

### Listar Estudiantes

- **GET** `/estudiantes/`
- Devuelve todos los estudiantes.
- Respuesta: lista de estudiantes con todos los campos, incluyendo `id_estudiante`.

### Obtener Estudiante por ID

- **GET** `/estudiantes/{estudiante_id}`
- Devuelve los datos de un estudiante específico.
- Respuesta:
  - id_estudiante: int
  - nombres: str
  - apellidos: str
  - cedula: str
  - correo: str
  - telefono: str
  - estado: bool

### Actualizar Estudiante

- **PUT** `/estudiantes/{estudiante_id}`
- Actualiza los datos de un estudiante.
- Body: campos editables
- Respuesta: estudiante actualizado con todos los campos, incluyendo `id_estudiante`.

### Eliminar Estudiante

- **DELETE** `/estudiantes/{estudiante_id}`
- Elimina un estudiante.

### Obtener Clases del Día

- **GET** `/estudiantes/proximas-clases/{estudiante_id}`
- Devuelve las clases del estudiante programadas para el día actual.
- Filtra por el día de la semana actual y solo muestra cursos activos.
- Respuesta:

```json
[
  {
    "id_curso": 1,
    "nombre_curso": "Cálculo I",
    "dia": "Viernes",
    "hora": "08:00-10:00",
    "id_docente": 1
  }
]
```
