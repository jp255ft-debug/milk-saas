'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import api, { extractErrorMessage } from '@/lib/api';

interface Animal {
  id: string;
  name: string;
  tag_id: string;
}

export default function EditMilkPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [formData, setFormData] = useState({
    animal_id: '',
    production_date: '',
    liters_produced: '',
    period: '',
    fat_content: '',
    protein_content: '',
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
      const [animalsRes, milkRes] = await Promise.all([
        api.get('/animals/'),
        api.get(`/milk/${params.id}`)
      ]);
      setAnimals(animalsRes.data);
      const milk = milkRes.data;
      setFormData({
        animal_id: milk.animal_id,
        production_date: milk.production_date,
        liters_produced: milk.liters_produced.toString(),
        period: milk.period || '',
        fat_content: milk.fat_content?.toString() || '',
        protein_content: milk.protein_content?.toString() || '',
      });
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.put(`/milk/${params.id}`, {
        animal_id: formData.animal_id,
        production_date: formData.production_date,
        liters_produced: parseFloat(formData.liters_produced),
        period: formData.period || undefined,
        fat_content: formData.fat_content ? parseFloat(formData.fat_content) : undefined,
        protein_content: formData.protein_content ? parseFloat(formData.protein_content) : undefined,
      });
      router.push('/milk');
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  if (isLoading || loading) return <p className="p-6">Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Editar Produção de Leite</h1>
      <Link href="/milk" className="text-blue-600 hover:underline block mb-4">
        ← Voltar
      </Link>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="max-w-lg bg-white p-6 rounded shadow">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Animal *</label>
          <select
            name="animal_id"
            value={formData.animal_id}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Selecione</option>
            {animals.map(a => (
              <option key={a.id} value={a.id}>{a.name || a.tag_id}</option>
            ))}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Data *</label>
          <input
            type="date"
            name="production_date"
            value={formData.production_date}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Litros *</label>
          <input
            type="number"
            step="0.01"
            name="liters_produced"
            value={formData.liters_produced}
            onChange={handleChange}
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Período</label>
          <select
            name="period"
            value={formData.period}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Selecione</option>
            <option value="morning">Manhã</option>
            <option value="afternoon">Tarde</option>
            <option value="night">Noite</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Gordura (%)</label>
          <input
            type="number"
            step="0.01"
            name="fat_content"
            value={formData.fat_content}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Proteína (%)</label>
          <input
            type="number"
            step="0.01"
            name="protein_content"
            value={formData.protein_content}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          />
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