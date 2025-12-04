import React, { useState, useEffect } from 'react';
import {
    Container, Typography, Button, Table, TableBody, TableCell,
    TableContainer, TableHead, TableRow, Paper, Box, Checkbox,
    Tooltip, IconButton, Dialog, DialogTitle, DialogContent,
    TextField, DialogActions, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import VisibilityIcon from '@mui/icons-material/Visibility';

interface Periodo {
    id: number;
    anio: number;
    mes: number;
    estado: string;
    ruc_empresa?: string;
    total_compras?: number;
    total_ventas?: number;
}

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [periodos, setPeriodos] = useState<Periodo[]>([]);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [open, setOpen] = useState(false);
    const [newPeriodo, setNewPeriodo] = useState({
        ruc_empresa: '',
        razon_social: '',  // Razón social de la empresa
        anio: new Date().getFullYear(),
        mes: new Date().getMonth() + 1
    });

    useEffect(() => {
        fetchPeriodos();
    }, []);

    const fetchPeriodos = async () => {
        try {
            const response = await axios.get('http://localhost:8000/periodos/');
            setPeriodos(response.data);
        } catch (error) {
            console.error('Error fetching periodos:', error);
        }
    };

    const handleCreate = async () => {
        try {
            await axios.post('http://localhost:8000/periodos/', newPeriodo);
            setOpen(false);
            fetchPeriodos();
        } catch (error) {
            console.error('Error creating periodo:', error);
            alert('Error creando periodo');
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm('¿Estás seguro de eliminar este periodo y toda su información?')) return;
        try {
            await axios.delete(`http://localhost:8000/periodos/${id}`);
            fetchPeriodos();
        } catch (error) {
            console.error('Error deleting periodo:', error);
            alert('Error eliminando periodo');
        }
    };

    const handleBulkDelete = async () => {
        if (!window.confirm(`¿Estás seguro de eliminar ${selectedIds.length} periodos seleccionados?`)) return;
        try {
            await axios.delete('http://localhost:8000/periodos/batch/delete', {
                data: { ids: selectedIds }
            });
            setSelectedIds([]);
            fetchPeriodos();
        } catch (error) {
            console.error('Error bulk deleting periodos:', error);
            alert('Error eliminando periodos');
        }
    };

    const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            setSelectedIds(periodos.map((p) => p.id));
        } else {
            setSelectedIds([]);
        }
    };

    const handleSelect = (id: number) => {
        const selectedIndex = selectedIds.indexOf(id);
        let newSelected: number[] = [];

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selectedIds, id);
        } else if (selectedIndex === 0) {
            newSelected = newSelected.concat(selectedIds.slice(1));
        } else if (selectedIndex === selectedIds.length - 1) {
            newSelected = newSelected.concat(selectedIds.slice(0, -1));
        } else if (selectedIndex > 0) {
            newSelected = newSelected.concat(
                selectedIds.slice(0, selectedIndex),
                selectedIds.slice(selectedIndex + 1),
            );
        }
        setSelectedIds(newSelected);
    };

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box display="flex" alignItems="center">
                    <Typography variant="h4" component="h1" sx={{ mr: 2 }}>
                        Gestión de ATS
                    </Typography>
                    <Tooltip title="Flujo de trabajo: 1. Crea un periodo. 2. Sube tus XMLs. 3. Revisa y edita. 4. Genera el ATS.">
                        <IconButton color="primary">
                            <HelpOutlineIcon />
                        </IconButton>
                    </Tooltip>
                </Box>
                <Box>
                    <Button
                        variant="outlined"
                        color="secondary"
                        onClick={() => navigate('/validar-archivo')}
                        sx={{ mr: 2 }}
                        startIcon={<CheckCircleIcon />}
                    >
                        Validar XML/ZIP
                    </Button>
                    {selectedIds.length > 0 && (
                        <Button
                            variant="contained"
                            color="error"
                            onClick={handleBulkDelete}
                            sx={{ mr: 2 }}
                            startIcon={<DeleteIcon />}
                        >
                            Eliminar ({selectedIds.length})
                        </Button>
                    )}
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => setOpen(true)}
                        startIcon={<AddIcon />}
                    >
                        Nuevo Periodo
                    </Button>
                </Box>
            </Box>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell padding="checkbox">
                                <Checkbox
                                    indeterminate={selectedIds.length > 0 && selectedIds.length < periodos.length}
                                    checked={periodos.length > 0 && selectedIds.length === periodos.length}
                                    onChange={handleSelectAll}
                                />
                            </TableCell>
                            <TableCell>Periodo</TableCell>
                            <TableCell>RUC</TableCell>
                            <TableCell>Estado</TableCell>
                            <TableCell>Compras</TableCell>
                            <TableCell>Ventas</TableCell>
                            <TableCell>Acciones</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {periodos.map((periodo) => {
                            const isSelected = selectedIds.indexOf(periodo.id) !== -1;
                            return (
                                <TableRow
                                    key={periodo.id}
                                    hover
                                    selected={isSelected}
                                >
                                    <TableCell padding="checkbox">
                                        <Checkbox
                                            checked={isSelected}
                                            onChange={() => handleSelect(periodo.id)}
                                        />
                                    </TableCell>
                                    <TableCell>{`${periodo.mes.toString().padStart(2, '0')}/${periodo.anio}`}</TableCell>
                                    <TableCell>{periodo.ruc_empresa || 'N/A'}</TableCell>
                                    <TableCell>{periodo.estado}</TableCell>
                                    <TableCell>{periodo.total_compras || 0}</TableCell>
                                    <TableCell>{periodo.total_ventas || 0}</TableCell>
                                    <TableCell>
                                        <Tooltip title="Ver detalles y editar">
                                            <Button
                                                variant="outlined"
                                                size="small"
                                                onClick={() => navigate(`/periodo/${periodo.id}`)}
                                                sx={{ mr: 1 }}
                                                startIcon={<VisibilityIcon />}
                                            >
                                                Gestionar
                                            </Button>
                                        </Tooltip>
                                        <Tooltip title="Eliminar periodo y sus datos">
                                            <IconButton
                                                color="error"
                                                size="small"
                                                onClick={() => handleDelete(periodo.id)}
                                            >
                                                <DeleteIcon />
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </TableContainer>

            <Dialog open={open} onClose={() => setOpen(false)}>
                <DialogTitle>Nuevo Periodo Fiscal</DialogTitle>
                <DialogContent>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="RUC Empresa"
                        fullWidth
                        value={newPeriodo.ruc_empresa}
                        onChange={(e) => setNewPeriodo({ ...newPeriodo, ruc_empresa: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Razón Social"
                        fullWidth
                        value={newPeriodo.razon_social}
                        onChange={(e) => setNewPeriodo({ ...newPeriodo, razon_social: e.target.value })}
                    />
                    <TextField
                        margin="dense"
                        label="Año"
                        type="number"
                        fullWidth
                        value={newPeriodo.anio}
                        onChange={(e) => setNewPeriodo({ ...newPeriodo, anio: parseInt(e.target.value) })}
                    />
                    <FormControl fullWidth margin="dense">
                        <InputLabel>Mes</InputLabel>
                        <Select
                            value={newPeriodo.mes}
                            label="Mes"
                            onChange={(e) => setNewPeriodo({ ...newPeriodo, mes: e.target.value as number })}
                        >
                            {[...Array(12)].map((_, i) => (
                                <MenuItem key={i + 1} value={i + 1}>
                                    {new Date(0, i).toLocaleString('es-ES', { month: 'long' })}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancelar</Button>
                    <Button onClick={handleCreate} variant="contained">Crear</Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default Dashboard;
