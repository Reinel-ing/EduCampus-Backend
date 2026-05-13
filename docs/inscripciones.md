# API de Inscripciones (Gestión de Estudiantes en Cursos)

## Base URL

```
http://127.0.0.1:8000/inscripciones
```

---

## 1. Inscribir Estudiante en un Curso

**Endpoint:** `POST /inscripciones/`

**Descripción:** Inscribe un estudiante en un curso. Valida cupo disponible y evita inscripciones duplicadas. Envía email automático al estudiante.

**Request Body:**

```json
{
  "id_estudiante": 1,
  "id_curso": 1
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "id_estudiante": 1,
  "id_curso": 1
}
```

**Errores Posibles:**

- `404` - Curso no encontrado
- `400` - Cupo lleno
- `400` - Estudiante ya inscrito

**Ejemplo Frontend (JavaScript/Fetch):**

```javascript
async function inscribirEstudiante(idEstudiante, idCurso) {
  const response = await fetch("http://127.0.0.1:8000/inscripciones/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id_estudiante: idEstudiante,
      id_curso: idCurso,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}

// Uso:
try {
  const inscripcion = await inscribirEstudiante(1, 1);
  console.log("Estudiante inscrito:", inscripcion);
  alert(
    "Estudiante inscrito exitosamente. Se ha enviado un email de confirmación."
  );
} catch (error) {
  alert("Error: " + error.message);
}
```

---

## 2. Listar Todas las Inscripciones

**Endpoint:** `GET /inscripciones/`

**Descripción:** Obtiene todas las inscripciones del sistema.

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "id_estudiante": 1,
    "id_curso": 1
  },
  {
    "id": 2,
    "id_estudiante": 2,
    "id_curso": 1
  }
]
```

**Ejemplo Frontend:**

```javascript
async function listarInscripciones() {
  const response = await fetch("http://127.0.0.1:8000/inscripciones/");
  return await response.json();
}

// Uso:
const inscripciones = await listarInscripciones();
console.log("Total inscripciones:", inscripciones.length);
```

---

## 3. Ver Estudiantes de un Curso (Solo IDs)

**Endpoint:** `GET /inscripciones/por-curso/{curso_id}`

**Descripción:** Obtiene los IDs de estudiantes inscritos en un curso.

**Response (200 OK):**

```json
[1, 2, 3, 5, 8]
```

**Ejemplo Frontend:**

```javascript
async function obtenerEstudiantesPorCurso(idCurso) {
  const response = await fetch(
    `http://127.0.0.1:8000/inscripciones/por-curso/${idCurso}`
  );
  return await response.json();
}

// Uso:
const estudiantesIds = await obtenerEstudiantesPorCurso(1);
console.log("IDs de estudiantes:", estudiantesIds);
```

---

## 4. Ver Estudiantes de un Curso (Con Detalles) 🆕

**Endpoint:** `GET /inscripciones/detalles/por-curso/{curso_id}`

**Descripción:** Obtiene información completa de los estudiantes inscritos en un curso (nombre, correo, cédula, etc.).

**Response (200 OK):**

```json
[
  {
    "id_inscripcion": 1,
    "id_estudiante": 1,
    "nombres": "Juan",
    "apellidos": "Pérez García",
    "correo": "juan.perez@estudiante.edu.co",
    "cedula": "1234567890"
  },
  {
    "id_inscripcion": 2,
    "id_estudiante": 2,
    "nombres": "María",
    "apellidos": "González López",
    "correo": "maria.gonzalez@estudiante.edu.co",
    "cedula": "0987654321"
  }
]
```

**Ejemplo Frontend (Tabla de Estudiantes):**

```javascript
async function cargarEstudiantesCurso(idCurso) {
  const response = await fetch(
    `http://127.0.0.1:8000/inscripciones/detalles/por-curso/${idCurso}`
  );
  const estudiantes = await response.json();

  // Renderizar tabla
  const tbody = document.querySelector("#tabla-estudiantes tbody");
  tbody.innerHTML = "";

  estudiantes.forEach((est) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${est.cedula}</td>
      <td>${est.nombres} ${est.apellidos}</td>
      <td>${est.correo}</td>
      <td>
        <button onclick="eliminarInscripcion(${est.id_inscripcion})">
          Eliminar del Curso
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Uso:
await cargarEstudiantesCurso(1);
```

---

## 5. Ver Cursos de un Estudiante

**Endpoint:** `GET /inscripciones/por-estudiante/{estudiante_id}`

**Descripción:** Obtiene los IDs de cursos en los que está inscrito un estudiante.

**Response (200 OK):**

```json
[1, 3, 5]
```

**Ejemplo Frontend:**

```javascript
async function obtenerCursosPorEstudiante(idEstudiante) {
  const response = await fetch(
    `http://127.0.0.1:8000/inscripciones/por-estudiante/${idEstudiante}`
  );
  return await response.json();
}

// Uso:
const cursosIds = await obtenerCursosPorEstudiante(1);
console.log("Cursos del estudiante:", cursosIds);
```

---

## 6. Eliminar Inscripción (Remover Estudiante de Curso)

**Endpoint:** `DELETE /inscripciones/{inscripcion_id}`

**Descripción:** Elimina una inscripción, removiendo al estudiante del curso.

**Response (204 No Content):** Sin contenido (éxito)

**Errores Posibles:**

- `404` - Inscripción no encontrada

**Ejemplo Frontend:**

```javascript
async function eliminarInscripcion(idInscripcion) {
  const confirmar = confirm("¿Está seguro de eliminar esta inscripción?");
  if (!confirmar) return;

  const response = await fetch(
    `http://127.0.0.1:8000/inscripciones/${idInscripcion}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error("Error al eliminar inscripción");
  }

  alert("Estudiante removido del curso exitosamente");
  // Recargar la tabla
  await cargarEstudiantesCurso(cursoIdActual);
}

// Uso:
try {
  await eliminarInscripcion(1);
} catch (error) {
  alert("Error: " + error.message);
}
```

---

## Ejemplo Completo: Módulo de Gestión de Inscripciones

```javascript
// ============================================
// MÓDULO COMPLETO DE GESTIÓN DE INSCRIPCIONES
// ============================================

class InscripcionesManager {
  constructor(baseURL = "http://127.0.0.1:8000") {
    this.baseURL = baseURL;
  }

  // Inscribir estudiante
  async inscribir(idEstudiante, idCurso) {
    const response = await fetch(`${this.baseURL}/inscripciones/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_estudiante: idEstudiante, id_curso: idCurso }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  }

  // Listar todas
  async listarTodas() {
    const response = await fetch(`${this.baseURL}/inscripciones/`);
    return await response.json();
  }

  // Estudiantes de un curso (con detalles)
  async estudiantesPorCurso(idCurso) {
    const response = await fetch(
      `${this.baseURL}/inscripciones/detalles/por-curso/${idCurso}`
    );
    return await response.json();
  }

  // Cursos de un estudiante
  async cursosPorEstudiante(idEstudiante) {
    const response = await fetch(
      `${this.baseURL}/inscripciones/por-estudiante/${idEstudiante}`
    );
    return await response.json();
  }

  // Eliminar inscripción
  async eliminar(idInscripcion) {
    const response = await fetch(
      `${this.baseURL}/inscripciones/${idInscripcion}`,
      {
        method: "DELETE",
      }
    );

    if (!response.ok) {
      throw new Error("Error al eliminar inscripción");
    }
  }

  // Verificar si estudiante está inscrito en curso
  async estaInscrito(idEstudiante, idCurso) {
    const cursos = await this.cursosPorEstudiante(idEstudiante);
    return cursos.includes(idCurso);
  }
}

// ============================================
// USO DEL MÓDULO
// ============================================

const inscripciones = new InscripcionesManager();

// 1. Inscribir estudiante en curso
async function handleInscribir() {
  const idEstudiante = document.getElementById("select-estudiante").value;
  const idCurso = document.getElementById("select-curso").value;

  try {
    await inscripciones.inscribir(idEstudiante, idCurso);
    alert("✅ Estudiante inscrito exitosamente. Email enviado.");
    await cargarTablaEstudiantes(idCurso);
  } catch (error) {
    alert("❌ Error: " + error.message);
  }
}

// 2. Cargar tabla de estudiantes de un curso
async function cargarTablaEstudiantes(idCurso) {
  const estudiantes = await inscripciones.estudiantesPorCurso(idCurso);

  const tbody = document.querySelector("#tabla-estudiantes tbody");
  tbody.innerHTML = "";

  if (estudiantes.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="4">No hay estudiantes inscritos</td></tr>';
    return;
  }

  estudiantes.forEach((est) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${est.cedula}</td>
      <td>${est.nombres} ${est.apellidos}</td>
      <td>${est.correo}</td>
      <td>
        <button class="btn-eliminar" data-id="${est.id_inscripcion}">
          🗑️ Eliminar
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Event listeners para botones eliminar
  document.querySelectorAll(".btn-eliminar").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const id = e.target.dataset.id;
      await handleEliminar(id, idCurso);
    });
  });
}

// 3. Eliminar inscripción
async function handleEliminar(idInscripcion, idCurso) {
  if (!confirm("¿Eliminar estudiante del curso?")) return;

  try {
    await inscripciones.eliminar(idInscripcion);
    alert("✅ Estudiante removido del curso");
    await cargarTablaEstudiantes(idCurso);
  } catch (error) {
    alert("❌ Error: " + error.message);
  }
}

// 4. Verificar inscripción antes de mostrar botón
async function mostrarBotonInscribir(idEstudiante, idCurso) {
  const estaInscrito = await inscripciones.estaInscrito(idEstudiante, idCurso);

  const boton = document.getElementById("btn-inscribir");
  if (estaInscrito) {
    boton.disabled = true;
    boton.textContent = "Ya está inscrito";
  } else {
    boton.disabled = false;
    boton.textContent = "Inscribir en Curso";
  }
}
```

---

## Flujo Recomendado para el Frontend

### Panel de Administrador - Gestión de Curso

```
1. Seleccionar Curso (dropdown)
   ↓
2. GET /inscripciones/detalles/por-curso/{curso_id}
   → Mostrar tabla con estudiantes inscritos
   ↓
3. Botón "Añadir Estudiante"
   → Modal con dropdown de estudiantes disponibles
   → POST /inscripciones/ al seleccionar
   ↓
4. Botón "Eliminar" en cada fila
   → DELETE /inscripciones/{id}
   → Recargar tabla
```

### Panel de Estudiante - Mis Cursos

```
1. GET /inscripciones/por-estudiante/{estudiante_id}
   → Obtener IDs de cursos
   ↓
2. Para cada ID: GET /cursos/{curso_id}
   → Obtener detalles del curso
   ↓
3. Mostrar lista de cursos con información
```

---

## Notas Importantes

1. **Email Automático:** Al inscribir un estudiante, se envía automáticamente un email de confirmación con los detalles del curso y el docente.

2. **Validaciones:**

   - El sistema verifica el cupo disponible antes de inscribir
   - No permite inscripciones duplicadas
   - Valida que el curso exista

3. **Para eliminar:** Usa `id_inscripcion` (no `id_estudiante` ni `id_curso`)

4. **IDs vs Detalles:**

   - Usa `/por-curso/{id}` cuando solo necesites IDs (más rápido)
   - Usa `/detalles/por-curso/{id}` cuando necesites mostrar información completa

5. **Seguridad:** En producción, todas estas operaciones deben requerir autenticación JWT del administrador.
