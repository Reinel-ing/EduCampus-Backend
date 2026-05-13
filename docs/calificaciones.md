# Documentación API - Calificaciones

## Endpoints

### Crear Calificación

- **POST** `/calificaciones/`
- Crea una nueva calificación para un estudiante en un curso.
- Valida que la nota esté entre 0 y 5.
- Body:
  - id_estudiante: int
  - id_curso: int
  - tipo_evaluacion: int (1 = Parcial 1, 2 = Parcial 2, 3 = Final)
  - nota: float (0.0 - 5.0)
- Respuesta:
  - id_calificacion: int
  - id_estudiante: int
  - id_curso: int
  - tipo_evaluacion: int
  - nota: float

### Actualizar Calificación

- **PUT** `/calificaciones/{calificacion_id}`
- Actualiza una calificación existente.
- Valida que la nota esté entre 0 y 5.
- Body:
  - tipo_evaluacion: int (opcional)
  - nota: float (opcional)
- Respuesta: calificación actualizada con todos los campos.

### Calificaciones por Curso

- **GET** `/calificaciones/por-curso/{curso_id}`
- Devuelve todas las calificaciones de un curso.
- Respuesta: lista de calificaciones con todos los campos.

### Calificaciones por Estudiante

- **GET** `/calificaciones/por-estudiante/{estudiante_id}`
- Devuelve todas las calificaciones de un estudiante.
- Respuesta: lista de calificaciones con todos los campos.

### Promedio de Estudiante

- **GET** `/calificaciones/promedio-estudiante/{estudiante_id}`
- Calcula el promedio general de todas las calificaciones del estudiante.
- Respuesta:

```json
{
  "promedio": 4.2
}
```

### Promedio de Curso

- **GET** `/calificaciones/promedio-curso/{curso_id}`
- Calcula el promedio general de todas las calificaciones del curso.
- Respuesta:

```json
{
  "promedio": 3.8
}
```

## Cálculo de Promedio Ponderado

El sistema calcula el promedio final con los siguientes pesos:

- **Parcial 1** (tipo_evaluacion = 1): 30%
- **Parcial 2** (tipo_evaluacion = 2): 30%
- **Final** (tipo_evaluacion = 3): 40%

**Fórmula:**

```
Promedio = (Parcial1 × 0.30) + (Parcial2 × 0.30) + (Final × 0.40)
```
