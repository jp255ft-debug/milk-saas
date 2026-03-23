'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api, { extractErrorMessage } from '@/lib/api';

interface Animal {
  id: string;
  name: string;
  tag_id: string;
}

export default function NewMilkPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    animal_id: '',
    production_date: new Date().toISOString().slice(0, 10),
    liters_produced: '',
    period: 'morning',
    fat_content: '',
    protein_content: '',
  });

  useEffect(() => {
    if (!isLoading && !user) router.push('/login');
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      api.get('/animals/')
        .then(res => setAnimals(res.data))
        .catch(err => setError(extractErrorMessage(err)))
        .finally(() => setLoading(false));
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    // Converte os campos numéricos (liters_produced, fat_content, protein_content)
    const payload = {
      animal_id: formData.animal_id,
      production_date: formData.production_date,
      liters_produced: parseFloat(formData.liters_produced) || 0,
      period: formData.period || undefined,
      fat_content: formData.fat_content ? parseFloat(formData.fat_content) : undefined,
      protein_content: formData.protein_content ? parseFloat(formData.protein_content) : undefined,
    };
    try {
      await api.post('/milk/', payload);
      router.push('/milk');
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  if (isLoading || loading) return <p>Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Nova Produção de Leite</h1>
      <Link href="/milk" className="text-blue-600 hover:underline block mb-4">
        ← Voltar
      </Link>
      {error && <div className="bg-red-100 p-2 mb-4 text-red-700">{error}</div>}
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow space-y-4">
        <div>
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
        <div>
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
        <div>
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
        <div>
          <label className="block text-sm font-medium mb-1">Período</label>
          <select
            name="period"
            value={formData.period}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          >
            <option value="morning">Manhã</option>
            <option value="afternoon">Tarde</option>
            <option value="night">Noite</option>
          </select>
        </div>
        <div>
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
        <div>
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
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Salvar
        </button>
      </form>
    </div>
  );
}