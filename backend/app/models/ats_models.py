from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
import re

class EmpresaInfo(BaseModel):
    """Información de la empresa que genera el ATS"""
    ruc: str = Field(..., min_length=13, max_length=13, description="RUC de la empresa")
    razon_social: str = Field(..., max_length=300, description="Razón social de la empresa")
    
    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v):
        if not re.match(r'^\d{13}$', v):
            raise ValueError('RUC debe tener exactamente 13 dígitos numéricos')
        return v
    
    @field_validator('razon_social')
    @classmethod
    def validate_razon_social(cls, v):
        cleaned = re.sub(r'\s+', ' ', v.strip().upper())
        if len(cleaned) > 300:
            raise ValueError('Razón social no puede exceder 300 caracteres')
        return cleaned

class ComprobanteTXT(BaseModel):
    ruc_emisor: str
    razon_social_emisor: str
    tipo_comprobante: str
    serie_comprobante: str
    clave_acceso: str
    fecha_autorizacion: str
    fecha_emision: str
    identificacion_receptor: str
    valor_sin_impuestos: float
    iva: float
    importe_total: float
    numero_documento_modificado: Optional[str] = None
    
    @field_validator('clave_acceso')
    @classmethod
    def validate_clave_acceso(cls, v):
        clave_limpia = re.sub(r'\D', '', str(v))
        if len(clave_limpia) != 49:
            if len(clave_limpia) < 49:
                clave_limpia = clave_limpia.ljust(49, '0')
            else:
                clave_limpia = clave_limpia[:49]
        if not clave_limpia.isdigit():
            raise ValueError('Clave de acceso debe contener solo dígitos numéricos')
        return clave_limpia

class FormaPago(BaseModel):
    """Forma de pago según SRI"""
    formaPago: str
    total: float

class DetalleCompra(BaseModel):
    """Detalle de compras según especificaciones del SRI"""
    codSustento: str = "01"  # ✅ CAMBIADO: Usar "01" por defecto
    tpIdProv: str = "01"
    idProv: str
    tipoComprobante: str = "01"
    parteRel: str = "NO"
    fechaRegistro: str
    establecimiento: str
    puntoEmision: str
    secuencial: str
    fechaEmision: str
    autorizacion: str
    baseNoGraIva: float = 0.00
    baseImponible: float = 0.00
    baseImpGrav: float = 0.00
    baseImpExe: float = 0.00
    montoIce: float = 0.00
    montoIva: float = 0.00
    valRetBien10: float = 0.00
    valRetServ20: float = 0.00
    valorRetBienes: float = 0.00
    valRetServ50: float = 0.00
    valorRetServicios: float = 0.00
    valRetServ100: float = 0.00
    valorRetencionNc: float = 0.00
    totbasesImpReemb: float = 0.00
    pagoLocExt: str = "01"
    paisEfecPago: str = "NA"
    aplicConvDobTrib: str = "NA"
    pagExtSujRetNorLeg: str = "NA"
    formas_pago: List[FormaPago] = []  # ✅ AGREGADO: Formas de pago
    
    @field_validator('autorizacion')
    @classmethod
    def validate_autorizacion(cls, v):
        auth_limpia = re.sub(r'\D', '', str(v))
        if len(auth_limpia) != 49:
            if len(auth_limpia) < 49:
                auth_limpia = auth_limpia.ljust(49, '0')
            else:
                auth_limpia = auth_limpia[:49]
        if not auth_limpia.isdigit():
            raise ValueError('Autorización debe contener solo dígitos numéricos')
        return auth_limpia
    
    @model_validator(mode='after')
    def validate_consistency(self):
        """Validaciones de consistencia después de crear el modelo"""
        # Asegurar campos correctos para pago local
        if self.pagoLocExt == "01":
            self.paisEfecPago = "NA"
            self.aplicConvDobTrib = "NA"
            self.pagExtSujRetNorLeg = "NA"
        
        # ✅ VALIDACIÓN: Agregar forma de pago si falta y el total excede $1000
        total_compra = self.baseImponible + self.baseImpGrav + self.montoIva
        if not self.formas_pago and total_compra >= 1000.00:
            self.formas_pago = [FormaPago(formaPago="01", total=total_compra)]
        
        return self

class DetalleVenta(BaseModel):
    """Detalle de ventas según especificaciones del SRI"""
    tpIdCliente: str
    idCliente: str
    parteRel: str = "NO"
    tipoComprobante: str
    tipoEmision: str
    numeroComprobantes: int
    baseNoGraIva: float = 0.00
    baseImponible: float = 0.00
    baseImpGrav: float = 0.00
    montoIva: float = 0.00
    montoIce: float = 0.00
    valorRetIva: float = 0.00
    valorRetRenta: float = 0.00
    formas_pago: List[FormaPago] = []

class ATSData(BaseModel):
    """Modelo principal para los datos del ATS"""
    tipoIDInformante: str = "R"
    idInformante: str
    razonSocial: str
    anio: int
    mes: int
    numEstabRuc: str = "001"
    totalVentas: float = 0.00
    codigoOperativo: str = "IVA"
    compras: List[DetalleCompra] = []
    ventas: List[DetalleVenta] = []
    
    @field_validator('idInformante')
    @classmethod
    def validate_id_informante(cls, v):
        if not re.match(r'^\d{13}$', v):
            raise ValueError('RUC debe tener exactamente 13 dígitos')
        return v
    
    @field_validator('mes')
    @classmethod
    def validate_mes(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Mes debe estar entre 1 y 12')
        return v
    
    @field_validator('anio')
    @classmethod
    def validate_anio(cls, v):
        current_year = datetime.now().year
        if not 2000 <= v <= current_year + 1:
            raise ValueError(f'Año debe estar entre 2000 y {current_year + 1}')
        return v
