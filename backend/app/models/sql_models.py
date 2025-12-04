from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from ..db.session import Base
from datetime import datetime

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    ruc = Column(String, unique=True, index=True)
    razon_social = Column(String)
    direccion = Column(String, nullable=True)
    obligado_contabilidad = Column(Boolean, default=False)
    
    periodos = relationship("PeriodoFiscal", back_populates="empresa")

class PeriodoFiscal(Base):
    __tablename__ = "periodos_fiscales"

    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    anio = Column(Integer)
    mes = Column(Integer)
    estado = Column(String, default="ABIERTO") # ABIERTO, CERRADO, GENERADO
    fecha_creacion = Column(Date, default=datetime.now)
    
    empresa = relationship("Empresa", back_populates="periodos")
    compras = relationship("FacturaCompra", back_populates="periodo", cascade="all, delete-orphan")
    ventas = relationship("FacturaVenta", back_populates="periodo", cascade="all, delete-orphan")
    retenciones = relationship("Retencion", back_populates="periodo", cascade="all, delete-orphan")

class FacturaCompra(Base):
    __tablename__ = "facturas_compra"

    id = Column(Integer, primary_key=True, index=True)
    periodo_id = Column(Integer, ForeignKey("periodos_fiscales.id"))
    
    # Datos Principales
    codSustento = Column(String, default="01")
    tpIdProv = Column(String, default="01")
    idProv = Column(String)
    razon_social = Column(String) # Added field
    tipoComprobante = Column(String, default="01")
    parteRel = Column(String, default="NO")
    fechaRegistro = Column(String)
    establecimiento = Column(String)
    puntoEmision = Column(String)
    secuencial = Column(String)
    fechaEmision = Column(String)
    autorizacion = Column(String)
    
    # Valores
    baseNoGraIva = Column(Float, default=0.0)
    baseImponible = Column(Float, default=0.0)
    baseImpGrav = Column(Float, default=0.0)
    baseImpExe = Column(Float, default=0.0)
    montoIce = Column(Float, default=0.0)
    montoIva = Column(Float, default=0.0)
    
    # Retenciones (Valores calculados o ingresados)
    valRetBien10 = Column(Float, default=0.0)
    valRetServ20 = Column(Float, default=0.0)
    valorRetBienes = Column(Float, default=0.0)
    valRetServ50 = Column(Float, default=0.0)
    valorRetServicios = Column(Float, default=0.0)
    valRetServ100 = Column(Float, default=0.0)
    
    # Pago
    pagoLocExt = Column(String, default="01")
    paisEfecPago = Column(String, default="NA")
    aplicConvDobTrib = Column(String, default="NA")
    pagExtSujRetNorLeg = Column(String, default="NA")
    formaPago = Column(String, default="01")
    
    periodo = relationship("PeriodoFiscal", back_populates="compras")

class FacturaVenta(Base):
    __tablename__ = "facturas_venta"

    id = Column(Integer, primary_key=True, index=True)
    periodo_id = Column(Integer, ForeignKey("periodos_fiscales.id"))
    
    tpIdCliente = Column(String)
    idCliente = Column(String)
    parteRel = Column(String, default="NO")
    tipoComprobante = Column(String)
    tipoEmision = Column(String, default="F")
    numeroComprobantes = Column(Integer, default=1)
    baseNoGraIva = Column(Float, default=0.0)
    baseImponible = Column(Float, default=0.0)
    baseImpGrav = Column(Float, default=0.0)
    montoIva = Column(Float, default=0.0)
    montoIce = Column(Float, default=0.0)
    valorRetIva = Column(Float, default=0.0)
    valorRetRenta = Column(Float, default=0.0)
    
    formaPago = Column(String, default="01")
    
    periodo = relationship("PeriodoFiscal", back_populates="ventas")

class Retencion(Base):
    __tablename__ = "retenciones"

    id = Column(Integer, primary_key=True, index=True)
    periodo_id = Column(Integer, ForeignKey("periodos_fiscales.id"))
    
    # Datos de la retención
    establecimiento = Column(String)
    puntoEmision = Column(String)
    secuencial = Column(String)
    autorizacion = Column(String)
    fechaEmision = Column(String)
    
    # Relación con factura (si aplica)
    codSustento = Column(String)
    
    periodo = relationship("PeriodoFiscal", back_populates="retenciones")
