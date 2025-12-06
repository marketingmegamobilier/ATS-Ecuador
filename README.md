# Sistema de Gestión de ATS (Anexo Transaccional Simplificado)

![GitHub Stars](https://img.shields.io/github/stars/jonavez/ATS-Ecuador?style=social)
![GitHub Forks](https://img.shields.io/github/forks/jonavez/ATS-Ecuador?style=social)

Sistema completo para gestionar y generar el Anexo Transaccional Simplificado (ATS) del SRI de Ecuador. Carga facturas de compra, venta y retenciones en formato XML, valida la información automáticamente y genera el archivo ATS listo para ser enviado al Servicio de Rentas Internas.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Guía de Uso Detallada](#-guía-de-uso-detallada)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuir](#-contribuir)
- [Apoyo al Proyecto](#-apoyo-al-proyecto)
- [Contacto](#-contacto)
- [Licencia](#-licencia)

---

## ✨ Características

- ✅ **Gestión Multi-Periodo**: Administra múltiples periodos fiscales mensuales simultáneamente
- ✅ **Carga Automática de Datos**: Sube archivos XML y extrae automáticamente toda la información relevante
- ✅ **Validación Inteligente**: 
  - Detecta comprobantes duplicados por clave de acceso
  - Valida estructura XML según estándares del SRI
  - Verifica totales y cálculos de impuestos
- ✅ **Base de Datos Persistente**: Almacenamiento local con SQLite (sin necesidad de servidor externo)
- ✅ **Generación ATS**: Crea el archivo XML del ATS cumpliendo con las especificaciones del SRI
- ✅ **Interfaz Moderna**: Dashboard intuitivo con Material-UI y diseño responsivo
- ✅ **Soporte Completo**:
  - Facturas de Compra
  - Facturas de Venta
  - Retenciones en la Fuente
  - Notas de Crédito y Débito

---

## 🔧 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8 o superior** - [Descargar](https://www.python.org/downloads/)
- **Node.js 14 o superior** - [Descargar](https://nodejs.org/)
- **npm** (incluido con Node.js)
- **Git** - [Descargar](https://git-scm.com/)
- **Navegador Web Moderno** (Chrome, Firefox, Edge)

---

## 📥 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/jonavez/ATS-Ecuador.git
cd ATS-Ecuador
```

### Paso 2: Configuración del Backend

```bash
# Navegar a la carpeta del backend
cd backend

# Crear entorno virtual de Python (recomendado)
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Configuración del Frontend

```bash
# Desde la raíz del proyecto, navegar al frontend
cd frontend

# Instalar dependencias de Node
npm install
```

---

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` en la carpeta `backend` basándote en el archivo `.env.example`:

```bash
# backend/.env
DATABASE_URL=sqlite:///./ats.db
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

> **Nota**: El archivo `.env.example` contiene todas las variables necesarias con valores de ejemplo. Nunca subas tu archivo `.env` real al repositorio.

---

## 📖 Guía de Uso Detallada

### Iniciar el Sistema

#### 1. Iniciar el Backend

Abre una terminal en la carpeta `backend`:

```bash
# Asegúrate de tener el entorno virtual activado
uvicorn app.main:app --reload --port 8000
```

El servidor estará disponible en:
- API: `http://localhost:8000`
- Documentación interactiva: `http://localhost:8000/docs`

#### 2. Iniciar el Frontend

Abre **otra terminal** en la carpeta `frontend`:

```bash
npm start
```

La aplicación se abrirá automáticamente en `http://localhost:3000`

---

### Flujo de Trabajo Completo

#### 📊 **Paso 1: Acceder al Dashboard**

Al abrir la aplicación verás el dashboard principal con:
- Lista de periodos fiscales existentes
- Botón para crear nuevo periodo
- Resumen de comprobantes por periodo

#### ➕ **Paso 2: Crear un Nuevo Periodo**

1. Haz clic en el botón **"Nuevo Periodo"**
2. Completa el formulario:
   - **RUC de la Empresa**: Tu RUC (13 dígitos)
   - **Año**: Año fiscal (ej: 2025)
   - **Mes**: Mes fiscal (1-12)
3. Haz clic en **"Crear Periodo"**

#### 📄 **Paso 3: Cargar Facturas de Compra**

1. Selecciona el periodo haciendo clic en **"Gestionar"**
2. Ve a la pestaña **"Compras"**
3. **Arrastra y suelta** tus archivos XML de facturas de compra o haz clic para seleccionar archivos
4. El sistema procesará automáticamente cada archivo y extraerá:
   - Fecha de emisión
   - RUC y razón social del proveedor
   - Base imponible 0%, 12%, 15%
   - IVA calculado
   - Total de la factura
5. Verifica que la información se muestre correctamente en la tabla

#### 💼 **Paso 4: Cargar Facturas de Venta**

1. Ve a la pestaña **"Ventas"**
2. Sube tus facturas emitidas (mismo procedimiento que compras)
3. El sistema extraerá:
   - Datos del cliente
   - Bases imponibles por tarifa
   - IVA cobrado
   - Totales

#### 📝 **Paso 5: Cargar Retenciones**

1. Ve a la pestaña **"Retenciones"**
2. Sube los comprobantes de retención XML
3. Se extraerán los valores retenidos automáticamente

#### 📦 **Paso 6: Generar el ATS**

1. Una vez cargados todos los comprobantes del periodo
2. Haz clic en el botón **"Generar ATS"**
3. El sistema:
   - Validará todos los datos
   - Verificará que sumen correctamente
   - Generará el XML del ATS
4. Descarga el archivo `ATS_RUC_PERIODO.xml`
5. Sube este archivo al portal del SRI

#### ✅ **Paso 7: Validar con DIMM**

Opcionalmente, puedes validar el archivo generado con la herramienta DIMM del SRI antes de enviarlo:

1. Descarga DIMM desde el [sitio del SRI](https://www.sri.gob.ec)
2. Carga el archivo XML generado
3. Verifica que no haya errores
4. Procede a enviar tu declaración

---

## 📁 Estructura del Proyecto

```
ATS/
├── backend/                    # Servidor API Python/FastAPI
│   ├── app/
│   │   ├── main.py            # Punto de entrada de la aplicación
│   │   ├── models/            # Modelos de base de datos (SQLAlchemy)
│   │   │   ├── periodo.py
│   │   │   ├── compra.py
│   │   │   └── venta.py
│   │   ├── routers/           # Rutas de la API
│   │   │   ├── periodos.py
│   │   │   └── comprobantes.py
│   │   ├── services/          # Lógica de negocio
│   │   │   ├── xml_parser.py # Parseo de XML del SRI
│   │   │   └── ats_generator.py # Generación de ATS
│   │   └── database.py        # Configuración de base de datos
│   ├── requirements.txt       # Dependencias Python
│   ├── .env.example          # Ejemplo de variables de entorno
│   └── ats.db                # Base de datos SQLite (generada)
│
├── frontend/                  # Aplicación React
│   ├── public/
│   ├── src/
│   │   ├── components/       # Componentes reutilizables
│   │   │   ├── FileUploader.jsx
│   │   │   └── PeriodoCard.jsx
│   │   ├── pages/            # Páginas/Vistas
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PeriodoDetalle.jsx
│   │   │   └── ATSValidator.jsx
│   │   ├── services/         # Servicios API
│   │   │   └── api.js
│   │   └── App.jsx           # Componente principal
│   ├── package.json
│   └── .env.example
│
├── .gitignore                # Archivos ignorados por Git
└── README.md                 # Este archivo
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno y rápido
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM para gestión de base de datos
- **[SQLite](https://www.sqlite.org/)** - Base de datos embebida
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validación de datos
- **xml.etree.ElementTree** - Parseo de archivos XML

### Frontend
- **[React 18](https://react.dev/)** - Librería para interfaces de usuario
- **[Material-UI (MUI)](https://mui.com/)** - Componentes de interfaz
- **[Axios](https://axios-http.com/)** - Cliente HTTP
- **[React Router](https://reactrouter.com/)** - Enrutamiento

---

## 🔍 Solución de Problemas

### El backend no inicia

**Problema**: `ModuleNotFoundError` o errores de importación

**Solución**:
```bash
# Asegúrate de estar en el entorno virtual
cd backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Reinstala las dependencias
pip install -r requirements.txt
```

### El frontend no carga

**Problema**: Errores de dependencias en npm

**Solución**:
```bash
cd frontend
# Elimina node_modules y reinstala
rm -rf node_modules package-lock.json
npm install
```

### Error CORS al subir archivos

**Problema**: `Access-Control-Allow-Origin` error

**Solución**: Verifica que en `backend/.env` tengas:
```
CORS_ORIGINS=http://localhost:3000
```

### Los archivos XML no se procesan

**Problema**: El sistema no reconoce los archivos XML

**Solución**:
- Verifica que los archivos XML estén autorizados por el SRI
- Asegúrate de que tengan la estructura correcta
- Revisa los logs del backend para ver errores específicos

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Este proyecto está en desarrollo activo y necesita tu ayuda.

### ¿Cómo puedes ayudar?

1. **Reporta Bugs**: Si encuentras algún error, [abre un issue](https://github.com/jonavez/ATS-Ecuador/issues/new)
2. **Sugiere Funcionalidades**: ¿Tienes ideas para mejorar el sistema? [Compártelas aquí](https://github.com/jonavez/ATS-Ecuador/issues/new)
3. **Mejora la Documentación**: Si algo no está claro, ayuda a mejorarlo
4. **Contribuye con Código**: 
   - Haz fork del proyecto
   - Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
   - Haz commit de tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
   - Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
   - Abre un Pull Request

### Funcionalidades que nos gustaría agregar

- [ ] Exportación a Excel de reportes
- [ ] Gráficos y estadísticas de compras/ventas
- [ ] Soporte para notas de crédito/débito
- [ ] Integración con firmas electrónicas
- [ ] Validación automática con DIMM
- [ ] Múltiples empresas en una sola instancia
- [ ] Backup automático de la base de datos
- [ ] Modo oscuro en la interfaz

**¿Tienes más ideas?** [Déjanos saber en la sección de Issues](https://github.com/jonavez/ATS-Ecuador/issues)

---

## ⭐ Apoyo al Proyecto

Si este proyecto te ha sido útil, considera apoyarlo:

### Dale una Estrella ⭐

Si el sistema te ayudó a agilizar tu declaración del ATS, **dale una estrella en GitHub**. Esto ayuda a que más personas descubran el proyecto.

[![GitHub Stars](https://img.shields.io/github/stars/jonavez/ATS-Ecuador?style=social)](https://github.com/jonavez/ATS-Ecuador/stargazers)

### Comparte el Proyecto 📢

Ayuda a otros contadores y empresas ecuatorianas compartiendo este proyecto:
- En tus redes sociales
- Con colegas que puedan beneficiarse
- En grupos de contadores en Ecuador

### Contribuye 💻

Tu experiencia y conocimientos pueden hacer este sistema aún mejor. Revisa la sección [Contribuir](#-contribuir) para comenzar.

---

## 📞 Contacto

**Jonathan Vélez**
- 🌐 Sitio Web / Enlaces: [https://pid.la/jona](https://pid.la/jona)
- 💼 GitHub: [@jonavez](https://github.com/jonavez)

¿Preguntas, sugerencias o necesitas ayuda? Contáctame a través de los enlaces anteriores.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 🙏 Agradecimientos

Gracias a todos los que han contribuido y apoyado este proyecto. Especial reconocimiento a:
- La comunidad de desarrolladores ecuatorianos
- Todos los que han reportado bugs y sugerido mejoras
- Los contadores que han probado el sistema

---

**Desarrollado con ❤️ en Ecuador 🇪🇨**
