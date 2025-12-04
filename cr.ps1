# Script en PowerShell para crear la estructura de directorios y archivos del proyecto

# Definir el directorio raíz (directorio actual)
$rootDir = Get-Location

# Crear directorio backend y sus subdirectorios/archivos
New-Item -Path "$rootDir\backend\app" -ItemType Directory -Force
New-Item -Path "$rootDir\backend\app\__init__.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\__init__.py" -Value "# Inicialización del paquete de la aplicación backend"

New-Item -Path "$rootDir\backend\app\main.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\main.py" -Value "# Punto de entrada principal para la aplicación backend"

New-Item -Path "$rootDir\backend\app\models" -ItemType Directory -Force
New-Item -Path "$rootDir\backend\app\models\__init__.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\models\__init__.py" -Value "# Inicialización del paquete de modelos"
New-Item -Path "$rootDir\backend\app\models\ats_models.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\models\ats_models.py" -Value "# Definiciones de modelos ATS"

New-Item -Path "$rootDir\backend\app\services" -ItemType Directory -Force
New-Item -Path "$rootDir\backend\app\services\__init__.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\services\__init__.py" -Value "# Inicialización del paquete de servicios"
New-Item -Path "$rootDir\backend\app\services\file_processor.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\services\file_processor.py" -Value "# Lógica de procesamiento de archivos"
New-Item -Path "$rootDir\backend\app\services\xml_generator.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\services\xml_generator.py" -Value "# Lógica de generación de XML"

New-Item -Path "$rootDir\backend\app\utils" -ItemType Directory -Force
New-Item -Path "$rootDir\backend\app\utils\__init__.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\utils\__init__.py" -Value "# Inicialización del paquete de utilidades"
New-Item -Path "$rootDir\backend\app\utils\validators.py" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\utils\validators.py" -Value "# Utilidades de validación"

New-Item -Path "$rootDir\backend\app\templates" -ItemType Directory -Force
New-Item -Path "$rootDir\backend\app\templates\ats_template.xml" -ItemType File -Force
Set-Content -Path "$rootDir\backend\app\templates\ats_template.xml" -Value "<!-- Plantilla XML para ATS -->"

New-Item -Path "$rootDir\backend\requirements.txt" -ItemType File -Force
Set-Content -Path "$rootDir\backend\requirements.txt" -Value "# Dependencias de Python
fastapi
uvicorn
pydantic
"

# Crear directorio frontend y sus subdirectorios/archivos
New-Item -Path "$rootDir\frontend\public" -ItemType Directory -Force
New-Item -Path "$rootDir\frontend\src\components" -ItemType Directory -Force
New-Item -Path "$rootDir\frontend\src\services" -ItemType Directory -Force
New-Item -Path "$rootDir\frontend\src\types" -ItemType Directory -Force
New-Item -Path "$rootDir\frontend\src\App.tsx" -ItemType File -Force
Set-Content -Path "$rootDir\frontend\src\App.tsx" -Value "// Componente principal de la aplicación React
import React from 'react';

const App: React.FC = () => {
  return (
    <div>
      <h1>Bienvenido a la Aplicación ATS</h1>
    </div>
  );
};

export default App;"

New-Item -Path "$rootDir\frontend\package.json" -ItemType File -Force
Set-Content -Path "$rootDir\frontend\package.json" -Value '{
  "name": "ats-frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}'

New-Item -Path "$rootDir\frontend\tsconfig.json" -ItemType File -Force
Set-Content -Path "$rootDir\frontend\tsconfig.json" -Value '{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}'

# Crear README.md en el directorio raíz
New-Item -Path "$rootDir\README.md" -ItemType File -Force
Set-Content -Path "$rootDir\README.md" -Value "# Proyecto ATS

Este es un proyecto con una estructura de backend y frontend para un Sistema de Seguimiento de Candidatos (ATS).

## Backend
- Construido con Python y FastAPI
- Contiene modelos, servicios, utilidades y plantillas para la funcionalidad del ATS

## Frontend
- Construido con React y TypeScript
- Contiene componentes, servicios y tipos para la interfaz de usuario

## Configuración
1. **Backend**: Instala las dependencias con `pip install -r backend/requirements.txt` y ejecuta con `uvicorn backend.app.main:app --reload`
2. **Frontend**: Instala las dependencias con `npm install` en el directorio `frontend` y ejecuta con `npm start`
"

Write-Host "¡Estructura del proyecto creada exitosamente!"