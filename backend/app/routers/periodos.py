from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db.session import get_db
from ..models.sql_models import PeriodoFiscal, Empresa
from pydantic import BaseModel

router = APIRouter(
    prefix="/periodos",
    tags=["periodos"]
)

class PeriodoCreate(BaseModel):
    ruc_empresa: str
    razon_social: str  # Razón social de la empresa
    anio: int
    mes: int

class PeriodoResponse(BaseModel):
    id: int
    ruc_empresa: str
    anio: int
    mes: int
    estado: str
    total_compras: int
    total_ventas: int

    class Config:
        from_attributes = True

@router.post("/", response_model=PeriodoResponse)
def create_periodo(periodo: PeriodoCreate, db: Session = Depends(get_db)):
    # Buscar o crear empresa
    empresa = db.query(Empresa).filter(Empresa.ruc == periodo.ruc_empresa).first()
    if not empresa:
        empresa = Empresa(ruc=periodo.ruc_empresa, razon_social=periodo.razon_social)
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
    else:
        # Actualizar razón social si cambió
        if empresa.razon_social != periodo.razon_social:
            empresa.razon_social = periodo.razon_social
            db.commit()
            db.refresh(empresa)
    
    # Verificar si ya existe el periodo
    existing = db.query(PeriodoFiscal).filter(
        PeriodoFiscal.empresa_id == empresa.id,
        PeriodoFiscal.anio == periodo.anio,
        PeriodoFiscal.mes == periodo.mes
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="El periodo ya existe")
    
    new_periodo = PeriodoFiscal(
        empresa_id=empresa.id,
        anio=periodo.anio,
        mes=periodo.mes
    )
    db.add(new_periodo)
    db.commit()
    db.refresh(new_periodo)
    
    return PeriodoResponse(
        id=new_periodo.id,
        ruc_empresa=empresa.ruc,
        anio=new_periodo.anio,
        mes=new_periodo.mes,
        estado=new_periodo.estado,
        total_compras=0,
        total_ventas=0
    )

@router.get("/", response_model=List[PeriodoResponse])
def list_periodos(ruc: str = None, db: Session = Depends(get_db)):
    query = db.query(PeriodoFiscal).join(Empresa)
    if ruc:
        query = query.filter(Empresa.ruc == ruc)
    
    periodos = query.all()
    results = []
    for p in periodos:
        results.append(PeriodoResponse(
            id=p.id,
            ruc_empresa=p.empresa.ruc,
            anio=p.anio,
            mes=p.mes,
            estado=p.estado,
            total_compras=len(p.compras),
            total_ventas=len(p.ventas)
        ))
    return results

@router.get("/{periodo_id}", response_model=PeriodoResponse)
def get_periodo(periodo_id: int, db: Session = Depends(get_db)):
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    return PeriodoResponse(
        id=periodo.id,
        ruc_empresa=periodo.empresa.ruc,
        anio=periodo.anio,
        mes=periodo.mes,
        estado=periodo.estado,
        total_compras=len(periodo.compras),
        total_ventas=len(periodo.ventas)
    )

@router.delete("/{periodo_id}")
def delete_periodo(periodo_id: int, db: Session = Depends(get_db)):
    periodo = db.query(PeriodoFiscal).filter(PeriodoFiscal.id == periodo_id).first()
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    db.delete(periodo)
    db.commit()
    return {"message": "Periodo eliminado correctamente"}

class BatchDeleteRequest(BaseModel):
    ids: List[int]

@router.delete("/batch/delete")
def delete_periodos_batch(request: BatchDeleteRequest, db: Session = Depends(get_db)):
    # Eliminar múltiples periodos
    db.query(PeriodoFiscal).filter(PeriodoFiscal.id.in_(request.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"{len(request.ids)} periodos eliminados correctamente"}
