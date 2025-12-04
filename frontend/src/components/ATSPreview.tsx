import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Business,
  DateRange,
  Receipt,
  AttachMoney,
  Warning,
  Info,
} from '@mui/icons-material';
import { ProcessResponse } from '../types';

interface ATSPreviewProps {
  data: ProcessResponse;
}

const ATSPreview: React.FC<ATSPreviewProps> = ({ data }) => {
  // Validación defensiva: Verificar que data y data.data existen
  if (!data || !data.data) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 200 }}>
          <CircularProgress />
          <Typography variant="body1" sx={{ ml: 2 }}>
            Cargando datos del ATS...
          </Typography>
        </Box>
      </Paper>
    );
  }

  const { data: atsData, errors, total_comprobantes, periodo } = data;

  // Validación adicional: Verificar propiedades específicas
  if (!atsData.idInformante || !atsData.razonSocial) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Alert severity="error">
          <Typography variant="body2">
            Error: Los datos del ATS están incompletos. Por favor, vuelva a procesar el archivo.
          </Typography>
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        📋 Vista Previa del ATS
      </Typography>

      {/* Información General */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Business sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Información del Contribuyente</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                <strong>RUC:</strong> {atsData.idInformante || 'No disponible'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Razón Social:</strong> {atsData.razonSocial || 'No disponible'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DateRange sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Período</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Año:</strong> {atsData.anio || 'No disponible'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Mes:</strong> {atsData.mes || 'No disponible'} ({periodo || 'No disponible'})
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Receipt sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Comprobantes</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Total:</strong> {total_comprobantes || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Proveedores únicos:</strong> {atsData.compras?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AttachMoney sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Totales</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                <strong>Total Compras:</strong> ${atsData.compras?.reduce((sum, compra) => sum + (compra.baseImponible || 0), 0).toFixed(2) || '0.00'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Total IVA:</strong> ${atsData.compras?.reduce((sum, compra) => sum + (compra.montoIva || 0), 0).toFixed(2) || '0.00'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Errores y advertencias mejorados */}
      {errors && errors.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Warning sx={{ mr: 1 }} />
            <Typography variant="body2" gutterBottom>
              <strong>⚠️ Archivos con problemas encontrados ({errors.length}):</strong>
            </Typography>
          </Box>
          <Box sx={{ mt: 2 }}>
            {errors.map((error, index) => (
              <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                  📄 {error}
                </Typography>
              </Box>
            ))}
          </Box>
          <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(25, 118, 210, 0.1)', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Info sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="body2" color="primary">
                <strong>💡 Recomendaciones:</strong>
              </Typography>
            </Box>
            <Typography variant="body2" color="primary">
              • Verifique que los archivos XML sean facturas autorizadas por el SRI
              <br />• Asegúrese de que los archivos no estén corruptos
              <br />• Los archivos deben tener la estructura completa de autorización
            </Typography>
          </Box>
        </Alert>
      )}

      {/* Tabla de Compras */}
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Detalle de Compras por Proveedor
      </Typography>
      
      {atsData.compras && atsData.compras.length > 0 ? (
        <TableContainer component={Paper} variant="outlined">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell><strong>Proveedor</strong></TableCell>
                <TableCell><strong>Establecimiento</strong></TableCell>
                <TableCell align="right"><strong>Base Imponible</strong></TableCell>
                <TableCell align="right"><strong>IVA</strong></TableCell>
                <TableCell align="center"><strong>Tipo</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {atsData.compras.map((compra, index) => (
                <TableRow key={index}>
                  <TableCell>{compra.idProv || 'No disponible'}</TableCell>
                  <TableCell>{compra.establecimiento || 'N/A'}-{compra.puntoEmision || 'N/A'}</TableCell>
                  <TableCell align="right">${(compra.baseImponible || 0).toFixed(2)}</TableCell>
                  <TableCell align="right">${(compra.montoIva || 0).toFixed(2)}</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={compra.tipoComprobante === '01' ? 'Factura' : 'Otro'}
                      size="small"
                      color={compra.tipoComprobante === '01' ? 'success' : 'default'}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Alert severity="info">
          <Typography variant="body2">
            No hay compras para mostrar.
          </Typography>
        </Alert>
      )}
    </Paper>
  );
};

export default ATSPreview;
