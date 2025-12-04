export interface ComprobanteTXT {
  ruc_emisor: string;
  razon_social_emisor: string;
  tipo_comprobante: string;
  serie_comprobante: string;
  clave_acceso: string;
  fecha_autorizacion: string;
  fecha_emision: string;
  identificacion_receptor: string;
  valor_sin_impuestos: number;
  iva: number;
  importe_total: number;
  numero_documento_modificado?: string;
}

export interface DetalleCompra {
  codSustento: string;
  tpIdProv: string;
  idProv: string;
  tipoComprobante: string;
  parteRel: string;
  fechaRegistro: string;
  establecimiento: string;
  puntoEmision: string;
  secuencial: string;
  fechaEmision: string;
  autorizacion: string;
  baseNoGraIva: number;
  baseImponible: number;
  baseImpGrav: number;
  baseImpExe: number;
  montoIce: number;
  montoIva: number;
  valRetBien10: number;
  valRetServ20: number;
  valorRetBienes: number;
  valRetServ50: number;
  valorRetServicios: number;
  valRetServ100: number;
  valorRetencionNc: number;
  totbasesImpReemb: number;
  pagoLocExt: string;
  paisEfecPago: string;
  aplicConvDobTrib: string;
  pagExtSujRetNorLeg: string;
}

export interface ATSData {
  tipoIDInformante: string;
  idInformante: string;
  razonSocial: string;
  anio: number;
  mes: number;
  numEstabRuc: string;
  totalVentas: number;
  codigoOperativo: string;
  compras: DetalleCompra[];
}

export interface ProcessResponse {
  success: boolean;
  message: string;
  data: ATSData;
  errors: string[];
  total_comprobantes?: number;
  total_facturas: number;
  total_archivos: number;        // ✅ AGREGADO
  archivos_con_error: number;    // ✅ AGREGADO
  periodo: string;
}
