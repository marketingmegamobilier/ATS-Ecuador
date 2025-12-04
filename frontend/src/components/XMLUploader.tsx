import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  CheckCircle,
} from '@mui/icons-material';
import { uploadXMLFiles } from '../services/api';
import { ProcessResponse } from '../types';

interface XMLUploaderProps {
  onFileProcessed: (data: ProcessResponse) => void;
  empresaRuc: string;
  empresaRazonSocial: string;
  disabled?: boolean;
}

const XMLUploader: React.FC<XMLUploaderProps> = ({ 
  onFileProcessed, 
  empresaRuc, 
  empresaRazonSocial,
  disabled = false 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    if (!empresaRuc || !empresaRazonSocial) {
      setError('Debe completar la información de la empresa antes de subir archivos');
      return;
    }

    setUploadedFiles(acceptedFiles);
    setIsLoading(true);
    setError(null);

    try {
      const response = await uploadXMLFiles(acceptedFiles, empresaRuc, empresaRazonSocial);
      onFileProcessed(response);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error procesando las facturas XML';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [onFileProcessed, empresaRuc, empresaRazonSocial]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
    },
    multiple: true,
    disabled: disabled || !empresaRuc || !empresaRazonSocial,
  });

  const canUpload = empresaRuc && empresaRazonSocial && !disabled;

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        📄 Subir Facturas XML (Recomendado)
      </Typography>
      
      <Alert severity="success" sx={{ mb: 2 }}>
        <Typography variant="body2">
          <strong>✅ Método Óptimo:</strong> Este método extrae automáticamente los valores exactos 
          de bases tributarias de cada factura XML, garantizando 100% de precisión en el ATS.
        </Typography>
      </Alert>

      {!canUpload && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2">
            Complete la información de la empresa antes de subir archivos
          </Typography>
        </Alert>
      )}
      
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: canUpload && isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: canUpload ? 'pointer' : 'not-allowed',
          bgcolor: canUpload && isDragActive ? 'action.hover' : 'background.paper',
          opacity: canUpload ? 1 : 0.5,
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: canUpload ? 'primary.main' : 'grey.300',
            bgcolor: canUpload ? 'action.hover' : 'background.paper',
          },
        }}
      >
        <input {...getInputProps()} />
        
        {isLoading ? (
          <Box>
            <CircularProgress size={48} sx={{ mb: 2 }} />
            <Typography variant="body1">
              Procesando facturas XML...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Extrayendo bases tributarias exactas...
            </Typography>
          </Box>
        ) : (
          <Box>
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {canUpload
                ? (isDragActive
                    ? 'Suelta las facturas XML aquí'
                    : 'Arrastra facturas XML o haz clic para seleccionar')
                : 'Complete la información de la empresa primero'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Formato: Archivos XML de facturas autorizadas por el SRI
            </Typography>
          </Box>
        )}
      </Box>

      {uploadedFiles.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Archivos seleccionados ({uploadedFiles.length}):
          </Typography>
          <List dense>
            {uploadedFiles.slice(0, 5).map((file, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Description color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary={file.name}
                  secondary={`${(file.size / 1024).toFixed(1)} KB`}
                />
                <Chip
                  icon={<CheckCircle />}
                  label="XML"
                  size="small"
                  color="success"
                />
              </ListItem>
            ))}
            {uploadedFiles.length > 5 && (
              <ListItem>
                <ListItemText 
                  primary={`... y ${uploadedFiles.length - 5} archivos más`}
                  sx={{ fontStyle: 'italic' }}
                />
              </ListItem>
            )}
          </List>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="body2">
            {error}
          </Typography>
        </Alert>
      )}
    </Paper>
  );
};

export default XMLUploader;
