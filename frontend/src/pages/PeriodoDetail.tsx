import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container, Typography, Button, Paper, Box, Tabs, Tab,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Stepper, Step, StepLabel, Tooltip, IconButton, Chip, Divider,
    CircularProgress, Alert, Snackbar, Stack
} from '@mui/material';
import axios from 'axios';
import FileUploader from '../components/FileUploader';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DownloadIcon from '@mui/icons-material/Download';
import FolderZipIcon from '@mui/icons-material/FolderZip';
import DescriptionIcon from '@mui/icons-material/Description';
import DeleteIcon from '@mui/icons-material/Delete';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { downloadATSZip, downloadATSXml, downloadBlobAsFile } from '../services/api';

interface Periodo {
    id: number;
    ruc_empresa: string;
    anio: number;
    mes: number;
    estado: string;
}

interface Compra {
    id: number;
    ruc_emisor: string;
    razon_social: string;
    fecha_emision: string;
    tipo_comprobante: string;
    base_imponible: number;
    monto_iva: number;
    total: number;
}

const PeriodoDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [periodo, setPeriodo] = useState<Periodo | null>(null);
    const [tabValue, setTabValue] = useState(0);
    const [compras, setCompras] = useState<Compra[]>([]);
    const [ventas, setVentas] = useState<any[]>([]);
    const [retenciones, setRetenciones] = useState<any[]>([]);
    const [downloadingZip, setDownloadingZip] = useState(false);
    const [downloadingXml, setDownloadingXml] = useState(false);
    const [snackbar, setSnackbar] = useState<{ open: boolean, message: string, severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });

    useEffect(() => {
        fetchPeriodo();
        fetchCompras();
        fetchVentas();
        fetchRetenciones();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);

    const fetchPeriodo = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/periodos/${id}`);
            setPeriodo(response.data);
        } catch (error) {
            console.error('Error fetching periodo:', error);
        }
    };

    const fetchCompras = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/transacciones/periodo/${id}/compras`);
            setCompras(response.data);
        } catch (error) {
            console.error('Error fetching compras:', error);
        }
    };

    const fetchVentas = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/transacciones/periodo/${id}/ventas`);
            setVentas(response.data);
        } catch (error) {
            console.error('Error fetching ventas:', error);
        }
    };

    const fetchRetenciones = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/transacciones/periodo/${id}/retenciones`);
            setRetenciones(response.data);
        } catch (error) {
            console.error('Error fetching retenciones:', error);
        }
    };

    const handleUploadSuccess = () => {
        fetchCompras();
        fetchVentas();
        fetchRetenciones();
        fetchPeriodo(); // Update counts
    };

    const handleDeleteCompra = async (id: number) => {
        if (!window.confirm('¿Estás seguro de eliminar esta factura?')) return;
        try {
            await axios.delete(`http://localhost:8000/transacciones/compras/${id}`);
            fetchCompras();
        } catch (error) {
            console.error('Error deleting compra:', error);
            alert('Error al eliminar la factura');
        }
    };

    const handleDeleteRetencion = async (id: number) => {
        if (!window.confirm('¿Estás seguro de eliminar esta retención?')) return;
        try {
            await axios.delete(`http://localhost:8000/transacciones/retenciones/${id}`);
            fetchRetenciones();
        } catch (error) {
            console.error('Error deleting retencion:', error);
            alert('Error al eliminar la retención');
        }
    };

    const handleDeleteVenta = async (id: number) => {
        if (!window.confirm('¿Estás seguro de eliminar esta factura de venta?')) return;
        try {
            await axios.delete(`http://localhost:8000/transacciones/ventas/${id}`);
            fetchVentas();
        } catch (error) {
            console.error('Error deleting venta:', error);
            alert('Error al eliminar la venta');
        }
    };

    const handleDownloadZip = async () => {
        if (!id) return;

        setDownloadingZip(true);
        try {
            const blob = await downloadATSZip(parseInt(id));
            const filename = `ATS_${periodo?.mes.toString().padStart(2, '0')}_${periodo?.anio}_${periodo?.ruc_empresa}.zip`;
            downloadBlobAsFile(blob, filename);

            setSnackbar({
                open: true,
                message: '✅ Archivo ZIP descargado correctamente. ¡Listo para enviar al SRI!',
                severity: 'success'
            });
        } catch (error) {
            console.error('Error downloading ZIP:', error);
            setSnackbar({
                open: true,
                message: '❌ Error al descargar el ZIP. Por favor, intenta de nuevo.',
                severity: 'error'
            });
        } finally {
            setDownloadingZip(false);
        }
    };

    const handleDownloadXml = async () => {
        if (!id) return;

        setDownloadingXml(true);
        try {
            const blob = await downloadATSXml(parseInt(id));
            const filename = `ATS_${periodo?.mes.toString().padStart(2, '0')}_${periodo?.anio}_${periodo?.ruc_empresa}.xml`;
            downloadBlobAsFile(blob, filename);

            setSnackbar({
                open: true,
                message: '✅ Archivo XML descargado correctamente. Úsalo para revisar o validar.',
                severity: 'success'
            });
        } catch (error) {
            console.error('Error downloading XML:', error);
            setSnackbar({
                open: true,
                message: '❌ Error al descargar el XML. Por favor, intenta de nuevo.',
                severity: 'error'
            });
        } finally {
            setDownloadingXml(false);
        }
    };

    if (!periodo) return <Typography>Cargando...</Typography>;

    const steps = ['Cargar Comprobantes', 'Revisar Información', 'Generar ATS'];

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Header y Navegación */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Button
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate('/')}
                    sx={{ textTransform: 'none' }}
                >
                    Volver al Dashboard
                </Button>
                <Stack direction="row" spacing={1}>
                    <Tooltip title="Validar el archivo ATS generado antes de enviarlo">
                        <Button
                            variant="outlined"
                            color="secondary"
                            onClick={() => navigate(`/periodo/${id}/validar`)}
                            startIcon={<CheckCircleIcon />}
                        >
                            Validar ATS
                        </Button>
                    </Tooltip>
                    <Tooltip title="Descargar ZIP para enviar al SRI (incluye README)">
                        <Button
                            variant="contained"
                            color="success"
                            onClick={handleDownloadZip}
                            disabled={downloadingZip}
                            startIcon={downloadingZip ? <CircularProgress size={20} color="inherit" /> : <FolderZipIcon />}
                        >
                            {downloadingZip ? 'Generando...' : 'Descargar ZIP (SRI)'}
                        </Button>
                    </Tooltip>
                    <Tooltip title="Descargar solo XML para revisar o validar offline">
                        <Button
                            variant="outlined"
                            color="primary"
                            onClick={handleDownloadXml}
                            disabled={downloadingXml}
                            startIcon={downloadingXml ? <CircularProgress size={20} color="inherit" /> : <DescriptionIcon />}
                        >
                            {downloadingXml ? 'Generando...' : 'Descargar XML'}
                        </Button>
                    </Tooltip>
                </Stack>
            </Box>

            {/* Información del Periodo */}
            <Paper sx={{ p: 3, mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                    <Typography variant="h5" gutterBottom>
                        Periodo Fiscal: {periodo.mes.toString().padStart(2, '0')}/{periodo.anio}
                    </Typography>
                    <Typography variant="subtitle1" color="textSecondary">
                        Empresa RUC: {periodo.ruc_empresa}
                    </Typography>
                </Box>
                <Chip
                    label={periodo.estado || 'Activo'}
                    color={periodo.estado === 'Cerrado' ? 'default' : 'primary'}
                    variant="outlined"
                />
            </Paper>

            {/* Stepper de Progreso */}
            <Box sx={{ width: '100%', mb: 4 }}>
                <Stepper activeStep={1} alternativeLabel>
                    {steps.map((label) => (
                        <Step key={label}>
                            <StepLabel>{label}</StepLabel>
                        </Step>
                    ))}
                </Stepper>
            </Box>

            {/* Contenido Principal (Tabs) */}
            <Paper sx={{ width: '100%', mb: 2 }}>
                <Tabs
                    value={tabValue}
                    onChange={(_, v) => setTabValue(v)}
                    indicatorColor="primary"
                    textColor="primary"
                    centered
                >
                    <Tab icon={<AssignmentIcon />} label={`Compras (${compras.length})`} />
                    <Tab icon={<AssignmentIcon />} label={`Ventas (${ventas.length})`} />
                    <Tab icon={<AssignmentIcon />} label={`Retenciones (${retenciones.length})`} />
                </Tabs>
                <Divider />

                <Box p={3}>
                    {tabValue === 0 && (
                        <Box>
                            <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
                                <FileUploader
                                    onUploadSuccess={handleUploadSuccess}
                                    periodoId={parseInt(id!)}
                                    docType="compra"
                                />
                            </Box>
                            <TableContainer>
                                <Table size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Fecha</TableCell>
                                            <TableCell>RUC</TableCell>
                                            <TableCell>Razón Social</TableCell>
                                            <TableCell>Tipo</TableCell>
                                            <TableCell align="right">Base Imp.</TableCell>
                                            <TableCell align="right">IVA</TableCell>
                                            <TableCell align="right">Total</TableCell>
                                            <TableCell align="center">Acciones</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {compras.map((compra) => (
                                            <TableRow key={compra.id} hover>
                                                <TableCell>{compra.fecha_emision}</TableCell>
                                                <TableCell>{compra.ruc_emisor}</TableCell>
                                                <TableCell>{compra.razon_social}</TableCell>
                                                <TableCell>{compra.tipo_comprobante}</TableCell>
                                                <TableCell align="right">${compra.base_imponible.toFixed(2)}</TableCell>
                                                <TableCell align="right">${compra.monto_iva.toFixed(2)}</TableCell>
                                                <TableCell align="right">${compra.total.toFixed(2)}</TableCell>
                                                <TableCell align="center">
                                                    <Tooltip title="Eliminar factura">
                                                        <IconButton size="small" color="error" onClick={() => handleDeleteCompra(compra.id)}>
                                                            <DeleteIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                        {compras.length === 0 && (
                                            <TableRow>
                                                <TableCell colSpan={8} align="center">
                                                    <Typography color="textSecondary" sx={{ py: 3 }}>
                                                        No hay compras registradas. Sube tus XMLs para comenzar.
                                                    </Typography>
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Box>
                    )}

                    {tabValue === 1 && (
                        <Box>
                            <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
                                <FileUploader
                                    onUploadSuccess={handleUploadSuccess}
                                    periodoId={parseInt(id!)}
                                    docType="venta"
                                />
                            </Box>
                            <TableContainer>
                                <Table size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Cliente ID</TableCell>
                                            <TableCell>Tipo Comp.</TableCell>
                                            <TableCell>Num. Comp.</TableCell>
                                            <TableCell align="right">Base Imp.</TableCell>
                                            <TableCell align="right">IVA</TableCell>
                                            <TableCell align="center">Acciones</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {ventas.map((venta) => (
                                            <TableRow key={venta.id} hover>
                                                <TableCell>{venta.cliente}</TableCell>
                                                <TableCell>{venta.tipo_comprobante}</TableCell>
                                                <TableCell>{venta.numero_comprobantes}</TableCell>
                                                <TableCell align="right">${venta.base_imponible.toFixed(2)}</TableCell>
                                                <TableCell align="right">${venta.monto_iva.toFixed(2)}</TableCell>
                                                <TableCell align="center">
                                                    <Tooltip title="Eliminar venta">
                                                        <IconButton size="small" color="error" onClick={() => handleDeleteVenta(venta.id)}>
                                                            <DeleteIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                        {ventas.length === 0 && (
                                            <TableRow>
                                                <TableCell colSpan={6} align="center">
                                                    <Typography color="textSecondary" sx={{ py: 3 }}>
                                                        No hay ventas registradas.
                                                    </Typography>
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Box>
                    )}

                    {tabValue === 2 && (
                        <Box>
                            <Box mb={3}>
                                <FileUploader
                                    onUploadSuccess={handleUploadSuccess}
                                    periodoId={parseInt(id!)}
                                    docType="retencion"
                                />
                            </Box>
                            <TableContainer>
                                <Table size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Fecha</TableCell>
                                            <TableCell>Establecimiento</TableCell>
                                            <TableCell>Pto. Emisión</TableCell>
                                            <TableCell>Secuencial</TableCell>
                                            <TableCell>Autorización</TableCell>
                                            <TableCell align="center">Acciones</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {retenciones.map((ret) => (
                                            <TableRow key={ret.id} hover>
                                                <TableCell>{ret.fechaEmision}</TableCell>
                                                <TableCell>{ret.establecimiento}</TableCell>
                                                <TableCell>{ret.puntoEmision}</TableCell>
                                                <TableCell>{ret.secuencial}</TableCell>
                                                <TableCell>{ret.autorizacion}</TableCell>
                                                <TableCell align="center">
                                                    <Tooltip title="Eliminar retención">
                                                        <IconButton size="small" color="error" onClick={() => handleDeleteRetencion(ret.id)}>
                                                            <DeleteIcon />
                                                        </IconButton>
                                                    </Tooltip>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                        {retenciones.length === 0 && (
                                            <TableRow>
                                                <TableCell colSpan={6} align="center">
                                                    <Typography color="textSecondary" sx={{ py: 3 }}>
                                                        No hay retenciones registradas.
                                                    </Typography>
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </Box>
                    )}
                </Box>
            </Paper>
        </Container>
    );
};

export default PeriodoDetail;
