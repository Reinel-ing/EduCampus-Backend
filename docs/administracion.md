# API de Administración - Gestión Completa del Sistema

## Base URL

```
http://127.0.0.1:8000
```

---

## GESTIÓN DE CURSOS

### 1. Actualizar Curso

**Endpoint:** `PUT /cursos/{curso_id}`

**Descripción:** Actualiza información de un curso existente.

**Request Body (todos los campos son opcionales):**

```json
{
  "nombre": "Matemáticas Avanzadas II",
  "descripcion": "Curso actualizado de matemáticas",
  "horario": "Martes y Jueves 10:00 AM - 12:00 PM",
  "cupo_estudiante": 35,
  "id_docente": 2,
  "estado": true
}
```

**Response (200 OK):**

```json
{
  "id_curso": 1,
  "nombre": "Matemáticas Avanzadas II",
  "descripcion": "Curso actualizado de matemáticas",
  "horario": "Martes y Jueves 10:00 AM - 12:00 PM",
  "cupo_estudiante": 35,
  "id_docente": 2,
  "estado": true
}
```

**Ejemplo Frontend:**

```javascript
async function actualizarCurso(idCurso, datosActualizados) {
  const response = await fetch(`http://127.0.0.1:8000/cursos/${idCurso}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(datosActualizados),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}

// Uso - Actualizar solo el nombre y cupo:
try {
  const cursoActualizado = await actualizarCurso(1, {
    nombre: "Matemáticas Avanzadas II",
    cupo_estudiante: 35,
  });
  alert("Curso actualizado exitosamente");
} catch (error) {
  alert("Error: " + error.message);
}
```

---

### 2. Eliminar Curso

**Endpoint:** `DELETE /cursos/{curso_id}`

**Descripción:** Elimina un curso del sistema.

**Response (204 No Content):** Sin contenido (éxito)

**Errores Posibles:**

- `404` - Curso no encontrado

**Ejemplo Frontend:**

```javascript
async function eliminarCurso(idCurso) {
  const confirmar = confirm(
    "¿Está seguro de eliminar este curso? Esta acción no se puede deshacer."
  );
  if (!confirmar) return;

  const response = await fetch(`http://127.0.0.1:8000/cursos/${idCurso}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Error al eliminar curso");
  }

  alert("Curso eliminado exitosamente");
  // Recargar lista de cursos
  await cargarCursos();
}

// Uso:
try {
  await eliminarCurso(1);
} catch (error) {
  alert("Error: " + error.message);
}
```

---

## GESTIÓN DE DOCENTES

### 3. Actualizar Docente

**Endpoint:** `PUT /docentes/{docente_id}`

**Descripción:** Actualiza información de un docente. Si se actualiza la contraseña, se hashea automáticamente.

**Request Body (todos los campos son opcionales):**

```json
{
  "nombres": "Carlos Alberto",
  "apellidos": "Rodríguez Pérez",
  "cedula": "9876543210",
  "correo": "carlos.rodriguez@vortal.edu.co",
  "telefono": "3201234567",
  "contraseña": "nuevaContraseña123"
}
```

**Response (200 OK):**

```json
{
  "id_docente": 1,
  "nombres": "Carlos Alberto",
  "apellidos": "Rodríguez Pérez",
  "cedula": "9876543210",
  "correo": "carlos.rodriguez@vortal.edu.co",
  "telefono": "3201234567",
  "contraseña": "$2b$12$hashedpassword..."
}
```

**Ejemplo Frontend:**

```javascript
async function actualizarDocente(idDocente, datos) {
  const response = await fetch(`http://127.0.0.1:8000/docentes/${idDocente}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(datos),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}

// Uso - Actualizar solo teléfono:
await actualizarDocente(1, {
  telefono: "3209876543",
});

// Uso - Cambiar contraseña:
await actualizarDocente(1, {
  contraseña: "nuevaContraseña123",
});
```

---

### 4. Eliminar Docente

**Endpoint:** `DELETE /docentes/{docente_id}`

**Descripción:** Elimina un docente del sistema.

**Response (204 No Content):** Sin contenido (éxito)

**Ejemplo Frontend:**

```javascript
async function eliminarDocente(idDocente) {
  const confirmar = confirm(
    "¿Eliminar este docente? Se eliminarán sus cursos asociados."
  );
  if (!confirmar) return;

  const response = await fetch(`http://127.0.0.1:8000/docentes/${idDocente}`, {
    method: "DELETE",
  });

  if (response.ok) {
    alert("Docente eliminado exitosamente");
    await cargarDocentes();
  } else {
    alert("Error al eliminar docente");
  }
}
```

---

## GESTIÓN DE ESTUDIANTES

### 5. Actualizar Estudiante

**Endpoint:** `PUT /estudiantes/{estudiante_id}`

**Descripción:** Actualiza información de un estudiante. Si se actualiza la contraseña, se hashea automáticamente.

**Request Body (todos los campos son opcionales):**

```json
{
  "nombres": "María José",
  "apellidos": "González López",
  "cedula": "1234567890",
  "correo": "maria.gonzalez@estudiante.edu.co",
  "telefono": "3101234567",
  "contraseña": "nuevaContraseña456"
}
```

**Ejemplo Frontend:**

```javascript
async function actualizarEstudiante(idEstudiante, datos) {
  const response = await fetch(
    `http://127.0.0.1:8000/estudiantes/${idEstudiante}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(datos),
    }
  );

  if (!response.ok) {
    throw new Error("Error al actualizar estudiante");
  }

  return await response.json();
}
```

---

### 6. Eliminar Estudiante

**Endpoint:** `DELETE /estudiantes/{estudiante_id}`

**Descripción:** Elimina un estudiante del sistema.

**Response (204 No Content):** Sin contenido (éxito)

**Ejemplo Frontend:**

```javascript
async function eliminarEstudiante(idEstudiante) {
  const confirmar = confirm(
    "¿Eliminar este estudiante? Se eliminarán sus inscripciones."
  );
  if (!confirmar) return;

  const response = await fetch(
    `http://127.0.0.1:8000/estudiantes/${idEstudiante}`,
    {
      method: "DELETE",
    }
  );

  if (response.ok) {
    alert("Estudiante eliminado exitosamente");
    await cargarEstudiantes();
  } else {
    alert("Error al eliminar estudiante");
  }
}
```

---

## MÓDULO COMPLETO DE ADMINISTRACIÓN

```javascript
// ========================================
// CLASE PARA GESTIÓN DE ADMINISTRACIÓN
// ========================================

class AdminManager {
  constructor(baseURL = "http://127.0.0.1:8000") {
    this.baseURL = baseURL;
  }

  // ============ CURSOS ============

  async actualizarCurso(id, datos) {
    const response = await fetch(`${this.baseURL}/cursos/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!response.ok) throw new Error("Error al actualizar curso");
    return await response.json();
  }

  async eliminarCurso(id) {
    const response = await fetch(`${this.baseURL}/cursos/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("Error al eliminar curso");
  }

  async listarCursos() {
    const response = await fetch(`${this.baseURL}/cursos/`);
    return await response.json();
  }

  async crearCurso(datos) {
    const response = await fetch(`${this.baseURL}/cursos/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!response.ok) throw new Error("Error al crear curso");
    return await response.json();
  }

  // ============ DOCENTES ============

  async actualizarDocente(id, datos) {
    const response = await fetch(`${this.baseURL}/docentes/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!response.ok) throw new Error("Error al actualizar docente");
    return await response.json();
  }

  async eliminarDocente(id) {
    const response = await fetch(`${this.baseURL}/docentes/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("Error al eliminar docente");
  }

  async listarDocentes() {
    const response = await fetch(`${this.baseURL}/docentes/`);
    return await response.json();
  }

  async crearDocente(datos) {
    const response = await fetch(`${this.baseURL}/docentes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!response.ok) throw new Error("Error al crear docente");
    return await response.json();
  }

  // ============ ESTUDIANTES ============

  async actualizarEstudiante(id, datos) {
    const response = await fetch(`${this.baseURL}/estudiantes/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!response.ok) throw new Error("Error al actualizar estudiante");
    return await response.json();
  }

  async eliminarEstudiante(id) {
    const response = await fetch(`${this.baseURL}/estudiantes/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("Error al eliminar estudiante");
  }

  async listarEstudiantes() {
    const response = await fetch(`${this.baseURL}/estudiantes/`);
    return await response.json();
  }

  async crearEstudiante(datos) {
    const response = await fetch(`${this.baseURL}/estudiantes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });

    if (!response.ok) throw new Error("Error al crear estudiante");
    return await response.json();
  }
}

// ========================================
// EJEMPLO DE USO COMPLETO
// ========================================

const admin = new AdminManager();

// ---------- FORMULARIO DE EDICIÓN DE CURSO ----------

async function cargarFormularioEditarCurso(idCurso) {
  // Obtener datos actuales
  const response = await fetch(`http://127.0.0.1:8000/cursos/${idCurso}`);
  const curso = await response.json();

  // Rellenar formulario
  document.getElementById("nombre").value = curso.nombre;
  document.getElementById("descripcion").value = curso.descripcion;
  document.getElementById("horario").value = curso.horario;
  document.getElementById("cupo").value = curso.cupo_estudiante;
  document.getElementById("docente").value = curso.id_docente;
  document.getElementById("estado").checked = curso.estado;

  // Al enviar formulario
  document.getElementById("form-curso").onsubmit = async (e) => {
    e.preventDefault();

    const datosActualizados = {
      nombre: document.getElementById("nombre").value,
      descripcion: document.getElementById("descripcion").value,
      horario: document.getElementById("horario").value,
      cupo_estudiante: parseInt(document.getElementById("cupo").value),
      id_docente: parseInt(document.getElementById("docente").value),
      estado: document.getElementById("estado").checked,
    };

    try {
      await admin.actualizarCurso(idCurso, datosActualizados);
      alert("✅ Curso actualizado exitosamente");
      window.location.href = "/cursos";
    } catch (error) {
      alert("❌ Error: " + error.message);
    }
  };
}

// ---------- TABLA DE CURSOS CON ACCIONES ----------

async function cargarTablaCursos() {
  const cursos = await admin.listarCursos();
  const tbody = document.querySelector("#tabla-cursos tbody");
  tbody.innerHTML = "";

  cursos.forEach((curso) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${curso.nombre}</td>
      <td>${curso.horario}</td>
      <td>${curso.cupo_estudiante}</td>
      <td>${curso.estado ? "✅ Activo" : "❌ Inactivo"}</td>
      <td>
        <button onclick="editarCurso(${curso.id_curso})">✏️ Editar</button>
        <button onclick="eliminarCurso(${curso.id_curso})">🗑️ Eliminar</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function editarCurso(id) {
  window.location.href = `/cursos/editar/${id}`;
}

async function eliminarCurso(id) {
  if (!confirm("¿Eliminar este curso?")) return;

  try {
    await admin.eliminarCurso(id);
    alert("✅ Curso eliminado");
    await cargarTablaCursos();
  } catch (error) {
    alert("❌ Error: " + error.message);
  }
}

// ---------- CAMBIO DE CONTRASEÑA ----------

async function cambiarContraseñaDocente(idDocente) {
  const nuevaContraseña = prompt("Ingrese la nueva contraseña:");
  if (!nuevaContraseña) return;

  try {
    await admin.actualizarDocente(idDocente, {
      contraseña: nuevaContraseña,
    });
    alert("✅ Contraseña actualizada exitosamente");
  } catch (error) {
    alert("❌ Error: " + error.message);
  }
}

// ---------- ACTIVAR/DESACTIVAR CURSO ----------

async function toggleEstadoCurso(idCurso, estadoActual) {
  const nuevoEstado = !estadoActual;
  const accion = nuevoEstado ? "activar" : "desactivar";

  if (!confirm(`¿${accion} este curso?`)) return;

  try {
    await admin.actualizarCurso(idCurso, {
      estado: nuevoEstado,
    });
    alert(`✅ Curso ${accion}do exitosamente`);
    await cargarTablaCursos();
  } catch (error) {
    alert("❌ Error: " + error.message);
  }
}
```

---

## Flujos Completos de Administración

### 1. Gestión de Curso

```
Ver Cursos → Listar Cursos
   ↓
Clic en "Editar" → Cargar formulario con datos
   ↓
Modificar campos → PUT /cursos/{id}
   ↓
Guardar → Actualizar tabla
```

### 2. Gestión de Docente

```
Ver Docentes → Listar Docentes
   ↓
Opciones por fila:
  - Editar perfil → PUT /docentes/{id}
  - Cambiar contraseña → PUT con solo contraseña
  - Eliminar → DELETE /docentes/{id}
```

### 3. Gestión de Estudiante

```
Ver Estudiantes → Listar Estudiantes
   ↓
Clic en estudiante → Ver cursos inscritos
   ↓
Opciones:
  - Editar perfil → PUT /estudiantes/{id}
  - Ver inscripciones → GET /inscripciones/por-estudiante/{id}
  - Eliminar → DELETE /estudiantes/{id}
```

---

## Notas Importantes

1. **Actualizaciones Parciales:** Todos los PUT aceptan campos opcionales. Solo envía los campos que quieres actualizar.

2. **Contraseñas:** Al actualizar contraseñas, se hashean automáticamente con bcrypt. No necesitas hashearlas en el frontend.

3. **Emails:** Al crear docentes o estudiantes, se envían emails automáticos con las credenciales.

4. **Validaciones:** El backend valida duplicados de email y cédula.

5. **Relaciones:**

   - Al eliminar un curso, se eliminan sus inscripciones
   - Al eliminar un docente, considera reasignar sus cursos primero
   - Al eliminar un estudiante, se eliminan sus inscripciones

6. **Estados de Curso:** Usa el campo `estado` (boolean) para activar/desactivar cursos sin eliminarlos.
