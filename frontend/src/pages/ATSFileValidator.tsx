import React, { useState } from 'react';
import {
    Container, Typography, Button, Paper, Box, Card, CardContent,
    List, ListItem, ListItemText, Chip, Divider, Alert, CircularProgress,
    Grid, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface ValidationError {
    tipo: string;
    modulo: string;
    mensaje: string;
    referencia?: any;
    linea?: number;
}

interface ValidationCheck {
    regla: string;
    estado: "PASÓ" | "FALLÓ";
    detalle: string;
    fuente?: string;
}

interface ValidationStats {
    total_compras?: number;
    total_ventas?: number;
    total_retenciones?: number;
    total_anulados?: number;
}

interface ValidationResult {
    valid: boolean;
    filename: string;
    errors: ValidationError[];
    warnings: ValidationError[];
    stats: ValidationStats;
    checklist: ValidationCheck[];
}

const ATSFileValidator: React.FC = () => {
    const navigate = useNavigate();
    const [result, setResult] = useState<ValidationResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const onDrop = async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        const file = acceptedFiles[0];
        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('validation/validate-file', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setError('Error al conectar con el servicio de validación.');
        } finally {
            setLoading(false);
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/xml': ['.xml'],
            'application/zip': ['.zip']
        },
        maxFiles: 1
    });

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Button
                startIcon={<ArrowBackIcon />}
                onClick={() => navigate('/')}
                sx={{ mb: 2 }}
            >
                Volver al Dashboard
            </Button>

            <Typography variant="h4" gutterBottom>
                Validador Avanzado de ATS
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
                Sube tu archivo XML o ZIP para verificar el cumplimiento de la Ficha Técnica del SRI.
                El sistema validará estructura XSD, cálculos matemáticos y consistencia de datos.
            </Typography>

            <Paper
                {...getRootProps()}
                sx={{
                    p: 5,
                    textAlign: 'center',
                    cursor: 'pointer',
                    border: '2px dashed #ccc',
                    backgroundColor: isDragActive ? '#f0f8ff' : '#fafafa',
                    mb: 4
                }}
            >
                <input {...getInputProps()} />
                {loading ? (
                    <CircularProgress />
                ) : (
                    <Typography>
                        {isDragActive
                            ? "Suelta el archivo aquí..."
                            : "Arrastra y suelta tu archivo ATS (XML o ZIP) aquí, o haz clic para seleccionar"}
                    </Typography>
                )}
            </Paper>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {result && (
                <Box>
                    {/* Resumen General */}
                    <Card sx={{ mb: 3, borderLeft: result.valid ? '6px solid green' : '6px solid red' }}>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                {result.valid ? "✅ Archivo Válido" : "❌ Se encontraron errores"}
                            </Typography>
                            <Typography color="textSecondary">
                                Archivo: {result.filename}
                            </Typography>
                        </CardContent>
                    </Card>

                    {/* Estadísticas */}
                    <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        Resumen de Registros
                    </Typography>
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                        <Grid item xs={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h4" color="primary">{result.stats.total_compras || 0}</Typography>
                                <Typography variant="body2">Compras</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h4" color="secondary">{result.stats.total_ventas || 0}</Typography>
                                <Typography variant="body2">Ventas</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h4">{result.stats.total_retenciones || 0}</Typography>
                                <Typography variant="body2">Retenciones</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6} md={3}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                                <Typography variant="h4" color="error">{result.stats.total_anulados || 0}</Typography>
                                <Typography variant="body2">Anulados</Typography>
                            </Paper>
                        </Grid>
                    </Grid>

                    {/* Checklist de Reglas */}
                    <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                        Criterios Evaluados
                    </Typography>
                    <Box sx={{ mb: 3 }}>
                        {result.checklist.map((check, index) => (
                            <Accordion key={index} defaultExpanded={check.estado === 'FALLÓ'}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Box display="flex" alignItems="center" width="100%">
                                        {check.estado === 'PASÓ' ? (
                                            <CheckCircleIcon color="success" sx={{ mr: 2 }} />
                                        ) : (
                                            <ErrorIcon color="error" sx={{ mr: 2 }} />
                                        )}
                                        <Typography sx={{ flexShrink: 0, fontWeight: 'bold' }}>
                                            {check.regla}
                                        </Typography>
                                        <Typography sx={{ color: 'text.secondary', ml: 2 }}>
                                            {check.estado}
                                        </Typography>
                                    </Box>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <Typography>
                                        {check.detalle}
                                    </Typography>
                                    {check.fuente && (
                                        <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary', fontStyle: 'italic' }}>
                                            Fuente: {check.fuente}
                                        </Typography>
                                    )}
                                </AccordionDetails>
                            </Accordion>
                        ))}
                    </Box>

                    {/* Lista Detallada de Errores */}
                    {result.errors.length > 0 && (
                        <Paper sx={{ mb: 3, p: 2, bgcolor: '#fff4f4' }}>
                            <Typography variant="h6" color="error" gutterBottom>
                                Detalle de Errores ({result.errors.length})
                            </Typography>
                            <Divider />
                            <List>
                                {result.errors.map((err, index) => (
                                    <ListItem key={index} divider>
                                        <ListItemText
                                            primary={
                                                <Box display="flex" alignItems="center" gap={1}>
                                                    <Chip
                                                        label={err.tipo.toUpperCase()}
                                                        color={err.tipo === 'estructura' ? 'warning' : 'error'}
                                                        size="small"
                                                    />
                                                    <Typography variant="subtitle1" fontWeight="bold">
                                                        {err.mensaje}
                                                    </Typography>
                                                </Box>
                                            }
                                            secondary={
                                                <>
                                                    <Typography component="span" variant="body2" color="textPrimary">
                                                        Módulo: {err.modulo}
                                                    </Typography>
                                                    {err.referencia && (
                                                        <Box component="pre" sx={{ bgcolor: '#ffffff', p: 1, mt: 1, borderRadius: 1, fontSize: '0.8rem', border: '1px solid #eee' }}>
                                                            {JSON.stringify(err.referencia, null, 2)}
                                                        </Box>
                                                    )}
                                                </>
                                            }
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        </Paper>
                    )}

                    {result.warnings.length > 0 && (
                        <Paper sx={{ mb: 3, p: 2, bgcolor: '#fffbf0' }}>
                            <Typography variant="h6" color="warning.main" gutterBottom>
                                Advertencias ({result.warnings.length})
                            </Typography>
                            <Divider />
                            <List>
                                {result.warnings.map((warn, index) => (
                                    <ListItem key={index} divider>
                                        <ListItemText
                                            primary={warn.mensaje}
                                            secondary={`Módulo: ${warn.modulo}`}
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        </Paper>
                    )}
                </Box>
            )}
        </Container>
    );
};

export default ATSFileValidator;
