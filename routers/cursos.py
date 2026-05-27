from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.curso import Curso
from models.docente import Docente
from models.estudiante_curso import EstudianteCurso
from schemas.curso import CursoCreate, CursoUpdate, CursoResponse
from datetime import datetime

router = APIRouter(prefix="/cursos", tags=["Cursos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
def create_curso(curso: CursoCreate, db: Session = Depends(get_db)):
    db_curso = Curso(**curso.model_dump())
    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)
    return db_curso

@router.get("/", response_model=list[CursoResponse])
def list_cursos(db: Session = Depends(get_db)):
    return db.query(Curso).all()

@router.get("/{curso_id}", response_model=CursoResponse)
def get_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@router.put("/{curso_id}", response_model=CursoResponse)
def update_curso(curso_id: int, curso: CursoUpdate, db: Session = Depends(get_db)):
    db_curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not db_curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    for key, value in curso.model_dump(exclude_unset=True).items():
        setattr(db_curso, key, value)
    db.commit()
    db.refresh(db_curso)
    return db_curso

@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curso(curso_id: int, db: Session = Depends(get_db)):
    db_curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not db_curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    db.delete(db_curso)
    db.commit()

@router.get("/{curso_id}/estudiantes", response_model=list)
def estudiantes_del_curso(curso_id: int, db: Session = Depends(get_db)):
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == curso_id).all()
    return [i.id_estudiante for i in inscripciones]

@router.get("/{curso_id}/verificar-cupo", response_model=dict)
def verificar_cupo(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    inscritos = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == curso_id).count()
    return {"cupo": curso.cupo_estudiante, "inscritos": inscritos, "disponible": curso.cupo_estudiante - inscritos}

@router.get("/por-docente/{docente_id}", response_model=list[CursoResponse])
def cursos_por_docente(docente_id: int, db: Session = Depends(get_db)):
    return db.query(Curso).filter(Curso.id_docente == docente_id).all()

@router.get("/proximas-clases/{docente_id}", response_model=list[dict])
def proximas_clases_docente(docente_id: int, db: Session = Depends(get_db)):
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_actual = dias_semana[datetime.now().weekday()]
    
    cursos = db.query(Curso).filter(Curso.id_docente == docente_id, Curso.estado == True).all()
    
    clases_proximas = []
    for curso in cursos:
        for horario in curso.horario:
            if horario.get("dia") == dia_actual:
                clases_proximas.append({
                    "id_curso": curso.id_curso,
                    "nombre_curso": curso.nombre,
                    "dia": horario.get("dia"),
                    "hora": horario.get("hora"),
                    "cupo_estudiante": curso.cupo_estudiante
                })
    
    return clases_proximas

@router.get("/por-estudiante/{estudiante_id}", response_model=list[dict])
def cursos_por_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_estudiante == estudiante_id).all()
    curso_ids = [i.id_curso for i in inscripciones]
    
    if not curso_ids:
        return []
    
    cursos = db.query(Curso).filter(Curso.id_curso.in_(curso_ids)).all()
    
    resultado = []
    for curso in cursos:
        docente = db.query(Docente).filter(Docente.id_docente == curso.id_docente).first()
        
        resultado.append({
            "id_curso": curso.id_curso,
            "nombre": curso.nombre,
            "cupo_estudiante": curso.cupo_estudiante,
            "horario": curso.horario,
            "estado": curso.estado,
            "docente": {
                "id_docente": docente.id_docente,
                "nombres": docente.nombres,
                "apellidos": docente.apellidos,
                "correo": docente.correo,
                "especialidad": docente.especialidad
            } if docente else None
        })
    
    return resultado

@router.get("/horario/{estudiante_id}", response_model=list[dict])
def obtener_horario_estudiante(estudiante_id: int, db: Session = Depends(get_db)):
    inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_estudiante == estudiante_id).all()
    curso_ids = [i.id_curso for i in inscripciones]

    if not curso_ids:
        return []

    cursos = db.query(Curso).filter(Curso.id_curso.in_(curso_ids), Curso.estado == True).all()

    horarios = []
    for curso in cursos:
        if curso.horario:
            for h in curso.horario:
                if isinstance(h, dict):
                    dia  = h.get("dia", "")
                    hora = h.get("hora", "")
                elif isinstance(h, str):
                    partes = h.split(" ", 1)
                    dia  = partes[0] if len(partes) > 0 else ""
                    hora = partes[1] if len(partes) > 1 else ""
                else:
                    continue
                horarios.append({
                    "id_curso": curso.id_curso,
                    "nombre_curso": curso.nombre,
                    "dia": dia,
                    "hora": hora,
                })

    return horarios


@router.get("/horario-docente/{docente_id}", response_model=list[dict])
def obtener_horario_docente(docente_id: int, db: Session = Depends(get_db)):
    cursos = db.query(Curso).filter(Curso.id_docente == docente_id, Curso.estado == True).all()

    horarios = []
    for curso in cursos:
        if curso.horario:
            for h in curso.horario:
                if isinstance(h, dict):
                    dia  = h.get("dia", "")
                    hora = h.get("hora", "")
                elif isinstance(h, str):
                    partes = h.split(" ", 1)
                    dia  = partes[0] if len(partes) > 0 else ""
                    hora = partes[1] if len(partes) > 1 else ""
                else:
                    continue
                horarios.append({
                    "id_curso": curso.id_curso,
                    "nombre_curso": curso.nombre,
                    "dia": dia,
                    "hora": hora,
                })

    return horarios
