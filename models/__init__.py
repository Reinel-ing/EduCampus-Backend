from sqlalchemy.orm import relationship
from .docente import Docente
from .curso import Curso
from .estudiante import Estudiante
from .estudiante_curso import EstudianteCurso
from .calificacion import Calificacion
from .asistencia import Asistencia
from .material_didactico import MaterialDidactico
from .configuracion import Configuracion
from .administrador import Administrador

# Relaciones
Docente.cursos = relationship("Curso", backref="docente", cascade="all, delete-orphan")
Curso.estudiantes = relationship("EstudianteCurso", backref="curso", cascade="all, delete-orphan")
Estudiante.cursos = relationship("EstudianteCurso", backref="estudiante", cascade="all, delete-orphan")
Curso.materiales = relationship("MaterialDidactico", backref="curso", cascade="all, delete-orphan")
Curso.calificaciones = relationship("Calificacion", backref="curso", cascade="all, delete-orphan")
Estudiante.calificaciones = relationship("Calificacion", backref="estudiante", cascade="all, delete-orphan")
Curso.asistencias = relationship("Asistencia", backref="curso", cascade="all, delete-orphan")
Estudiante.asistencias = relationship("Asistencia", backref="estudiante", cascade="all, delete-orphan")
