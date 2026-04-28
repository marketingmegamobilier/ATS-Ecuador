import axios from 'axios';
import { ProcessResponse, ATSData } from '../types';

const API_BASE_URL = 'http://backend-sri-ats-0wgkap-64803a-217-216-80-123.traefik.me';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadTxtFile = async (file: File, rucEmpresa: string, razonSocial: string): Promise<ProcessResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('ruc_empresa', rucEmpresa);
  formData.append('razon_social_empresa', razonSocial);
  
  const response = await api.post('/upload-txt', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const uploadXMLFiles = async (files: File[], rucEmpresa: string, razonSocial: string): Promise<ProcessResponse> => {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  formData.append('ruc_empresa', rucEmpresa);
  formData.append('razon_social_empresa', razonSocial);
  
  const response = await api.post('/upload-xml-facturas', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const uploadCompras = async (files: File[], periodoId: number): Promise<any> => {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/transacciones/periodo/${periodoId}/upload-compras`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const uploadVentas = async (files: File[], periodoId: number): Promise<any> => {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/transacciones/periodo/${periodoId}/upload-ventas`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const uploadRetenciones = async (files: File[], periodoId: number): Promise<any> => {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/transacciones/periodo/${periodoId}/upload-retenciones`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const generateXML = async (atsData: ATSData): Promise<Blob> => {
  const response = await api.post('/generate-xml', atsData, {
    responseType: 'blob',
  });
  
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getFeatures = async () => {
  const response = await api.get('/features');
  return response.data;
};

// ======================================
// DESCARGA DE ATS - Dual Download
// ======================================

/**
 * Descarga el archivo ATS en formato ZIP (listo para enviar al SRI).
 * El ZIP incluye el XML y un archivo README con instrucciones.
 */
export const downloadATSZip = async (periodoId: number): Promise<Blob> => {
  const response = await api.get(`/transacciones/periodo/${periodoId}/generar-ats`, {
    responseType: 'blob'
  });
  return response.data;
};

/**
 * Descarga SOLO el archivo XML del ATS (sin comprimir).
 * Útil para debugging, revisión y validación offline.
 */
export const downloadATSXml = async (periodoId: number): Promise<Blob> => {
  const response = await api.get(`/transacciones/periodo/${periodoId}/generar-ats-xml`, {
    responseType: 'blob'
  });
  return response.data;
};

/**
 * Helper function para descargar un blob como archivo.
 * @param blob - El blob a descargar
 * @param filename - Nombre del archivo
 */
export const downloadBlobAsFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const deletePeriodo = async (periodoId: number): Promise<void> => {
  await api.delete(`/periodos/${periodoId}`);
};

export const deletePeriodosBatch = async (ids: number[]): Promise<any> => {
  return (await api.delete('/periodos/batch/delete', { data: { ids } })).data;
};

export default api;
