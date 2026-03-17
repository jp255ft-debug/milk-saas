import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  withCredentials: true,
});

export function extractErrorMessage(err: any): string {
  const data = err.response?.data;
  if (data?.detail) {
    if (Array.isArray(data.detail)) {
      return data.detail.map((e: any) => {
        if (e.loc && e.msg) return `${e.loc.join('.')}: ${e.msg}`;
        return JSON.stringify(e);
      }).join('; ');
    }
    if (typeof data.detail === 'string') return data.detail;
    return JSON.stringify(data.detail);
  }
  if (data?.message) return data.message;
  return err.message || 'Erro desconhecido';
}

export default api;
