import React, { useState } from 'react';
import {
  Paper,
  Typography,
  TextField,
  Box,
  Grid,
  Alert,
  Chip,
} from '@mui/material';
import {
  Business,
  CheckCircle,
} from '@mui/icons-material';

interface EmpresaFormProps {
  onEmpresaChange: (ruc: string, razonSocial: string) => void;
  disabled?: boolean;
}

const EmpresaForm: React.FC<EmpresaFormProps> = ({ onEmpresaChange, disabled = false }) => {
  const [ruc, setRuc] = useState('');
  const [razonSocial, setRazonSocial] = useState('');
  const [rucError, setRucError] = useState('');
  const [razonSocialError, setRazonSocialError] = useState('');

  const validateRuc = (value: string) => {
    const cleanRuc = value.replace(/\D/g, '');
    if (cleanRuc.length !== 13) {
      setRucError('El RUC debe tener exactamente 13 dígitos');
      return false;
    }
    setRucError('');
    return true;
  };

  const validateRazonSocial = (value: string) => {
    const cleanValue = value.trim();
    if (cleanValue.length === 0) {
      setRazonSocialError('La razón social es obligatoria');
      return false;
    }
    if (cleanValue.length > 300) {
      setRazonSocialError('La razón social no puede exceder 300 caracteres');
      return false;
    }
    setRazonSocialError('');
    return true;
  };

  const handleRucChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value.replace(/\D/g, '').slice(0, 13);
    setRuc(value);
    
    if (validateRuc(value) && razonSocial.trim()) {
      onEmpresaChange(value, razonSocial.trim().toUpperCase());
    }
  };

  const handleRazonSocialChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setRazonSocial(value);
    
    if (validateRazonSocial(value) && ruc.length === 13) {
      onEmpresaChange(ruc, value.trim().toUpperCase());
    }
  };

  const isFormValid = ruc.length === 13 && razonSocial.trim().length > 0 && !rucError && !razonSocialError;

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Business sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">
          Información de la Empresa
        </Typography>
        {isFormValid && (
          <Chip
            icon={<CheckCircle />}
            label="Válido"
            color="success"
            size="small"
            sx={{ ml: 2 }}
          />
        )}
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Importante:</strong> Ingrese el RUC y razón social de la empresa 
          que está generando el ATS (la empresa compradora), no del proveedor.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="RUC de la Empresa"
            value={ruc}
            onChange={handleRucChange}
            error={!!rucError}
            helperText={rucError || 'Ingrese 13 dígitos numéricos'}
            placeholder="1793212860001"
            disabled={disabled}
            inputProps={{
              maxLength: 13,
              pattern: '[0-9]*',
            }}
          />
        </Grid>

        <Grid item xs={12} md={8}>
          <TextField
            fullWidth
            label="Razón Social de la Empresa"
            value={razonSocial}
            onChange={handleRazonSocialChange}
            error={!!razonSocialError}
            helperText={razonSocialError || 'Nombre completo de la empresa'}
            placeholder="PIDA"
            disabled={disabled}
            inputProps={{
              maxLength: 300,
            }}
          />
        </Grid>
      </Grid>

      {isFormValid && (
        <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
          <Typography variant="body2" color="success.contrastText">
            <strong>✓ Empresa configurada:</strong> {razonSocial.toUpperCase()} - RUC: {ruc}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default EmpresaForm;
