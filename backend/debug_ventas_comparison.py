"""
Script de debugging para analizar el problema de ventas en ATS
Compara XML generado vs XML de ejemplo del SRI
"""

# XML DE EJEMPLO SRI (Agosto 2016)
xml_ejemplo_sri_ventas = """
<detalleVentas>
    <tpIdCliente>04</tpIdCliente>
    <idCliente>0602846586001</idCliente>
    <parteRelVtas>SI</parteRelVtas>
    <tipoComprobante>18</tipoComprobante>
    <tipoEmision>F</tipoEmision>           ← FÍSICO
    <numeroComprobantes>145</numeroComprobantes>
    <baseNoGraIva>1000.00</baseNoGraIva>
    <baseImponible>1000.00</baseImponible>  ← Mismo valor que baseImpGrav
    <baseImpGrav>1000.00</baseImpGrav>
    <montoIva>140.00</montoIva>  ← IVA 14% (período 2016)
    <compensaciones>
        <compensacion>
            <tipoCompe>01</tipoCompe>
            <monto>60</monto>
        </compensacion>
    </compensaciones>
    <montoIce>12.30</ montoIce>
    <valorRetIva>40</valorRetIva>
    <valorRetRenta>40</valorRetRenta>
    <formasDePago>
        <formaPago>01</formaPago>
    </formasDePago>
</detalleVentas>
"""

# NUESTRO XML (Julio 2025)
xml_nuestro_ventas = """
<detalleVentas>
    <tpIdCliente>04</tpIdCliente>
    <idCliente>2200520399001</idCliente>
    <parteRelVtas>NO</parteRelVtas>
    <tipoComprobante>18</tipoComprobante>
    <tipoEmision>E</tipoEmision>            ← ELECTRÓNICO
    <numeroComprobantes>1</numeroComprobantes>
    <baseNoGraIva>0.00</baseNoGraIva>
    <baseImponible>0.00</baseImponible>     ← CERO (reverted fix)
    <baseImpGrav>1200.00</baseImpGrav>
    <montoIva>180.00</montoIva>  ← IVA 15% (período 2025)
    <montoIce>0.00</montoIce>
    <valorRetIva>0.00</valorRetIva>
    <valorRetRenta>0.00</valorRetRenta>
    <formasDePago>
        <formaPago>01</formaPago>
    </formasDePago>
</detalleVentas>
"""

# DIFERENCIAS CLAVE:
diferencias = {
    "tipoEmision": {
        "SRI_ejemplo": "F (Facturación Física)",
        "Nuestro": "E (Facturación Electrónica)",
        "¿Problema?": "DIMM 2016 puede no reconocer 'E'"
    },
    "campos_duplicados_en_ejemplo": {
        "baseNoGraIva": "1000.00",
        "baseImponible": "1000.00",  # Mismo valor
        "baseImpGrav": "1000.00",     # Mismo valor
        "Interpretación": "¿Los tres siempre deben tener el mismo valor cuando solo hay un tipo de IVA?"
    },
    "nuestro_problema": {
        "baseImponible": "0.00 (IVA 0% no tenemos)",
        "baseImpGrav": "1200.00 (IVA 15% sí tenemos)",
        "DIMM_error": "Suma ventas = 0.00",
        "Hipótesis": "DIMM 2016 solo reconoce  ventas si baseImponible > 0?"
    }
}

print("=" * 80)
print("ANÁLISIS XML EJEMPLO SRI VS NUESTRO XML")
print("=" * 80)

for key, value in diferencias.items():
    print(f"\n{key}:")
    if isinstance(value, dict):
        for k, v in value.items():
            print(f"  {k}: {v}")
    else:
        print(f"  {value}")

print("\n" + "=" * 80)
print("HIPÓTESIS:")
print("=" * 80)
print("""
1. DIMM 2016 puede requerir baseImponible > 0 para sumar ventas
2. DIMM 2016 puede no reconocer tipoEmision='E' (electrónico)
3. El ejemplo SRI muestra los 3 campos con el mismo valor (¿siempre igual?)

SIGUIENTE PASO: Probar con baseImponible = baseImpGrav = baseNoGraIva
""")
