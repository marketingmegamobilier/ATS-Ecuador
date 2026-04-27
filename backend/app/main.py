import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from datetime import datetime
from typing import List
import zipfile
import io

from .services.xml_processor import XMLProcessor
from .services.xml_generator import XMLGenerator
from .models.ats_models import EmpresaInfo
from .db.session import engine, Base
from .models import sql_models # Importar modelos para que se registren en Base

# Crear tablas
# Crear tablas
Base.metadata.create_all(bind=engine)

from .routers import periodos, transacciones, validation

app = FastAPI(
    title="Generador ATS - SRI Ecuador",
    description="Sistema para generar XML del Anexo Transaccional Simplificado",
    version="2.0.0"
)

# Configurar CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(periodos.router)
app.include_router(transacciones.router)
app.include_router(validation.router)

# Instanciar servicios
xml_processor = XMLProcessor()
xml_generator = XMLGenerator()

@app.get("/")
async def root():
    return {
        "message": "Generador ATS - SRI Ecuador",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.post("/upload-xml-facturas")
async def upload_xml_facturas(
    files: List[UploadFile] = File(...),
    ruc_empresa: str = Form(...),
    razon_social_empresa: str = Form(...)
):
    """
    Endpoint para subir múltiples archivos XML de facturas con identificación de errores
    """
    # Validar que todos los archivos sean XML
    for file in files:
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail=f"El archivo {file.filename} no es XML")
    
    try:
        # Validar información de la empresa
        empresa_info = EmpresaInfo(
            ruc=ruc_empresa,
            razon_social=razon_social_empresa
        )
        
        # Leer contenido de todos los archivos XML con nombres
        xml_contents = []
        filenames = []
        
        for file in files:
            content = await file.read()
            xml_content = content.decode('utf-8')
            xml_contents.append(xml_content)
            filenames.append(file.filename)  # ✅ AGREGADO: Guardar nombres de archivos
        
        # Procesar archivos XML con nombres
        ats_data, errors = xml_processor.process_xml_files(xml_contents, empresa_info, filenames)
        
        return {
            "success": True,
            "message": f"Procesados {len(ats_data.compras)} facturas exitosamente de {len(files)} archivos",
            "data": ats_data.model_dump(),
            "errors": errors,
            "total_facturas": len(ats_data.compras),
            "total_archivos": len(files),
            "archivos_con_error": len(errors),
            "periodo": f"{ats_data.mes:02d}/{ats_data.anio}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando facturas XML: {str(e)}")

@app.post("/generate-xml")
async def generate_xml(ats_data: dict):
    """
    Endpoint para generar solo XML del ATS
    """
    try:
        from .models.ats_models import ATSData
        
        ats_model = ATSData(**ats_data)
        xml_content = xml_generator.generate_ats_xml(ats_model)
        filename = f"AT{ats_model.mes:02d}{ats_model.anio}.xml"
        
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generando XML: {str(e)}")

@app.post("/generate-xml-zip")
async def generate_xml_zip(ats_data: dict):
    """
    Endpoint para generar XML del ATS comprimido en ZIP
    """
    try:
        from .models.ats_models import ATSData
        
        ats_model = ATSData(**ats_data)
        xml_content = xml_generator.generate_ats_xml(ats_model)
        
        xml_filename = f"AT{ats_model.mes:02d}{ats_model.anio}.xml"
        zip_filename = f"AT{ats_model.mes:02d}{ats_model.anio}.zip"
        
        # Crear ZIP en memoria
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
            zip_file.writestr(xml_filename, xml_content.encode('utf-8'))
            
            readme_content = f"""
ANEXO TRANSACCIONAL SIMPLIFICADO (ATS)
=====================================

Archivo: {xml_filename}
Período: {ats_model.mes:02d}/{ats_model.anio}
RUC: {ats_model.idInformante}
Razón Social: {ats_model.razonSocial}
Total Compras: {len(ats_model.compras)}

Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Instrucciones:
1. Extraer el archivo {xml_filename}
2. Ingresar al portal del SRI: https://srienlinea.sri.gob.ec
3. Ir a Anexos > Envío y consulta de anexos
4. Seleccionar "Anexo Transaccional Simplificado"
5. Subir el archivo {xml_filename}

Sistema Generador ATS v2.0.0
            """.strip()
            
            zip_file.writestr("README.txt", readme_content.encode('utf-8'))
        
        zip_buffer.seek(0)
        zip_content = zip_buffer.getvalue()
        
        return Response(
            content=zip_content,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}",
                "Content-Length": str(len(zip_content))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generando ZIP: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
