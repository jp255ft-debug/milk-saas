'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api, { extractErrorMessage } from '@/lib/api';

interface MilkProduction {
  id: string;
  animal_id: string;
  production_date: string;
  liters_produced: number;
  period: string;
  fat_content?: number;
  protein_content?: number;
  animal_name?: string;
}

interface Animal {
  id: string;
  name: string;
  tag_id: string;
}

interface Summary {
  total_liters: number;
  per_animal: Array<{
    animal_id: string;
    animal_name?: string;
    tag_id?: string;
    total: number;
  }>;
}

export default function MilkPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [productions, setProductions] = useState<MilkProduction[]>([]);
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    animal_id: '',
    start_date: '',
    end_date: '',
  });
  const [summary, setSummary] = useState<Summary>({ total_liters: 0, per_animal: [] });

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [animalsRes, productionsRes, summaryRes] = await Promise.all([
        api.get('/animals/'),
        api.get('/milk/'),
        api.get('/milk/summary/totals')
      ]);
      setAnimals(animalsRes.data);
      setProductions(productionsRes.data);
      setSummary(summaryRes.data);
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filters.animal_id) params.append('animal_id', filters.animal_id);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      const [productionsRes, summaryRes] = await Promise.all([
        api.get(`/milk/?${params.toString()}`),
        api.get(`/milk/summary/totals?${params.toString()}`)
      ]);
      setProductions(productionsRes.data);
      setSummary(summaryRes.data);
    } catch (err) {
      console.error('Erro ao aplicar filtros:', err);
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const getAnimalName = (animalId: string) => {
    const animal = animals.find(a => a.id === animalId);
    return animal ? (animal.name || animal.tag_id) : animalId;
  };

  const handleDownloadReport = async () => {
    if (!filters.start_date || !filters.end_date) {
      alert('Selecione as datas inicial e final para gerar o relatório.');
      return;
    }
    setError('');
    try {
      const response = await api.get(`/milk/report?start_date=${filters.start_date}&end_date=${filters.end_date}`, {
        responseType: 'blob'
      });

      if (response.status !== 200 || response.headers['content-type'] !== 'application/pdf') {
        const errorText = await response.data.text();
        throw new Error(errorText);
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `relatorio_producao_${filters.start_date}_${filters.end_date}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro no download do relatório:', err);
      setError(extractErrorMessage(err));
    }
  };

  // Mapeamento para tradução dos períodos
  const periodoTexto: Record<string, string> = {
    morning: 'manhã',
    afternoon: 'tarde',
    night: 'noite',
  };

  if (isLoading || loading) return <p className="p-6">Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">Produção de Leite</h1>
          <Link href="/dashboard" className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
            Dashboard
          </Link>
        </div>
        <Link href="/milk/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Nova Produção
        </Link>
      </div>

      {/* Acesso Rápido */}
      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Acesso Rápido</h2>
        <div className="flex flex-wrap gap-4">
          <Link href="/animals" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Gerenciar Animais
          </Link>
          <Link href="/milk" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Produção de Leite
          </Link>
          <Link href="/finance" className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
            Financeiro
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="mt-6 bg-gray-100 p-4 rounded">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-semibold">Filtros</h2>
          <button
            onClick={handleDownloadReport}
            className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
          >
            Baixar Relatório PDF
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <select
            name="animal_id"
            value={filters.animal_id}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
          >
            <option value="">Todos os animais</option>
            {animals.map(a => (
              <option key={a.id} value={a.id}>{a.name || a.tag_id}</option>
            ))}
          </select>
          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
            placeholder="Data inicial"
          />
          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2"
            placeholder="Data final"
          />
          <button
            onClick={applyFilters}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            Aplicar
          </button>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <h3 className="text-lg font-medium">Total de leite</h3>
          <p className="text-3xl font-bold">{summary.total_liters.toFixed(2)} L</p>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <h3 className="text-lg font-medium">Produção por animal</h3>
          <ul className="list-disc list-inside">
            {summary.per_animal.map((item) => (
              <li key={item.animal_id}>
                {item.animal_name || item.tag_id}: {item.total.toFixed(2)} L
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Registros</h2>
        {productions.length === 0 ? (
          <p>Nenhuma produção registrada.</p>
        ) : (
          <table className="min-w-full bg-white border">
            <thead>
              <tr>
                <th className="border px-4 py-2">Data</th>
                <th className="border px-4 py-2">Animal</th>
                <th className="border px-4 py-2">Litros</th>
                <th className="border px-4 py-2">Período</th>
                <th className="border px-4 py-2">Gordura</th>
                <th className="border px-4 py-2">Proteína</th>
                <th className="border px-4 py-2">Ações</th>
              </tr>
            </thead>
            <tbody>
              {productions.map(p => (
                <tr key={p.id}>
                  {/* CORREÇÃO: exibe a data diretamente no formato DD/MM/AAAA */}
                  <td className="border px-4 py-2">
                    {p.production_date.split('-').reverse().join('/')}
                  </td>
                  <td className="border px-4 py-2">{getAnimalName(p.animal_id)}</td>
                  <td className="border px-4 py-2">{p.liters_produced}</td>
                  <td className="border px-4 py-2">{periodoTexto[p.period] || p.period || '—'}</td>
                  <td className="border px-4 py-2">{p.fat_content || '—'}</td>
                  <td className="border px-4 py-2">{p.protein_content || '—'}</td>
                  <td className="border px-4 py-2">
                    <Link href={`/milk/${p.id}/edit`} className="text-blue-600 hover:underline mr-2">
                      Editar
                    </Link>
                    <button
                      onClick={async () => {
                        if (confirm('Remover este registro?')) {
                          try {
                            await api.delete(`/milk/${p.id}`);
                            fetchData();
                          } catch (err) {
                            alert(extractErrorMessage(err));
                          }
                        }
                      }}
                      className="text-red-600 hover:underline"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}