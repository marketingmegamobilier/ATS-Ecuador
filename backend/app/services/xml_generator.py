from lxml import etree
from ..models.ats_models import ATSData
from typing import Dict, Any

class XMLGenerator:
    def __init__(self):
        self.namespace = None
    
    def generate_ats_xml(self, ats_data: ATSData) -> str:
        """
        Genera el XML del ATS con formas de pago incluidas
        """
        # Crear elemento raíz
        root = etree.Element("iva")
        
        # Información del informante
        etree.SubElement(root, "TipoIDInformante").text = ats_data.tipoIDInformante
        etree.SubElement(root, "IdInformante").text = ats_data.idInformante
        etree.SubElement(root, "razonSocial").text = ats_data.razonSocial
        etree.SubElement(root, "Anio").text = str(ats_data.anio)
        etree.SubElement(root, "Mes").text = str(ats_data.mes).zfill(2)
        etree.SubElement(root, "numEstabRuc").text = ats_data.numEstabRuc.zfill(3)
        etree.SubElement(root, "totalVentas").text = f"{ats_data.totalVentas:.2f}"
        etree.SubElement(root, "codigoOperativo").text = ats_data.codigoOperativo
        
        # Sección de compras
        if ats_data.compras:
            compras_element = etree.SubElement(root, "compras")
            
            for compra in ats_data.compras:
                detalle_compra = etree.SubElement(compras_element, "detalleCompras")
                
                etree.SubElement(detalle_compra, "codSustento").text = compra.codSustento
                etree.SubElement(detalle_compra, "tpIdProv").text = compra.tpIdProv
                etree.SubElement(detalle_compra, "idProv").text = compra.idProv
                etree.SubElement(detalle_compra, "tipoComprobante").text = compra.tipoComprobante
                etree.SubElement(detalle_compra, "parteRel").text = compra.parteRel
                etree.SubElement(detalle_compra, "fechaRegistro").text = compra.fechaRegistro
                etree.SubElement(detalle_compra, "establecimiento").text = compra.establecimiento
                etree.SubElement(detalle_compra, "puntoEmision").text = compra.puntoEmision
                etree.SubElement(detalle_compra, "secuencial").text = compra.secuencial
                etree.SubElement(detalle_compra, "fechaEmision").text = compra.fechaEmision
                etree.SubElement(detalle_compra, "autorizacion").text = compra.autorizacion
                etree.SubElement(detalle_compra, "baseNoGraIva").text = f"{compra.baseNoGraIva:.2f}"
                etree.SubElement(detalle_compra, "baseImponible").text = f"{compra.baseImponible:.2f}"
                etree.SubElement(detalle_compra, "baseImpGrav").text = f"{compra.baseImpGrav:.2f}"
                etree.SubElement(detalle_compra, "baseImpExe").text = f"{compra.baseImpExe:.2f}"
                etree.SubElement(detalle_compra, "montoIce").text = f"{compra.montoIce:.2f}"
                etree.SubElement(detalle_compra, "montoIva").text = f"{compra.montoIva:.2f}"
                etree.SubElement(detalle_compra, "valRetBien10").text = f"{compra.valRetBien10:.2f}"
                etree.SubElement(detalle_compra, "valRetServ20").text = f"{compra.valRetServ20:.2f}"
                etree.SubElement(detalle_compra, "valorRetBienes").text = f"{compra.valorRetBienes:.2f}"
                etree.SubElement(detalle_compra, "valRetServ50").text = f"{compra.valRetServ50:.2f}"
                etree.SubElement(detalle_compra, "valorRetServicios").text = f"{compra.valorRetServicios:.2f}"
                etree.SubElement(detalle_compra, "valRetServ100").text = f"{compra.valRetServ100:.2f}"
                etree.SubElement(detalle_compra, "valorRetencionNc").text = f"{compra.valorRetencionNc:.2f}"
                etree.SubElement(detalle_compra, "totbasesImpReemb").text = f"{compra.totbasesImpReemb:.2f}"
                
                # Pago exterior
                pago_exterior = etree.SubElement(detalle_compra, "pagoExterior")
                etree.SubElement(pago_exterior, "pagoLocExt").text = compra.pagoLocExt
                etree.SubElement(pago_exterior, "paisEfecPago").text = compra.paisEfecPago
                etree.SubElement(pago_exterior, "aplicConvDobTrib").text = compra.aplicConvDobTrib
                etree.SubElement(pago_exterior, "pagExtSujRetNorLeg").text = compra.pagExtSujRetNorLeg
                
                # ✅ AGREGAR FORMAS DE PAGO - SOLUCIÓN AL ERROR PRINCIPAL
                if compra.formas_pago:
                    formas_pago_element = etree.SubElement(detalle_compra, "formasDePago")
                    for forma_pago in compra.formas_pago:
                        etree.SubElement(formas_pago_element, "formaPago").text = forma_pago.formaPago

        # Sección de ventas
        if ats_data.ventas:
            ventas_element = etree.SubElement(root, "ventas")
            
            for venta in ats_data.ventas:
                detalle_venta = etree.SubElement(ventas_element, "detalleVentas")
                
                etree.SubElement(detalle_venta, "tpIdCliente").text = venta.tpIdCliente
                etree.SubElement(detalle_venta, "idCliente").text = venta.idCliente
                
                # Solo agregar parteRelVtas si tpIdCliente es 04, 05 o 06
                if venta.tpIdCliente in ["04", "05", "06"]:
                    etree.SubElement(detalle_venta, "parteRelVtas").text = venta.parteRel or "NO"
                
                etree.SubElement(detalle_venta, "tipoComprobante").text = venta.tipoComprobante
                
                # Mapeo de tipoEmision: 1 (Normal) -> E, 2 (Indisponibilidad) -> E, F (Física) -> F
                tipo_emision_ats = "E" if venta.tipoEmision in ["1", "2", "E"] else "F"
                etree.SubElement(detalle_venta, "tipoEmision").text = tipo_emision_ats
                
                etree.SubElement(detalle_venta, "numeroComprobantes").text = str(venta.numeroComprobantes)
                etree.SubElement(detalle_venta, "baseNoGraIva").text = f"{venta.baseNoGraIva:.2f}"
                etree.SubElement(detalle_venta, "baseImponible").text = f"{venta.baseImponible:.2f}"
                etree.SubElement(detalle_venta, "baseImpGrav").text = f"{venta.baseImpGrav:.2f}"
                etree.SubElement(detalle_venta, "montoIva").text = f"{venta.montoIva:.2f}"
                etree.SubElement(detalle_venta, "montoIce").text = f"{venta.montoIce:.2f}"
                etree.SubElement(detalle_venta, "valorRetIva").text = f"{venta.valorRetIva:.2f}"
                etree.SubElement(detalle_venta, "valorRetRenta").text = f"{venta.valorRetRenta:.2f}"
                
                # Formas de pago ventas
                if venta.formas_pago:
                    formas_pago_element = etree.SubElement(detalle_venta, "formasDePago")
                    for forma_pago in venta.formas_pago:
                        etree.SubElement(formas_pago_element, "formaPago").text = forma_pago.formaPago

        # Sección ventasEstablecimiento (SEPARADA - según XSD oficial)
        if ats_data.ventas:
            ventas_est_element = etree.SubElement(root, "ventasEstablecimiento")
            venta_est = etree.SubElement(ventas_est_element, "ventaEst")
            
            # Asumimos establecimiento 001 y sumamos todas las ventas
            etree.SubElement(venta_est, "codEstab").text = "001"
            etree.SubElement(venta_est, "ventasEstab").text = f"{ats_data.totalVentas:.2f}"
            etree.SubElement(venta_est, "ivaComp").text = "0.00"


        # Sección de retenciones (anulados o emitidos) - TODO: Implementar si se requiere
        # Por ahora solo ventas y compras son lo principal solicitado
        
        # Convertir a string con formato
        xml_string = etree.tostring(
            root, 
            pretty_print=True, 
            xml_declaration=True, 
            encoding='UTF-8'
        ).decode('utf-8')
        
        return xml_string
    
    def validate_xml_against_xsd(self, xml_content: str, xsd_path: str = None) -> bool:
        """
        Valida el XML generado contra el esquema XSD del SRI
        """
        try:
            xml_doc = etree.fromstring(xml_content.encode('utf-8'))
            
            if xsd_path:
                with open(xsd_path, 'r', encoding='utf-8') as xsd_file:
                    xsd_doc = etree.parse(xsd_file)
                    xsd_schema = etree.XMLSchema(xsd_doc)
                    return xsd_schema.validate(xml_doc)
            
            return True
            
        except Exception as e:
            print(f"Error validando XML: {e}")
            return False
