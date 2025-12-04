import os
from lxml import etree
from typing import List, Dict, Any, Tuple
import zipfile
import io

class ATSValidatorService:
    def __init__(self, xsd_path: str = "app/resources/ats.xsd"):
        self.xsd_path = xsd_path

    def validate_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Main validation entry point. Handles ZIP or XML.
        """
        errors = []
        warnings = []
        stats = {}
        checklist = []
        
        try:
            # Detect if ZIP
            if filename.lower().endswith('.zip'):
                with zipfile.ZipFile(io.BytesIO(file_content)) as z:
                    xml_files = [f for f in z.namelist() if f.lower().endswith('.xml')]
                    if not xml_files:
                        return {"valid": False, "errors": [{"tipo": "estructura", "mensaje": "El ZIP no contiene archivos XML"}]}
                    
                    # Validate first XML found (ATS usually has one main XML)
                    xml_filename = xml_files[0]
                    xml_data = z.read(xml_filename)
                    return self._validate_xml_content(xml_data, xml_filename)
            else:
                # Assume XML
                return self._validate_xml_content(file_content, filename)

        except Exception as e:
            return {
                "valid": False, 
                "errors": [{"tipo": "crítico", "mensaje": f"Error procesando archivo: {str(e)}"}],
                "warnings": [],
                "stats": {},
                "checklist": []
            }

    def _validate_xml_content(self, xml_content: bytes, filename: str) -> Dict[str, Any]:
        errors = []
        warnings = []
        checklist = []
        stats = {
            "total_compras": 0,
            "total_ventas": 0,
            "total_retenciones": 0,
            "total_anulados": 0
        }
        
        # 1. Structural Validation (XSD)
        xsd_valid, xsd_errors = self._validate_xsd(xml_content)
        if not xsd_valid:
            errors.extend(xsd_errors)
            checklist.append({"regla": "Validación Estructural XSD", "estado": "FALLÓ", "detalle": "El archivo no cumple con el esquema XSD oficial."})
        else:
            checklist.append({"regla": "Validación Estructural XSD", "estado": "PASÓ", "detalle": "Estructura XML correcta."})
        
        # 2. Business Rules Validation
        try:
            root = etree.fromstring(xml_content)
            biz_errors, biz_warnings, biz_stats, biz_checklist = self._validate_business_rules(root)
            errors.extend(biz_errors)
            warnings.extend(biz_warnings)
            stats.update(biz_stats)
            checklist.extend(biz_checklist)
        except etree.XMLSyntaxError:
            if not errors: # If XSD didn't catch it (unlikely)
                errors.append({"tipo": "estructura", "mensaje": "XML mal formado, no se puede analizar"})
        
        return {
            "valid": len(errors) == 0,
            "filename": filename,
            "errors": errors,
            "warnings": warnings,
            "stats": stats,
            "checklist": checklist
        }

    def _validate_xsd(self, xml_content: bytes) -> Tuple[bool, List[Dict]]:
        if not os.path.exists(self.xsd_path):
            return True, [] # Skip if XSD not found (dev mode)
            
        try:
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.fromstring(xml_content)
            
            if schema.validate(doc):
                return True, []
            
            errors = []
            for error in schema.error_log:
                errors.append({
                    "tipo": "estructura",
                    "modulo": "XSD",
                    "mensaje": error.message,
                    "linea": error.line
                })
            return False, errors
        except Exception as e:
            return False, [{"tipo": "estructura", "mensaje": f"Error validando XSD: {str(e)}"}]

    def _validate_business_rules(self, root: etree.Element) -> Tuple[List[Dict], List[Dict], Dict, List[Dict]]:
        errors = []
        warnings = []
        checklist = []
        stats = {"total_compras": 0, "total_ventas": 0}
        
        # Helper to get text safely
        def get_text(elem, tag, default=""):
            found = elem.find(tag)
            return found.text if found is not None else default

        # --- Header Validations ---
        total_ventas_header = float(get_text(root, "totalVentas", "0"))
        
        # Rule: tipoEmision must be empty or absent (CRITICAL)
        tipo_emision_header = get_text(root, "tipoEmision")
        if tipo_emision_header:
             errors.append({
                "tipo": "negocio",
                "modulo": "cabecera",
                "mensaje": "El campo 'tipoEmision' debe estar vacío o no enviarse.",
                "referencia": {"valor_encontrado": tipo_emision_header}
            })
             checklist.append({"regla": "Campo tipoEmision vacío", "estado": "FALLÓ", "detalle": "El campo contiene valor."})
        else:
             checklist.append({"regla": "Campo tipoEmision vacío", "estado": "PASÓ", "detalle": "Campo correcto."})

        # Rule: RUC Informante
        ruc_informante = get_text(root, "IdInformante")
        if len(ruc_informante) != 13 or not ruc_informante.endswith("001"):
             errors.append({
                "tipo": "negocio",
                "modulo": "cabecera",
                "mensaje": f"RUC del informante '{ruc_informante}' inválido (debe tener 13 dígitos y terminar en 001)",
                "referencia": {"ruc": ruc_informante}
            })
             checklist.append({"regla": "RUC Informante Válido", "estado": "FALLÓ", "detalle": "RUC incorrecto."})
        else:
             checklist.append({"regla": "RUC Informante Válido", "estado": "PASÓ", "detalle": "RUC válido."})

        # --- Compras Validations ---
        compras = root.find("compras")
        compras_valid = True
        if compras is not None:
            detalles = compras.findall("detalleCompras")
            stats["total_compras"] = len(detalles)
            
            for i, detalle in enumerate(detalles):
                ref = {
                    "secuencial": get_text(detalle, "secuencial"),
                    "codSustento": get_text(detalle, "codSustento")
                }
                
                # Rule: codSustento validity
                cod_sustento = get_text(detalle, "codSustento")
                if cod_sustento not in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]:
                     errors.append({
                        "tipo": "negocio",
                        "modulo": "compras",
                        "mensaje": f"Código de sustento '{cod_sustento}' no es válido o común",
                        "referencia": ref
                    })
                     compras_valid = False

                # Rule: Base Imponible > 0 check (at least one base must be > 0)
                bases = [
                    float(get_text(detalle, "baseNoGraIva", "0")),
                    float(get_text(detalle, "baseImponible", "0")),
                    float(get_text(detalle, "baseImpGrav", "0")),
                    float(get_text(detalle, "baseImpExe", "0"))
                ]
                if sum(bases) <= 0:
                    errors.append({
                        "tipo": "negocio",
                        "modulo": "compras",
                        "mensaje": "La suma de bases imponibles es 0.00",
                        "referencia": ref
                    })
                    compras_valid = False
                
                # Rule: IVA Calculation Check (Approx 15% or 12%)
                base_grav = float(get_text(detalle, "baseImpGrav", "0"))
                monto_iva = float(get_text(detalle, "montoIva", "0"))
                if base_grav > 0:
                    # Check against 15% (current) and 12% (old)
                    iva_15 = base_grav * 0.15
                    iva_12 = base_grav * 0.12
                    if abs(monto_iva - iva_15) > 0.05 and abs(monto_iva - iva_12) > 0.05:
                         warnings.append({
                            "tipo": "negocio",
                            "modulo": "compras",
                            "mensaje": f"Monto IVA ({monto_iva}) no coincide con 12% ({iva_12:.2f}) ni 15% ({iva_15:.2f}) de la base gravada ({base_grav})",
                            "referencia": ref
                        })

        
        checklist.append({
            "regla": "Validación de Compras", 
            "estado": "PASÓ" if compras_valid else "FALLÓ", 
            "detalle": "Verificación de códigos de sustento, bases imponibles e IVA."
        })

        # --- Ventas Validations ---
        ventas = root.find("ventas")
        sum_ventas_bases = 0.0
        ventas_valid = True
        
        if ventas is not None:
            detalles = ventas.findall("detalleVentas")
            stats["total_ventas"] = len(detalles)
            
            for i, detalle in enumerate(detalles):
                ref = {
                    "idCliente": get_text(detalle, "idCliente"),
                    "tipoComprobante": get_text(detalle, "tipoComprobante")
                }
                
                # Rule: Validate ID Type and Value
                tp_id = get_text(detalle, "tpIdCliente")
                id_cliente = get_text(detalle, "idCliente")
                parte_rel = get_text(detalle, "parteRelVtas")

                # Validar tpIdCliente permitido en ventas
                if tp_id not in ["04", "05", "06", "07"]:
                     errors.append({
                        "tipo": "negocio",
                        "modulo": "ventas",
                        "mensaje": f"Tipo de identificación '{tp_id}' no es válido para ventas (usar 04, 05, 06, 07)",
                        "referencia": ref
                    })
                     ventas_valid = False

                # Validar parteRelVtas
                if parte_rel:
                    if tp_id not in ["04", "05", "06"]:
                         errors.append({
                            "tipo": "negocio",
                            "modulo": "ventas",
                            "mensaje": f"parteRelVtas no debe enviarse para tipo de identificación '{tp_id}'",
                            "referencia": ref
                        })
                         ventas_valid = False

                if tp_id == "05" and len(id_cliente) != 10:
                     errors.append({
                        "tipo": "negocio",
                        "modulo": "ventas",
                        "mensaje": f"Cédula '{id_cliente}' debe tener 10 dígitos",
                        "referencia": ref
                    })
                     ventas_valid = False
                if tp_id == "04" and len(id_cliente) != 13:
                     errors.append({
                        "tipo": "negocio",
                        "modulo": "ventas",
                        "mensaje": f"RUC '{id_cliente}' debe tener 13 dígitos",
                        "referencia": ref
                    })
                     ventas_valid = False

                # Sum bases for header check
                base_imp = float(get_text(detalle, "baseImponible", "0"))
                base_grav = float(get_text(detalle, "baseImpGrav", "0"))
                base_nogra = float(get_text(detalle, "baseNoGraIva", "0"))
                sum_ventas_bases += (base_imp + base_grav + base_nogra)

        checklist.append({
            "regla": "Validación de Ventas", 
            "estado": "PASÓ" if ventas_valid else "FALLÓ", 
            "detalle": "Verificación de RUC/Cédula y estructura de ventas."
        })

        # Rule: Header totalVentas vs Sum of Details
        # Allow small float difference
        math_valid = True
        if abs(total_ventas_header - sum_ventas_bases) > 0.02:
            errors.append({
                "tipo": "negocio",
                "modulo": "cabecera",
                "mensaje": f"Total Ventas en cabecera ({total_ventas_header}) no coincide con suma de detalles ({sum_ventas_bases})",
                "referencia": {"diferencia": f"{total_ventas_header - sum_ventas_bases:.2f}"}
            })
            math_valid = False
            
        checklist.append({
            "regla": "Consistencia Matemática", 
            "estado": "PASÓ" if math_valid else "FALLÓ", 
            "detalle": "Suma de ventas coincide con el total declarado en cabecera.",
            "fuente": "Ficha Técnica ATS v1.1.1"
        })

        return errors, warnings, stats, checklist
