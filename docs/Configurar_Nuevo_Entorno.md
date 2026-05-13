# Configurar el Nuevo Entorno

Esta guía explica cómo configurar e implementar el sistema académico Vortal en un nuevo servidor o base de datos.

## Requisitos Previos

- Python 3.10 o superior
- PostgreSQL (recomendado: Neon, AWS RDS, o cualquier instancia PostgreSQL)
- Cuenta de Cloudinary (para almacenamiento de archivos PDF)

## Pasos de Configuración

### 1. Clonar o Copiar el Proyecto

Asegúrate de tener todos los archivos del proyecto en el servidor destino.

### 2. Crear Entorno Virtual (Recomendado)

```bash
python -m venv venv
```

**Activar el entorno virtual:**

- Windows:

```bash
venv\Scripts\activate
```

- Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**

- FastAPI
- SQLAlchemy
- Pydantic
- Alembic
- psycopg (PostgreSQL driver)
- Cloudinary
- python-dotenv
- uvicorn

### 4. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@host:puerto/nombre_db?sslmode=require
API_SECRET=tu_cloudinary_api_secret
```

**Ejemplo con Neon PostgreSQL:**

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require
API_SECRET=ZDQVj8Fx2wPJm9hUM0OqObgBmWk
```

**Ejemplo con PostgreSQL local:**

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/vortal_db
API_SECRET=tu_cloudinary_secret
```

### 5. Configurar Cloudinary (Opcional pero Recomendado)

Si vas a usar la funcionalidad de subida de material didáctico:

1. Crea una cuenta en [Cloudinary](https://cloudinary.com/)
2. Obtén tus credenciales: `cloud_name`, `api_key`, `api_secret`
3. Actualiza el archivo `routers/material.py` con tus credenciales:

```python
cloudinary.config(
    cloud_name="tu_cloud_name",
    api_key="tu_api_key",
    api_secret=os.getenv("API_SECRET"),
    secure=True
)
```

### 6. Crear las Tablas en la Base de Datos

Ejecuta el script para crear todas las tablas automáticamente:

```bash
python create_tables.py
```

Este comando creará las siguientes tablas:

- administrador
- docente
- estudiante
- curso
- estudiante_curso (inscripciones)
- calificacion
- asistencia
- material_didactico
- configuracion

### 7. Crear Administrador Inicial

```bash
python seed_admin.py
```

**Credenciales por defecto:**

- Correo: `admin@vortal.edu.co`
- Contraseña: `123456789`

**⚠️ IMPORTANTE:** Cambia estas credenciales después del primer login.

### 8. (Opcional) Cargar Datos de Prueba

Si deseas poblar la base de datos con datos de ejemplo:

```bash
python seed_data.py
```

Esto creará:

- 3 docentes
- 5 estudiantes
- 3 cursos con horarios
- 8 inscripciones
- 7 calificaciones
- 7 asistencias
- 3 materiales didácticos

### 9. Ejecutar el Servidor

**Modo desarrollo (con recarga automática):**

```bash
uvicorn main:app --reload
```

**Modo producción:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Con workers para alta disponibilidad:**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 10. Verificar la Instalación

1. Abre el navegador en: `http://localhost:8000`
2. Accede a la documentación interactiva: `http://localhost:8000/docs`
3. Prueba el endpoint de login con las credenciales del administrador

## Comandos Resumidos

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env (editar manualmente)

# 4. Crear tablas
python create_tables.py

# 5. Crear administrador
python seed_admin.py

# 6. (Opcional) Datos de prueba
python seed_data.py

# 7. Ejecutar servidor
uvicorn main:app --reload
```

## Solución de Problemas

### Error: "No module named 'psycopg'"

```bash
pip install psycopg
```

### Error: "relation does not exist"

Ejecuta nuevamente:

```bash
python create_tables.py
```

### Error de conexión a la base de datos

- Verifica que el `DATABASE_URL` en `.env` sea correcto
- Asegúrate de que la base de datos existe
- Verifica credenciales de acceso

### Puerto 8000 en uso

Usa otro puerto:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

## Despliegue en Producción

Para despliegue en servidores de producción, considera:

1. **Usar un servidor ASGI robusto** como Gunicorn con workers de Uvicorn
2. **Configurar HTTPS** con certificados SSL
3. **Usar un proxy reverso** como Nginx
4. **Configurar variables de entorno** de forma segura
5. **Implementar backups** automáticos de la base de datos
6. **Monitorear logs** y rendimiento

## Soporte

Para más información, consulta la documentación de cada módulo en la carpeta `docs/`.
