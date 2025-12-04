from app.services.xml_processor import XMLProcessor
import xml.etree.ElementTree as ET

xml_content = """<factura id="comprobante" version="1.1.0">
<infoTributaria>
<ambiente>2</ambiente>
<tipoEmision>1</tipoEmision>
<razonSocial>PIDAAPP S.A.S.</razonSocial>
<nombreComercial>PIDA</nombreComercial>
<ruc>1793212860001</ruc>
<claveAcceso>2907202501179321286000120010010000000047736108116</claveAcceso>
<codDoc>01</codDoc>
<estab>001</estab>
<ptoEmi>001</ptoEmi>
<secuencial>000000004</secuencial>
<dirMatriz>Barrio: CHECA Calle: AV QUITO Numero: SN Interseccion: CRISTOBAL ERAZO </dirMatriz>
<contribuyenteRimpe>CONTRIBUYENTE RÉGIMEN RIMPE</contribuyenteRimpe>
</infoTributaria>
<infoFactura>
<fechaEmision>29/07/2025</fechaEmision>
<dirEstablecimiento>Barrio: CHECA Calle: AV QUITO Numero: SN Interseccion: CRISTOBAL ERAZO </dirEstablecimiento>
<obligadoContabilidad>SI</obligadoContabilidad>
<tipoIdentificacionComprador>04</tipoIdentificacionComprador>
<razonSocialComprador>ALVARADO MERINO CESIA PAULINA</razonSocialComprador>
<identificacionComprador>2200520399001</identificacionComprador>
<totalSinImpuestos>1200.00</totalSinImpuestos>
<totalDescuento>0.00</totalDescuento>
<totalConImpuestos>
<totalImpuesto>
<codigo>2</codigo>
<codigoPorcentaje>4</codigoPorcentaje>
<baseImponible>1200.00</baseImponible>
<valor>180.00</valor>
</totalImpuesto>
</totalConImpuestos>
<propina>0</propina>
<importeTotal>1380.00</importeTotal>
<moneda>DOLAR</moneda>
<pagos>
<pago>
<formaPago>01</formaPago>
<total>1380.00</total>
<plazo>30</plazo>
<unidadTiempo>Dias</unidadTiempo>
</pago>
</pagos>
</infoFactura>
<detalles>
<detalle>
<codigoPrincipal>002</codigoPrincipal>
<descripcion>SERVICIO DE ENVIO DE PAQUETERIA</descripcion>
<cantidad>2.0</cantidad>
<precioUnitario>600</precioUnitario>
<descuento>0.00</descuento>
<precioTotalSinImpuesto>1200.00</precioTotalSinImpuesto>
<impuestos>
<impuesto>
<codigo>2</codigo>
<codigoPorcentaje>4</codigoPorcentaje>
<tarifa>15.0</tarifa>
<baseImponible>1200.00</baseImponible>
<valor>180.00</valor>
</impuesto>
</impuestos>
</detalle>
</detalles>
<infoAdicional>
<campoAdicional nombre="Email">cesiapaulina2000@gmail.com</campoAdicional>
</infoAdicional>
</factura>"""

processor = XMLProcessor()
try:
    data = processor.extract_venta_from_xml(xml_content, "test_venta.xml")
    print("Extraction Successful:")
    print(f"Base Imponible Gravada: {data['baseImpGrav']}")
    print(f"Monto IVA: {data['montoIva']}")
    print(f"Tipo ID Cliente: {data['tpIdCliente']}")
except Exception as e:
    print(f"Error: {e}")
