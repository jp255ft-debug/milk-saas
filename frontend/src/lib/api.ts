import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
});

// Interceptor para adicionar token JWT no cabeçalho Authorization
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const extractErrorMessage = (error: any): string => {
  const data = error.response?.data;
  if (data?.detail) {
    if (Array.isArray(data.detail)) {
      const messages = data.detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
      return messages;
    }
    return String(data.detail);
  }
  if (data?.message) return String(data.message);
  return error.message || 'Erro desconhecido';
};

export default api;