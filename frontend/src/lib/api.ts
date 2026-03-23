
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  withCredentials: true,
});

export const extractErrorMessage = (error: any): string => {
  const data = error.response?.data;
  if (data?.detail) {
    if (Array.isArray(data.detail)) {
      // FastAPI validation error: detail is an array of { loc, msg, type, input }
      const messages = data.detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ');
      return messages;
    }
    return String(data.detail);
  }
  if (data?.message) return String(data.message);
  return error.message || 'Erro desconhecido';
};

export default api;
