'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

interface Category {
  id: string;
  name: string;
  type: string;
}

export default function EditTransactionPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const [categories, setCategories] = useState<Category[]>([]);
  const [formData, setFormData] = useState({
    category_id: '',
    description: '',
    amount: '',
    transaction_date: '',
    is_paid: true,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user && params.id) {
      fetchData();
    }
  }, [user, params.id]);

  const fetchData = async () => {
    try {
      const [catsRes, transRes] = await Promise.all([
        api.get('/finance/categories'),
        api.get(`/finance/transactions/${params.id}`)
      ]);
      setCategories(catsRes.data);
      const t = transRes.data;
      setFormData({
        category_id: t.category_id,
        description: t.description || '',
        amount: t.amount.toString(),
        transaction_date: t.transaction_date,
        is_paid: t.is_paid,
      });
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      router.push('/finance');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const value = e.target.type === 'checkbox' ? (e.target as HTMLInputElement).checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.put(`/finance/transactions/${params.id}`, {
        category_id: formData.category_id,
        description: formData.description || undefined,
        amount: parseFloat(formData.amount),
        transaction_date: formData.transaction_date,
        is_paid: formData.is_paid,
      });
      router.push('/finance');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao atualizar transação');
    }
  };

  if (isLoading || loading) return <p className="p-6">Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Editar Transação</h1>
      <Link href="/finance" className="text-blue-600 hover:underline block mb-4">
        ← Voltar
      </Link>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="max-w-lg bg-white p-6 rounded shadow">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Categoria *</label>
          <select
            name="category_id"
            value={formData.category_id}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Selecione</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Descrição</label>
          <input
            type="text"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Valor * (R$)</label>
          <input
            type="number"
            step="0.01"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Data *</label>
          <input
            type="date"
            name="transaction_date"
            value={formData.transaction_date}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              name="is_paid"
              checked={formData.is_paid}
              onChange={handleChange}
              className="mr-2"
            />
            <span className="text-sm font-medium">Pago</span>
          </label>
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Atualizar
        </button>
      </form>
    </div>
  );
}