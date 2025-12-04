import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import re
from ..models.ats_models import ATSData, DetalleCompra, EmpresaInfo

class XMLProcessor:
    def __init__(self):
        self.tipo_comprobante_map = {
            "01": "01",  # Factura
            "04": "04",  # Nota de Crédito
            "05": "05",  # Nota de Débito
            "06": "06"   # Guía de Remisión
        }
    
    def validate_xml_structure(self, xml_content: str, filename: str) -> Tuple[bool, str]:
        """
        Valida la estructura básica del XML antes de procesarlo
        """
        try:
            root = ET.fromstring(xml_content)
            
            root = ET.fromstring(xml_content)
            
            # Caso 1: XML de Autorización (Estándar SRI Online)
            if root.tag == 'autorizacion':
                # Verificar elementos básicos
                estado = root.find('estado')
                if estado is None:
                    return False, f"El archivo {filename} no tiene elemento 'estado'"
                
                if estado.text != 'AUTORIZADO':
                    return False, f"El archivo {filename} no está autorizado (estado: {estado.text})"
                
                # Verificar que existe el comprobante
                comprobante = root.find('comprobante')
                if comprobante is None:
                    return False, f"El archivo {filename} no tiene elemento 'comprobante'"
                
                if not comprobante.text:
                    return False, f"El archivo {filename} no contiene contenido en el comprobante"

                return True, "OK"

            # Caso 2: XML Directo (Factura, Retención, etc. sin wrapper de autorización)
            elif root.tag in ['factura', 'comprobanteRetencion', 'notaCredito', 'notaDebito', 'guiaRemision']:
                # Validaciones básicas para documento directo
                info_tributaria = root.find('infoTributaria')
                if info_tributaria is None:
                    return False, f"El archivo {filename} no tiene infoTributaria"
                
                return True, "OK"

            else:
                return False, f"El archivo {filename} tiene un formato desconocido (root: {root.tag})"
            
        except ET.ParseError as e:
            return False, f"El archivo {filename} tiene formato XML inválido: {str(e)}"
        except Exception as e:
            return False, f"Error validando {filename}: {str(e)}"
    
    def _get_xml_root(self, xml_content: str) -> ET.Element:
        """Helper to get the document root, handling both authorized and direct XMLs"""
        root = ET.fromstring(xml_content)
        if root.tag == 'autorizacion':
            comprobante = root.find('comprobante')
            cdata_content = comprobante.text
            if cdata_content.startswith('<![CDATA['):
                cdata_content = cdata_content.replace('<![CDATA[', '').replace(']]>', '')
            return ET.fromstring(cdata_content)
        return root

    def extract_factura_from_xml(self, xml_content: str, filename: str) -> Dict:
        """
        Extrae información completa de una factura XML del SRI con manejo de errores mejorado
        """
        try:
            # Validar estructura primero
            is_valid, validation_message = self.validate_xml_structure(xml_content, filename)
            if not is_valid:
                raise ValueError(validation_message)
            
            factura_root = self._get_xml_root(xml_content)
            
            # Extraer información tributaria
            info_tributaria = factura_root.find('infoTributaria')
            info_factura = factura_root.find('infoFactura')
            
            if info_tributaria is None:
                raise ValueError(f"El archivo {filename} no tiene información tributaria")
            if info_factura is None:
                raise ValueError(f"El archivo {filename} no tiene información de factura")
            
            # Extraer datos básicos con validación
            def safe_get_text(element, element_name, required=True):
                if element is None:
                    if required:
                        raise ValueError(f"El archivo {filename} no tiene elemento '{element_name}'")
                    return ""
                return element.text or ""
            
            ruc_emisor = safe_get_text(info_tributaria.find('ruc'), 'ruc')
            razon_social = safe_get_text(
                info_tributaria.find('razonSocial'), 'razonSocial'
            ) or safe_get_text(
                info_tributaria.find('nombreComercial'), 'nombreComercial', False
            )
            
            establecimiento = safe_get_text(info_tributaria.find('estab'), 'estab')
            punto_emision = safe_get_text(info_tributaria.find('ptoEmi'), 'ptoEmi')
            secuencial = safe_get_text(info_tributaria.find('secuencial'), 'secuencial')
            clave_acceso = safe_get_text(info_tributaria.find('claveAcceso'), 'claveAcceso')
            fecha_emision = safe_get_text(info_factura.find('fechaEmision'), 'fechaEmision')
            identificacion_comprador = safe_get_text(
                info_factura.find('identificacionComprador'), 'identificacionComprador'
            )
            
            # Extraer totales con validación
            total_sin_impuestos_elem = info_factura.find('totalSinImpuestos')
            importe_total_elem = info_factura.find('importeTotal')
            
            if total_sin_impuestos_elem is None or importe_total_elem is None:
                raise ValueError(f"El archivo {filename} no tiene totales válidos")
            
            total_sin_impuestos = float(total_sin_impuestos_elem.text)
            importe_total = float(importe_total_elem.text)
            
            # Extraer bases tributarias exactas del XML
            base_no_gra_iva = 0.00
            base_imponible = 0.00  # Tarifa 0%
            base_imp_grav = 0.00   # Tarifa 15%
            base_imp_exe = 0.00
            iva_total = 0.00
            
            # Procesar totalConImpuestos
            total_con_impuestos = info_factura.find('totalConImpuestos')
            if total_con_impuestos is not None:
                for total_impuesto in total_con_impuestos.findall('totalImpuesto'):
                    try:
                        codigo = safe_get_text(total_impuesto.find('codigo'), 'codigo')
                        codigo_porcentaje = safe_get_text(total_impuesto.find('codigoPorcentaje'), 'codigoPorcentaje')
                        base_imponible_elem = total_impuesto.find('baseImponible')
                        valor_elem = total_impuesto.find('valor')
                        
                        if base_imponible_elem is None or valor_elem is None:
                            continue
                        
                        base_imponible_val = float(base_imponible_elem.text)
                        valor = float(valor_elem.text)
                        
                        if codigo == '2':  # IVA
                            if codigo_porcentaje == '0':  # 0% IVA
                                base_imponible += base_imponible_val
                            elif codigo_porcentaje == '4':  # 15% IVA
                                base_imp_grav += base_imponible_val
                                iva_total += valor
                            elif codigo_porcentaje == '6':  # No objeto de impuesto
                                base_no_gra_iva += base_imponible_val
                            elif codigo_porcentaje == '7':  # Exento
                                base_imp_exe += base_imponible_val
                    except (ValueError, AttributeError) as e:
                        # Log del error pero continuar procesando
                        print(f"Warning: Error procesando impuesto en {filename}: {e}")
                        continue
            
            return {
                'filename': filename,
                'ruc_emisor': ruc_emisor,
                'razon_social_emisor': razon_social,
                'establecimiento': establecimiento,
                'punto_emision': punto_emision,
                'secuencial': secuencial,
                'clave_acceso': clave_acceso,
                'fecha_emision': fecha_emision,
                'identificacion_comprador': identificacion_comprador,
                'total_sin_impuestos': total_sin_impuestos,
                'importe_total': importe_total,
                'base_no_gra_iva': round(base_no_gra_iva, 2),
                'base_imponible': round(base_imponible, 2),
                'base_imp_grav': round(base_imp_grav, 2),
                'base_imp_exe': round(base_imp_exe, 2),
                'iva_total': round(iva_total, 2)
            }
            
        except Exception as e:
            raise ValueError(f"Error procesando {filename}: {str(e)}")
    def extract_venta_from_xml(self, xml_content: str, filename: str) -> Dict:
        """
        Extrae información de una factura de venta (emitida)
        """
        try:
            # Reutilizar validación básica
            is_valid, validation_message = self.validate_xml_structure(xml_content, filename)
            if not is_valid:
                raise ValueError(validation_message)
            
            factura_root = self._get_xml_root(xml_content)
            
            info_tributaria = factura_root.find('infoTributaria')
            info_factura = factura_root.find('infoFactura')
            
            # Datos Cliente
            tipo_identificacion = info_factura.find('tipoIdentificacionComprador').text
            identificacion = info_factura.find('identificacionComprador').text
            parte_rel = "NO" # Default
            
            # Mapeo de tipo de identificación para ATS (Ventas)
            # En Factura Electrónica: 04=RUC, 05=Cédula, 06=Pasaporte, 07=Consumidor Final
            # En ATS Ventas: 04=RUC, 05=Cédula, 06=Pasaporte, 07=Consumidor Final
            # ¡Son los mismos códigos! No se requiere mapeo complejo, solo pasar el valor.
            
            tipo_id_ats = tipo_identificacion # Por defecto usar el mismo
            
            # Ajuste por si acaso el XML trae algo raro, pero 04, 05, 06, 07 son directos.
            if tipo_identificacion not in ["04", "05", "06", "07"]:
                 # Fallback logic si es necesario, o dejarlo pasar
                 pass
            
            # Totales
            total_sin_impuestos = float(info_factura.find('totalSinImpuestos').text)
            
            base_no_gra_iva = 0.0
            base_imponible = 0.0
            base_imp_grav = 0.0
            monto_iva = 0.0
            monto_ice = 0.0
            
            total_con_impuestos = info_factura.find('totalConImpuestos')
            if total_con_impuestos is not None:
                for total_impuesto in total_con_impuestos.findall('totalImpuesto'):
                    codigo = total_impuesto.find('codigo').text
                    codigo_porcentaje = total_impuesto.find('codigoPorcentaje').text
                    base = float(total_impuesto.find('baseImponible').text)
                    valor = float(total_impuesto.find('valor').text)
                    
                    if codigo == '2': # IVA
                        if codigo_porcentaje == '0':  # IVA 0%
                            base_imponible += base
                        elif codigo_porcentaje in ['2', '3', '4']:  # IVA 5%, 12%, 15%
                            base_imp_grav += base
                            monto_iva += valor
                        elif codigo_porcentaje == '6':  # No gravado
                            base_no_gra_iva += base
                    elif codigo == '3': # ICE
                        monto_ice += valor

            # MAPEO CRÍTICO: En ATS, código "01" es para COMPRAS, código "18" es para VENTAS
            # Ref: Ficha Técnica ATS SRI Tabla 4 + XML ejemplo agosto 2016
            cod_doc = info_tributaria.find('codDoc').text
            tipo_comp_ats = '18' if cod_doc == '01' else cod_doc  # Factura electrónica "01" → ATS ventas "18"

            return {
                'tpIdCliente': tipo_id_ats,
                'idCliente': identificacion,
                'parteRel': parte_rel,
                'tipoComprobante': tipo_comp_ats,  # Código mapeado para ATS ventas
                # CRÍTICO: DIMM 2016 no procesa correctamente tipoEmision='E' (bug)
                # Usar 'F' (Físico) para compatibilidad, aunque sea factura electrónica
                'tipoEmision': 'F',  # Forzar a 'F' para compatibilidad DIMM 2016
                'numeroComprobantes': 1,
                'baseNoGraIva': base_no_gra_iva,
                'baseImponible': base_imponible,
                'baseImpGrav': base_imp_grav,
                'montoIva': monto_iva,
                'montoIce': monto_ice,
                'valorRetIva': 0.0, # Se llena si hay retención recibida (no en factura emitida)
                'valorRetRenta': 0.0,
                'formaPago': "01", # Default
                'fechaEmision': info_factura.find('fechaEmision').text,
                'claveAcceso': info_tributaria.find('claveAcceso').text
            }
        except Exception as e:
            raise ValueError(f"Error procesando venta {filename}: {str(e)}")

    def extract_retencion_from_xml(self, xml_content: str, filename: str) -> Dict:
        """
        Extrae información de un comprobante de retención
        """
        try:
            is_valid, validation_message = self.validate_xml_structure(xml_content, filename)
            if not is_valid:
                raise ValueError(validation_message)
            
            retencion_root = self._get_xml_root(xml_content)
            
            info_tributaria = retencion_root.find('infoTributaria')
            info_comp_retencion = retencion_root.find('infoCompRetencion')
            
            return {
                'establecimiento': info_tributaria.find('estab').text,
                'puntoEmision': info_tributaria.find('ptoEmi').text,
                'secuencial': info_tributaria.find('secuencial').text,
                'autorizacion': info_tributaria.find('claveAcceso').text,
                'fechaEmision': info_comp_retencion.find('fechaEmision').text,
                'codSustento': "01" # Default, often needs manual adjustment or mapping
            }
        except Exception as e:
            raise ValueError(f"Error procesando retención {filename}: {str(e)}")
        """
        Procesa múltiples archivos XML con identificación de errores por archivo
        """
        facturas = []
        errors = []
        
        for i, (xml_content, filename) in enumerate(zip(xml_files, filenames)):
            try:
                factura_data = self.extract_factura_from_xml(xml_content, filename)
                facturas.append(factura_data)
            except Exception as e:
                error_msg = f"Archivo '{filename}': {str(e)}"
                errors.append(error_msg)
                print(f"Error procesando {filename}: {e}")
        
        if not facturas:
            raise ValueError("No se pudieron procesar facturas válidas. Revise los archivos XML.")
        
        # Detectar automáticamente mes y año
        primera_fecha = datetime.strptime(facturas[0]['fecha_emision'], '%d/%m/%Y')
        mes = primera_fecha.month
        anio = primera_fecha.year
        
        # Convertir facturas a detalles de compra
        compras = []
        for factura in facturas:
            try:
                detalle_compra = DetalleCompra(
                    codSustento="01",
                    tpIdProv="01",
                    idProv=factura['ruc_emisor'],
                    tipoComprobante="01",
                    parteRel="NO",
                    fechaRegistro=factura['fecha_emision'],
                    establecimiento=factura['establecimiento'],
                    puntoEmision=factura['punto_emision'],
                    secuencial=factura['secuencial'],
                    fechaEmision=factura['fecha_emision'],
                    autorizacion=factura['clave_acceso'],
                    baseNoGraIva=factura['base_no_gra_iva'],
                    baseImponible=factura['base_imponible'],
                    baseImpGrav=factura['base_imp_grav'],
                    baseImpExe=factura['base_imp_exe'],
                    montoIce=0.00,
                    montoIva=factura['iva_total'],
                    valRetBien10=0.00,
                    valRetServ20=0.00,
                    valorRetBienes=0.00,
                    valRetServ50=0.00,
                    valorRetServicios=0.00,
                    valRetServ100=0.00,
                    valorRetencionNc=0.00,
                    totbasesImpReemb=0.00,
                    pagoLocExt="01",
                    paisEfecPago="NA",
                    aplicConvDobTrib="NA",
                    pagExtSujRetNorLeg="NA"
                )
                compras.append(detalle_compra)
            except Exception as e:
                error_msg = f"Archivo '{factura['filename']}': Error creando detalle de compra: {str(e)}"
                errors.append(error_msg)
        
        # Crear datos del ATS
        ats_data = ATSData(
            tipoIDInformante="R",
            idInformante=empresa_info.ruc,
            razonSocial=empresa_info.razon_social,
            anio=anio,
            mes=mes,
            numEstabRuc="001",
            totalVentas=0.00,
            codigoOperativo="IVA",
            compras=compras
        )
        
    def process_and_save_to_db(self, xml_files: List[str], filenames: List[str], periodo_id: int, db: Session, doc_type: str = "compra") -> Tuple[int, List[str]]:
        """
        Procesa archivos XML y guarda la información en la base de datos
        doc_type: 'compra', 'venta', 'retencion'
        """
        from ..models.sql_models import FacturaCompra, FacturaVenta, Retencion
        
        processed_count = 0
        errors = []
        
        for i, (xml_content, filename) in enumerate(zip(xml_files, filenames)):
            try:
                # Detectar tipo de documento si no se especifica o validar
                # Por ahora asumimos que el endpoint llama con el tipo correcto
                
                if doc_type == "compra":
                    factura_data = self.extract_factura_from_xml(xml_content, filename)
                    
                    existing = db.query(FacturaCompra).filter(
                        FacturaCompra.autorizacion == factura_data['clave_acceso']
                    ).first()
                    
                    if existing:
                        errors.append(f"Archivo '{filename}': Factura ya registrada")
                        continue
                    
                    nueva_compra = FacturaCompra(
                        periodo_id=periodo_id,
                        codSustento="01",
                        tpIdProv="01",
                        idProv=factura_data['ruc_emisor'],
                        razon_social=factura_data['razon_social_emisor'],
                        tipoComprobante="01",
                        parteRel="NO",
                        fechaRegistro=factura_data['fecha_emision'],
                        establecimiento=factura_data['establecimiento'],
                        puntoEmision=factura_data['punto_emision'],
                        secuencial=factura_data['secuencial'],
                        fechaEmision=factura_data['fecha_emision'],
                        autorizacion=factura_data['clave_acceso'],
                        baseNoGraIva=factura_data['base_no_gra_iva'],
                        baseImponible=factura_data['base_imponible'],
                        baseImpGrav=factura_data['base_imp_grav'],
                        baseImpExe=factura_data['base_imp_exe'],
                        montoIce=0.00,
                        montoIva=factura_data['iva_total'],
                        pagoLocExt="01",
                        formaPago="01"
                    )
                    db.add(nueva_compra)
                    
                elif doc_type == "venta":
                    venta_data = self.extract_venta_from_xml(xml_content, filename)
                    
                    # Check existing logic for sales if needed (usually by authorization too if available)
                    
                    nueva_venta = FacturaVenta(
                        periodo_id=periodo_id,
                        tpIdCliente=venta_data['tpIdCliente'],
                        idCliente=venta_data['idCliente'],
                        parteRel=venta_data['parteRel'],
                        tipoComprobante=venta_data['tipoComprobante'],
                        tipoEmision=venta_data['tipoEmision'],
                        numeroComprobantes=venta_data['numeroComprobantes'],
                        baseNoGraIva=venta_data['baseNoGraIva'],
                        baseImponible=venta_data['baseImponible'],
                        baseImpGrav=venta_data['baseImpGrav'],
                        montoIva=venta_data['montoIva'],
                        montoIce=venta_data['montoIce'],
                        valorRetIva=venta_data['valorRetIva'],
                        valorRetRenta=venta_data['valorRetRenta'],
                        formaPago=venta_data['formaPago']
                    )
                    db.add(nueva_venta)

                elif doc_type == "retencion":
                    ret_data = self.extract_retencion_from_xml(xml_content, filename)
                    
                    nueva_retencion = Retencion(
                        periodo_id=periodo_id,
                        establecimiento=ret_data['establecimiento'],
                        puntoEmision=ret_data['puntoEmision'],
                        secuencial=ret_data['secuencial'],
                        autorizacion=ret_data['autorizacion'],
                        fechaEmision=ret_data['fechaEmision'],
                        codSustento=ret_data['codSustento']
                    )
                    db.add(nueva_retencion)
                
                processed_count += 1
                
            except Exception as e:
                error_msg = f"Archivo '{filename}': {str(e)}"
                errors.append(error_msg)
                print(f"Error procesando {filename}: {e}")
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error guardando en base de datos: {str(e)}")
            
        return processed_count, errors
