import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.material_didactico import MaterialDidactico
from models.curso import Curso
from models.estudiante_curso import EstudianteCurso
from models.estudiante import Estudiante
from models.docente import Docente
from schemas.material import MaterialResponse
from datetime import date
from dotenv import load_dotenv
import os
from service.email_service import email_service
from service.sms_service import sms_service
from service.notificacion_service import crear_notificacion, notificar_admins

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

router = APIRouter(prefix="/material", tags=["Material Didáctico"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def subir_material(
    id_curso: int = Form(...),
    nombre_archivo: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if archivo.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    result = cloudinary.uploader.upload(
        file=archivo.file,
        resource_type="raw",
        public_id=nombre_archivo
    )
    url = result["secure_url"]
    nuevo_material = MaterialDidactico(
        id_curso=id_curso,
        archivo_url=url,
        nombre_archivo=nombre_archivo,
        fecha=date.today()
    )
    db.add(nuevo_material)
    db.commit()
    db.refresh(nuevo_material)
    
    # Obtener curso y docente
    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if curso:
        docente = db.query(Docente).filter(Docente.id_docente == curso.id_docente).first()
        docente_nombre = f"{docente.nombres} {docente.apellidos}" if docente else "Docente"
        
        # Obtener todos los estudiantes inscritos en el curso
        inscripciones = db.query(EstudianteCurso).filter(EstudianteCurso.id_curso == id_curso).all()
        
        for inscripcion in inscripciones:
            estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == inscripcion.id_estudiante).first()
            if estudiante:
                # Notificacion en BD
                crear_notificacion(
                    db,
                    titulo=f"Nuevo material en {curso.nombre}",
                    mensaje=f"El docente {docente_nombre} subio el archivo '{nombre_archivo}' en el curso '{curso.nombre}'.",
                    tipo="material",
                    id_destinatario=estudiante.id_estudiante,
                    tipo_destinatario="estudiante",
                )
                try:
                    email_service.notify_material_uploaded(
                        to_email=estudiante.correo,
                        nombre_estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
                        curso=curso.nombre,
                        nombre_archivo=nombre_archivo,
                        docente=docente_nombre
                    )
                except Exception as e:
                    print(f"Error al enviar email a {estudiante.correo}: {e}")

                try:
                    sms_service.notify_material_uploaded(
                        to_number=estudiante.telefono,
                        nombre_estudiante=f"{estudiante.nombres} {estudiante.apellidos}",
                        curso=curso.nombre,
                        nombre_archivo=nombre_archivo,
                        docente=docente_nombre
                    )
                except Exception as e:
                    print(f"Error al enviar SMS a {estudiante.telefono}: {e}")
        # Notificacion para los admins
        notificar_admins(
            db,
            titulo="Material didactico subido",
            mensaje=f"El docente {docente_nombre} subio el archivo '{nombre_archivo}' en el curso '{curso.nombre}'.",
            tipo="sistema",
        )
        db.commit()

    return nuevo_material

@router.get("/por-curso/{curso_id}", response_model=list[MaterialResponse])
def listar_material_por_curso(curso_id: int, db: Session = Depends(get_db)):
    return db.query(MaterialDidactico).filter(MaterialDidactico.id_curso == curso_id).all()

from fastapi.responses import JSONResponse

@router.get("/descargar/{material_id}", response_class=JSONResponse)
def descargar_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(MaterialDidactico).filter(MaterialDidactico.id_material == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return JSONResponse(content={"url": material.archivo_url})

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(MaterialDidactico).filter(MaterialDidactico.id_material == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    db.delete(material)
    db.commit()

@router.get("/por-docente/{docente_id}", response_model=list[dict])
def listar_material_por_docente(docente_id: int, db: Session = Depends(get_db)):
    cursos = db.query(Curso).filter(Curso.id_docente == docente_id).all()
    
    if not cursos:
        return []
    
    materiales = []
    for curso in cursos:
        materiales_curso = db.query(MaterialDidactico).filter(MaterialDidactico.id_curso == curso.id_curso).all()
        
        for material in materiales_curso:
            materiales.append({
                "id_material": material.id_material,
                "nombre_archivo": material.nombre_archivo,
                "archivo_url": material.archivo_url,
                "fecha": str(material.fecha),
                "curso": curso.nombre,
                "id_curso": curso.id_curso
            })
    
    return materiales
