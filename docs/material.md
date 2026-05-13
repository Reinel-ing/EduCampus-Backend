# Documentación API - Material Didáctico

## Endpoints

### Subir Material

- **POST** `/material/upload`
- Sube un archivo PDF a Cloudinary y guarda la referencia en la base de datos.
- Solo acepta archivos PDF.
- Body (form-data):
  - id_curso: int
  - nombre_archivo: str
  - archivo: File (PDF)
- Respuesta:
  - id_material: int
  - id_curso: int
  - archivo_url: str
  - nombre_archivo: str
  - fecha: date

### Listar Material por Curso

- **GET** `/material/por-curso/{curso_id}`
- Devuelve todos los materiales didácticos de un curso específico.
- Respuesta: lista de materiales con todos los campos.

### Listar Material por Docente

- **GET** `/material/por-docente/{docente_id}`
- Devuelve todos los materiales didácticos de todos los cursos del docente.
- Respuesta:

```json
[
  {
    "id_material": 1,
    "nombre_archivo": "Guía Cálculo I",
    "archivo_url": "https://res.cloudinary.com/.../archivo.pdf",
    "fecha": "2025-11-15",
    "curso": "Cálculo I",
    "id_curso": 1
  }
]
```

### Descargar Material

- **GET** `/material/descargar/{material_id}`
- Devuelve la URL de descarga del archivo PDF.
- Respuesta:

```json
{
  "url": "https://res.cloudinary.com/.../archivo.pdf"
}
```

### Eliminar Material

- **DELETE** `/material/{material_id}`
- Elimina un material didáctico de la base de datos.
- No elimina el archivo de Cloudinary, solo la referencia.

## Notas

- Los archivos se almacenan en **Cloudinary** con URLs públicas.
- Solo se aceptan archivos en formato **PDF**.
- La fecha de subida se registra automáticamente.
