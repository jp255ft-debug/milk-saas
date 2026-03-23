
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter, useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import api, { extractErrorMessage } from '@/lib/api';

interface Animal {
  id: string;
  tag_id: string;
  name: string;
  breed: string;
  status: string;
}

export default function EditAnimalPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const [formData, setFormData] = useState({
    tag_id: '',
    name: '',
    breed: '',
    status: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) router.push('/login');
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user && params.id) {
      api.get(`/animals/${params.id}`)
        .then(res => {
          const animal = res.data;
          setFormData({
            tag_id: animal.tag_id,
            name: animal.name,
            breed: animal.breed,
            status: animal.status,
          });
        })
        .catch(err => setError(extractErrorMessage(err)))
        .finally(() => setLoading(false));
    }
  }, [user, params.id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.put(`/animals/${params.id}`, formData);
      router.push('/animals');
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  };

  if (isLoading || loading) return <p>Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Editar Animal</h1>
      <Link href="/animals" className="text-blue-600 hover:underline block mb-4">← Voltar</Link>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="max-w-lg bg-white p-6 rounded shadow">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Brinco *</label>
          <input name="tag_id" value={formData.tag_id} onChange={handleChange} required className="w-full border rounded px-3 py-2" />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Nome</label>
          <input name="name" value={formData.name} onChange={handleChange} className="w-full border rounded px-3 py-2" />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Raça</label>
          <input name="breed" value={formData.breed} onChange={handleChange} className="w-full border rounded px-3 py-2" />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Status *</label>
          <select name="status" value={formData.status} onChange={handleChange} required className="w-full border rounded px-3 py-2">
            <option value="lactation">Lactação</option>
            <option value="dry">Seca</option>
            <option value="heifer">Novilha</option>
            <option value="calf">Bezerra</option>
          </select>
        </div>
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Salvar</button>
      </form>
    </div>
  );
}
