from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from ..db.session import get_db
from ..models.sql_models import FacturaCompra, FacturaVenta, PeriodoFiscal, Retencion
from ..services.xml_processor import XMLProcessor
from pydantic import BaseModel
from fastapi.responses import Response

router = APIRouter(
    prefix="/transacciones",
    tags=["transacciones"]
)

xml_processor = XMLProcessor()

# --- Schemas ---
class CompraResponse(BaseModel):
    id: int
    ruc_emisor: str
    razon_social: str
    fecha_emision: str
    tipo_comprobante: str
    secuencial: str
    base_imponible: float
    monto_iva: float
    total: float

    class Config:
        from_attributes = True

class VentaResponse(BaseModel):
    id: int
    cliente: str
    fecha_emision: str
    tipo_comprobante: str
    numero_comprobantes: int
    base_imponible: float
    monto_iva: float

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/periodo/{periodo_id}/compras", response_model=List[CompraResponse])
def list_compras(periodo_id: int, db: Session = Depends(get_db)):
    compras = db.query(FacturaCompra).filter(FacturaCompra.periodo_id == periodo_id).all()
    
    results = []
    for c in compras:
        total = c.baseImponible + c.baseImpGrav + c.baseImpExe + c.baseNoGraIva + c.montoIva + c.montoIce
        results.append(CompraResponse(
            id=c.id,
            ruc_emisor=c.idProv,
            razon_social=c.razon_social,
            fecha_emision=c.fechaEmision,
            tipo_comprobante=c.tipoComprobante,
            secuencial=c.secuencial,
            base_imponible=c.baseImponible + c.baseImpGrav,
            monto_iva=c.montoIva,
            total=total
        ))
    
    return results

@router.get("/periodo/{periodo_id}/ventas", response_model=List[VentaResponse])
def list_ventas(periodo_id: int, db: Session = Depends(get_db)):
    ventas = db.query(FacturaVenta).filter(FacturaVenta.periodo_id == periodo_id).all()
    
    results = []
    for v in ventas:
        results.append(VentaResponse(
            id=v.id,
            cliente=v.idCliente,
            fecha_emision="N/A",
            tipo_comprobante=v.tipoComprobante,
            numero_comprobantes=v.numeroComprobantes,
            base_imponible=v.baseImponible + v.baseImpGrav,
            monto_iva=v.montoIva
        ))
    
    return results

@router.post("/periodo/{periodo_id}/upload-compras")
async def upload_compras(
    periodo_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    xml_contents = []
    filenames = []
    
    for file in files:
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail=f"{file.filename} no es XML")
        content = await file.read()
        xml_contents.append(content.decode('utf-8'))
        filenames.append(file.filename)
    
    try:
        count, errors = xml_processor.process_and_save_to_db(xml_contents, filenames, periodo_id, db, doc_type="compra")
        
        return {
            "success": True,
            "processed": count,
            "errors": errors,
            "total_files": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/compras/{compra_id}")
def delete_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = db.query(FacturaCompra).filter(FacturaCompra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    db.delete(compra)
    db.commit()
    return {"message": "Compra eliminada"}

@router.post("/periodo/{periodo_id}/upload-ventas")
async def upload_ventas(
    periodo_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    xml_contents = []
    filenames = []
    
    for file in files:
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail=f"{file.filename} no es XML")
        content = await file.read()
        xml_contents.append(content.decode('utf-8'))
        filenames.append(file.filename)
    
    try:
        count, errors = xml_processor.process_and_save_to_db(xml_contents, filenames, periodo_id, db, doc_type="venta")
        
        return {
            "success": True,
            "processed": count,
            "errors": errors,
            "total_files": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/periodo/{periodo_id}/upload-retenciones")
async def upload_retenciones(
    periodo_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    xml_contents = []
    filenames = []
    
    for file in files:
        if not file.filename.endswith('.xml'):
            raise HTTPException(status_code=400, detail=f"{file.filename} no es XML")
        content = await file.read()
        xml_contents.append(content.decode('utf-8'))
        filenames.append(file.filename)
        
    try:
        count, errors = xml_processor.process_and_save_to_db(xml_contents, filenames, periodo_id, db, doc_type="retencion")
        
        return {
            "success": True,
            "processed": count,
            "errors": errors,
            "total_files": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ventas/{venta_id}")
def delete_venta(venta_id: int, db: Session = Depends(get_db)):
    venta = db.query(FacturaVenta).filter(FacturaVenta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(venta)
    db.commit()
    return {"message": "Venta eliminada"}

@router.delete("/retenciones/{retencion_id}")
def delete_retencion(retencion_id: int, db: Session = Depends(get_db)):
    retencion = db.query(Retencion).filter(Retencion.id == retencion_id).first()
    if not retencion:
        raise HTTPException(status_code=404, detail="Retención no encontrada")
    db.delete(retencion)
    db.commit()
    return {"message": "Retención eliminada"}

@router.get("/periodo/{periodo_id}/retenciones")
def list_retenciones(periodo_id: int, db: Session = Depends(get_db)):
    retenciones = db.query(Retencion).filter(Retencion.periodo_id == periodo_id).all()
    results = []
    for r in retenciones:
        results.append({
            "id": r.id,
            "establecimiento": r.establecimiento,
            "puntoEmision": r.puntoEmision,
            "secuencial": r.secuencial,
            "autorizacion": r.autorizacion,
            "fechaEmision": r.fechaEmision
        })
    return results

# ==============================================
# ENDPOINTS DE GENERACIÓN Y DESCARGA DE ATS
# ==============================================

@router.get("/periodo/{periodo_id}/generar-ats")
def generar_ats_zip(periodo_id: int, db: Session = Depends(get_db)):
    """
    Genera y descarga el archivo ATS en formato ZIP (para envío al SRI).
    Incluye README con instrucciones.
    """
    from ..models.ats_models import ATSData, DetalleCompra, DetalleVenta, FormaPago
    from ..services.xml_generator import XMLGenerator
    import io
    import zipfile
    from datetime import datetime
    
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    # Generar compras
    compras_ats = []
    for c in periodo.compras:
        total_bases = c.baseImponible + c.baseImpGrav + c.baseNoGraIva + c.baseImpExe
        total_con_impuestos = total_bases + c.montoIva + c.montoIce
        
        formas_pago_list = []
        if total_con_impuestos > 500.00:
            formas_pago_list = [FormaPago(formaPago=c.formaPago or "01", total=total_con_impuestos)]
        
        compras_ats.append(DetalleCompra(
            codSustento=c.codSustento,
            tpIdProv=c.tpIdProv,
            idProv=c.idProv,
            tipoComprobante=c.tipoComprobante,
            parteRel=c.parteRel,
            fechaRegistro=c.fechaRegistro,
            establecimiento=c.establecimiento,
            puntoEmision=c.puntoEmision,
            secuencial=c.secuencial,
            fechaEmision=c.fechaEmision,
            autorizacion=c.autorizacion,
            baseNoGraIva=c.baseNoGraIva,
            baseImponible=c.baseImponible,
            baseImpGrav=c.baseImpGrav,
            baseImpExe=c.baseImpExe,
            montoIce=c.montoIce,
            montoIva=c.montoIva,
            valRetBien10=c.valRetBien10,
            valRetServ20=c.valRetServ20,
            valorRetBienes=c.valorRetBienes,
            valRetServ50=c.valRetServ50,
            valorRetServicios=c.valorRetServicios,
            valRetServ100=c.valRetServ100,
            valorRetencionNc=getattr(c, 'valorRetencionNc', 0.0),
            totbasesImpReemb=getattr(c, 'totbasesImpReemb', 0.0),
            pagoLocExt=c.pagoLocExt,
            paisEfecPago=c.paisEfecPago,
            aplicConvDobTrib=c.aplicConvDobTrib,
            pagExtSujRetNorLeg=c.pagExtSujRetNorLeg,
            formas_pago=formas_pago_list
        ))
    
    # Generar ventas
    ventas_ats = []
    total_ventas = 0.0
    
    def get_tipo_id_cliente_ventas(identificacion: str) -> str:
        if len(identificacion) == 13 and identificacion.endswith("001"):
            return "04"
        elif len(identificacion) == 10:
            return "05"
        elif identificacion == "9999999999999":
            return "07"
        elif len(identificacion) >= 3:
            return "06"
        return "07"
    
    for v in periodo.ventas:
        # Los campos de bases son EXCLUYENTES (no se duplican)
        total_bases = v.baseImponible + v.baseImpGrav + v.baseNoGraIva
        total_ventas += total_bases
        
        total_con_iva = total_bases + v.montoIva + v.montoIce
        tp_id_cliente = get_tipo_id_cliente_ventas(v.idCliente)
        
        parte_rel = "NO"
        if tp_id_cliente in ["04", "05", "06"]:
            parte_rel = v.parteRel or "NO"
        else:
            parte_rel = None
        
        formas_pago_list = []
        if total_con_iva > 500.00:
            formas_pago_list = [FormaPago(formaPago=v.formaPago or "01", total=total_con_iva)]
        
        ventas_ats.append(DetalleVenta(
            tpIdCliente=tp_id_cliente,
            idCliente=v.idCliente,
            parteRel=parte_rel if parte_rel else "NO",
            tipoComprobante=v.tipoComprobante,
            tipoEmision=v.tipoEmision,
            numeroComprobantes=v.numeroComprobantes,
            baseNoGraIva=v.baseNoGraIva,
            baseImponible=v.baseImponible,
            baseImpGrav=v.baseImpGrav,
            montoIva=v.montoIva,
            montoIce=v.montoIce,
            valorRetIva=v.valorRetIva,
            valorRetRenta=v.valorRetRenta,
            formas_pago=formas_pago_list
        ))
    
    ats_data = ATSData(
        idInformante=periodo.empresa.ruc,
        razonSocial=periodo.empresa.razon_social,
        anio=periodo.anio,
        mes=periodo.mes,
        numEstabRuc="001",
        totalVentas=total_ventas,
        compras=compras_ats,
        ventas=ventas_ats
    )
    
    generator = XMLGenerator()
    xml_str = generator.generate_ats_xml(ats_data)
    
    xml_filename = f"ATS_{periodo.mes:02d}_{periodo.anio}_{periodo.empresa.ruc}.xml"
    zip_filename = f"ATS_{periodo.mes:02d}_{periodo.anio}_{periodo.empresa.ruc}.zip"
    
    
    # Crear ZIP en memoria con solo el XML
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(xml_filename, xml_str.encode('utf-8'))
    
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )


@router.get("/periodo/{periodo_id}/generar-ats-xml")
def generar_ats_xml_solo(periodo_id: int, db: Session = Depends(get_db)):
    """
    Genera y descarga SOLO el archivo XML del ATS (sin comprimir).
    Útil para revisión, debugging y validación offline.
    """
    from ..models.ats_models import ATSData, DetalleCompra, DetalleVenta, FormaPago
    from ..services.xml_generator import XMLGenerator
    
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    # Generar compras (mismo código que ZIP)
    compras_ats = []
    for c in periodo.compras:
        total_bases = c.baseImponible + c.baseImpGrav + c.baseNoGraIva + c.baseImpExe
        total_con_impuestos = total_bases + c.montoIva + c.montoIce
        
        formas_pago_list = []
        if total_con_impuestos > 500.00:
            formas_pago_list = [FormaPago(formaPago=c.formaPago or "01", total=total_con_impuestos)]
        
        compras_ats.append(DetalleCompra(
            codSustento=c.codSustento,
            tpIdProv=c.tpIdProv,
            idProv=c.idProv,
            tipoComprobante=c.tipoComprobante,
            parteRel=c.parteRel,
            fechaRegistro=c.fechaRegistro,
            establecimiento=c.establecimiento,
            puntoEmision=c.puntoEmision,
            secuencial=c.secuencial,
            fechaEmision=c.fechaEmision,
            autorizacion=c.autorizacion,
            baseNoGraIva=c.baseNoGraIva,
            baseImponible=c.baseImponible,
            baseImpGrav=c.baseImpGrav,
            baseImpExe=c.baseImpExe,
            montoIce=c.montoIce,
            montoIva=c.montoIva,
            valRetBien10=c.valRetBien10,
            valRetServ20=c.valRetServ20,
            valorRetBienes=c.valorRetBienes,
            valRetServ50=c.valRetServ50,
            valorRetServicios=c.valorRetServicios,
            valRetServ100=c.valRetServ100,
            valorRetencionNc=getattr(c, 'valorRetencionNc', 0.0),
            totbasesImpReemb=getattr(c, 'totbasesImpReemb', 0.0),
            pagoLocExt=c.pagoLocExt,
            paisEfecPago=c.paisEfecPago,
            aplicConvDobTrib=c.aplicConvDobTrib,
            pagExtSujRetNorLeg=c.pagExtSujRetNorLeg,
            formas_pago=formas_pago_list
        ))
    
    # Generar ventas (mismo código que ZIP)
    ventas_ats = []
    total_ventas = 0.0
    
    def get_tipo_id_cliente_ventas(identificacion: str) -> str:
        if len(identificacion) == 13 and identificacion.endswith("001"):
            return "04"
        elif len(identificacion) == 10:
            return "05"
        elif identificacion == "9999999999999":
            return "07"
        elif len(identificacion) >= 3:
            return "06"
        return "07"
    
    for v in periodo.ventas:
        # Los campos de bases son EXCLUYENTES (no se duplican)
        total_bases = v.baseImponible + v.baseImpGrav + v.baseNoGraIva  
        total_ventas += total_bases
        
        total_con_iva = total_bases + v.montoIva + v.montoIce
        tp_id_cliente = get_tipo_id_cliente_ventas(v.idCliente)
        
        parte_rel = "NO"
        if tp_id_cliente in ["04", "05", "06"]:
            parte_rel = v.parteRel or "NO"
        else:
            parte_rel = None
        
        formas_pago_list = []
        if total_con_iva > 500.00:
            formas_pago_list = [FormaPago(formaPago=v.formaPago or "01", total=total_con_iva)]
        
        ventas_ats.append(DetalleVenta(
            tpIdCliente=tp_id_cliente,
            idCliente=v.idCliente,
            parteRel=parte_rel if parte_rel else "NO",
            tipoComprobante=v.tipoComprobante,
            tipoEmision=v.tipoEmision,
            numeroComprobantes=v.numeroComprobantes,
            baseNoGraIva=v.baseNoGraIva,
            baseImponible=v.baseImponible,
            baseImpGrav=v.baseImpGrav,
            montoIva=v.montoIva,
            montoIce=v.montoIce,
            valorRetIva=v.valorRetIva,
            valorRetRenta=v.valorRetRenta,
            formas_pago=formas_pago_list
        ))
    
    ats_data = ATSData(
        idInformante=periodo.empresa.ruc,
        razonSocial=periodo.empresa.razon_social,
        anio=periodo.anio,
        mes=periodo.mes,
        numEstabRuc="001",
        totalVentas=total_ventas,
        compras=compras_ats,
        ventas=ventas_ats
    )
    
    generator = XMLGenerator()
    xml_str = generator.generate_ats_xml(ats_data)
    
    xml_filename = f"ATS_{periodo.mes:02d}_{periodo.anio}_{periodo.empresa.ruc}.xml"
    
    # Retornar XML directamente
    return Response(
        content=xml_str.encode('utf-8'),
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={xml_filename}",
            "Content-Type": "application/xml; charset=utf-8"
        }
    )
