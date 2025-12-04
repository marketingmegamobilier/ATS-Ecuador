from app.services.xml_generator import XMLGenerator
from app.models.ats_models import ATSData, DetalleVenta, FormaPago

# Dummy Data
ats_data = ATSData(
    idInformante="1793212860001",
    razonSocial="TEST EMPRESA",
    anio=2025,
    mes=7,
    numEstabRuc="001",
    totalVentas=1200.00,
    codigoOperativo="IVA",
    compras=[],
    ventas=[
        DetalleVenta(
            tpIdCliente="04",
            idCliente="2200520399001",
            parteRel="NO",
            tipoComprobante="01",
            tipoEmision="F",
            numeroComprobantes=1,
            baseNoGraIva=0.0,
            baseImponible=0.0,
            baseImpGrav=1200.00,
            montoIva=180.00,
            montoIce=0.0,
            valorRetIva=0.0,
            valorRetRenta=0.0,
            formas_pago=[FormaPago(formaPago="01", total=1380.00)]
        )
    ]
)

generator = XMLGenerator()
xml = generator.generate_ats_xml(ats_data)
print(xml)
