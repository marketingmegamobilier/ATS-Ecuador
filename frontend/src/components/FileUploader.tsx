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
import { uploadCompras, uploadVentas, uploadRetenciones } from '../services/api';

interface FileUploaderProps {
  onUploadSuccess: () => void;
  periodoId: number;
  disabled?: boolean;
  docType?: 'compra' | 'venta' | 'retencion';
}

const FileUploader: React.FC<FileUploaderProps> = ({
  onUploadSuccess,
  periodoId,
  disabled = false,
  docType = 'compra'
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setUploadedFiles(acceptedFiles);
    setIsLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      let response;
      if (docType === 'compra') {
        response = await uploadCompras(acceptedFiles, periodoId);
      } else if (docType === 'venta') {
        response = await uploadVentas(acceptedFiles, periodoId);
      } else if (docType === 'retencion') {
        response = await uploadRetenciones(acceptedFiles, periodoId);
      }

      setSuccessMsg(`Procesados ${response.processed} archivos correctamente.`);
      if (response.errors && response.errors.length > 0) {
        setError(`Algunos archivos tuvieron errores: ${response.errors.join(', ')}`);
      }
      onUploadSuccess();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error procesando los archivos XML';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [onUploadSuccess, periodoId, docType]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/xml': ['.xml'],
      'application/xml': ['.xml'],
    },
    multiple: true,
    disabled: disabled,
  });

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        📄 Subir {docType === 'compra' ? 'Facturas de Compra' : docType === 'venta' ? 'Facturas de Venta' : 'Retenciones'} (XML)
      </Typography>

      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
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
          </Box>
        ) : (
          <Box>
            <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive
                ? 'Suelta las facturas XML aquí'
                : 'Arrastra facturas XML o haz clic para seleccionar'}
            </Typography>
          </Box>
        )}
      </Box>

      {successMsg && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {successMsg}
        </Alert>
      )}

      {error && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Paper>
  );
};

export default FileUploader;
