'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

export default function NewAnimalPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [formData, setFormData] = useState({
    tag_id: '',
    name: '',
    breed: '',
    birth_date: '',
    status: 'cow', // lactação
    last_calving_date: '',
  });
  const [error, setError] = useState('');

  if (isLoading) return <p className="p-6">Carregando...</p>;
  if (!user) {
    router.push('/login');
    return null;
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Prepara os dados para envio: converte strings vazias em null
    const payload = {
      ...formData,
      birth_date: formData.birth_date || null,
      last_calving_date: formData.last_calving_date || null,
    };

    try {
      await api.post('/animals/', payload);
      router.push('/animals');
    } catch (err: any) {
      // Tratamento detalhado de erros de validação
      const responseData = err.response?.data;
      if (responseData?.detail) {
        if (Array.isArray(responseData.detail)) {
          // Erros de validação do Pydantic (lista de objetos)
          const messages = responseData.detail.map((e: any) => {
            if (e.loc && e.msg) {
              return `${e.loc.join('.')}: ${e.msg}`;
            }
            return JSON.stringify(e);
          });
          setError(messages.join('; '));
        } else if (typeof responseData.detail === 'string') {
          setError(responseData.detail);
        } else {
          setError(JSON.stringify(responseData.detail));
        }
      } else {
        setError('Erro ao cadastrar animal');
      }
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Novo Animal</h1>
      <Link href="/animals" className="text-blue-600 hover:underline block mb-4">
        ← Voltar
      </Link>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <pre className="whitespace-pre-wrap font-sans text-sm">{error}</pre>
        </div>
      )}
      <form onSubmit={handleSubmit} className="max-w-lg bg-white p-6 rounded shadow">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Brinco *</label>
          <input
            type="text"
            name="tag_id"
            value={formData.tag_id}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Nome</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Raça</label>
          <input
            type="text"
            name="breed"
            value={formData.breed}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Data de nascimento</label>
          <input
            type="date"
            name="birth_date"
            value={formData.birth_date}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Status *</label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          >
            <option value="cow">Lactação</option>
            <option value="dry">Seca</option>
            <option value="heifer">Novilha</option>
            <option value="calf">Bezerra</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Data do último parto</label>
          <input
            type="date"
            name="last_calving_date"
            value={formData.last_calving_date}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Salvar
        </button>
      </form>
    </div>
  );
}