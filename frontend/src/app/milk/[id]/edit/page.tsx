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
  
  // Atualizado para bater 100% com o seu banco de dados real (SQLAlchemy)
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
      
      // Preenche o form com os dados da API
      setFormData({
        animal_id: milk.animal_id || '',
        production_date: milk.production_date ? milk.production_date.split('T')[0] : '', // Garante que a data corte a hora se houver
        liters_produced: (milk.liters_produced || 0).toString(),
        period: milk.period || '',
        fat_content: milk.fat_content ? milk.fat_content.toString() : '',
        protein_content: milk.protein_content ? milk.protein_content.toString() : '',
      });
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      // Se não achar, avisa amigavelmente na tela em vez de explodir
      setError(extractErrorMessage(err) || "Produção não encontrada."); 
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
      // Monta o pacote de dados do jeito que a classe MilkProductionUpdate do FastAPI espera
      await api.put(`/milk/${params.id}`, {
        animal_id: formData.animal_id,
        production_date: formData.production_date,
        liters_produced: parseFloat(formData.liters_produced) || 0,
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
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-lg mx-auto">
        <h1 className="text-2xl font-bold mb-4 text-gray-800">Editar Produção</h1>
        <Link href="/milk" className="text-blue-600 hover:underline flex items-center mb-6">
          <span className="mr-1">←</span> Voltar
        </Link>
        
        {error && (
          <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}
        
        {/* Só mostra o form se a produção existir (esconde se for erro 404) */}
        {!error && (
          <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow border border-gray-200">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1 text-gray-700">Animal *</label>
              <select
                name="animal_id"
                value={formData.animal_id}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Selecione um animal</option>
                {animals.map(a => (
                  <option key={a.id} value={a.id}>{a.name || a.tag_id}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-1 text-gray-700">Data *</label>
              <input
                type="date"
                name="production_date"
                value={formData.production_date}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Litros Produzidos *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  name="liters_produced"
                  value={formData.liters_produced}
                  onChange={handleChange}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Período</label>
                <select
                  name="period"
                  value={formData.period}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Selecione</option>
                  <option value="morning">Manhã</option>
                  <option value="afternoon">Tarde</option>
                  <option value="evening">Noite</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Gordura (%)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  name="fat_content"
                  value={formData.fat_content}
                  onChange={handleChange}
                  placeholder="Ex: 3.5"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1 text-gray-700">Proteína (%)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  name="protein_content"
                  value={formData.protein_content}
                  onChange={handleChange}
                  placeholder="Ex: 3.2"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white font-medium px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Salvar Alterações
            </button>
          </form>
        )}
      </div>
    </div>
  );
}