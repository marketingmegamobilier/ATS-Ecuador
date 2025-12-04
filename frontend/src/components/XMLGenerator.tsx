import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Button,
  Box,
  Alert,
  CircularProgress,
  ButtonGroup,
} from '@mui/material';
import {
  Download,
  Code,
  CheckCircle,
  Archive,
} from '@mui/icons-material';
import { ATSData } from '../types';

interface XMLGeneratorProps {
  atsData: ATSData;
}

const XMLGenerator: React.FC<XMLGeneratorProps> = ({ atsData }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!atsData) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Alert severity="error">
          <Typography variant="body2">
            Error: No hay datos del ATS disponibles para generar el XML.
          </Typography>
        </Alert>
      </Paper>
    );
  }

  if (!atsData.mes || !atsData.anio || !atsData.idInformante) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Alert severity="error">
          <Typography variant="body2">
            Error: Los datos del ATS están incompletos. Faltan campos obligatorios (mes, año, o RUC).
          </Typography>
        </Alert>
      </Paper>
    );
  }

  const generateXML = async (atsData: ATSData): Promise<Blob> => {
    const response = await fetch('http://localhost:8000/generate-xml', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(atsData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error generando XML');
    }
    
    return response.blob();
  };

  const generateZIP = async (atsData: ATSData): Promise<Blob> => {
    const response = await fetch('http://localhost:8000/generate-xml-zip', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(atsData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error generando ZIP');
    }
    
    return response.blob();
  };

  const handleDownload = async (format: 'xml' | 'zip') => {
    setIsGenerating(true);
    setError(null);
    setSuccess(false);

    try {
      let blob: Blob;
      let filename: string;
      
      if (format === 'xml') {
        blob = await generateXML(atsData);
        filename = `AT${atsData.mes.toString().padStart(2, '0')}${atsData.anio}.xml`;
      } else {
        blob = await generateZIP(atsData);
        filename = `AT${atsData.mes.toString().padStart(2, '0')}${atsData.anio}.zip`;
      }
      
      // Crear URL para descarga
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(true);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error en la descarga';
      setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        🔧 Generar ATS para el SRI
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          El archivo será generado según las especificaciones técnicas del SRI
          y estará listo para ser subido al portal en línea.
        </Typography>
        
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2">
            <strong>Archivo a generar:</strong> AT{atsData.mes.toString().padStart(2, '0')}{atsData.anio}
          </Typography>
          <Typography variant="body2">
            <strong>Período:</strong> {atsData.mes}/{atsData.anio}
          </Typography>
          <Typography variant="body2">
            <strong>Total compras:</strong> {atsData.compras?.length || 0}
          </Typography>
        </Box>
      </Box>

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <CheckCircle sx={{ mr: 1 }} />
            <Typography variant="body2">
              ¡Archivo descargado exitosamente!
            </Typography>
          </Box>
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="body2">
            {error}
          </Typography>
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <ButtonGroup variant="contained" size="large">
          <Button
            startIcon={isGenerating ? <CircularProgress size={20} /> : <Download />}
            onClick={() => handleDownload('xml')}
            disabled={isGenerating}
            sx={{ minWidth: 150 }}
          >
            {isGenerating ? 'Generando...' : 'XML'}
          </Button>
          <Button
            startIcon={isGenerating ? <CircularProgress size={20} /> : <Archive />}
            onClick={() => handleDownload('zip')}
            disabled={isGenerating}
            sx={{ minWidth: 150 }}
          >
            {isGenerating ? 'Generando...' : 'ZIP'}
          </Button>
        </ButtonGroup>

        <Button
          variant="outlined"
          startIcon={<Code />}
          href="https://www.sri.gob.ec/formularios-e-instructivos1"
          target="_blank"
          rel="noopener noreferrer"
        >
          Documentación SRI
        </Button>
      </Box>

      <Box sx={{ p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
        <Typography variant="body2" color="info.contrastText">
          <strong>💡 Siguiente paso:</strong> Una vez descargado, puedes subir el archivo
          al portal del SRI en la sección "Anexos" → "Envío y consulta de anexos" → 
          "Anexo Transaccional Simplificado".
        </Typography>
      </Box>
    </Paper>
  );
};

export default XMLGenerator;
