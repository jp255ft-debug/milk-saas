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
  period?: string;
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

  const mapBackendData = (backendData: any[]): MilkProduction[] => {
    return backendData.map(item => ({
      id: item.id,
      animal_id: item.animal_id,
      production_date: item.date || item.production_date || '',
      liters_produced: (item.morning || 0) + (item.afternoon || 0) + (item.evening || 0),
      period: undefined,
      fat_content: undefined,
      protein_content: undefined,
    }));
  };

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [animalsRes, productionsRes] = await Promise.all([
        api.get('/animals/'),
        api.get('/milk/'),
      ]);
      setAnimals(animalsRes.data);
      const mappedProductions = mapBackendData(productionsRes.data);
      setProductions(mappedProductions);
      computeSummary(mappedProductions);
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const computeSummary = (productionsData: MilkProduction[]) => {
    const total = productionsData.reduce((acc, p) => acc + p.liters_produced, 0);
    const perAnimalMap = new Map<string, number>();
    productionsData.forEach(p => {
      const current = perAnimalMap.get(p.animal_id) || 0;
      perAnimalMap.set(p.animal_id, current + p.liters_produced);
    });
    const perAnimal = Array.from(perAnimalMap.entries()).map(([animal_id, totalLiters]) => {
      const animal = animals.find(a => a.id === animal_id);
      return {
        animal_id,
        animal_name: animal?.name,
        tag_id: animal?.tag_id,
        total: totalLiters,
      };
    });
    setSummary({ total_liters: total, per_animal: perAnimal });
  };

  const applyFilters = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filters.animal_id) params.append('animal_id', filters.animal_id);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      const productionsRes = await api.get(`/milk/?${params.toString()}`);
      const filteredProductions = mapBackendData(productionsRes.data);
      setProductions(filteredProductions);
      computeSummary(filteredProductions);
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

  if (isLoading || loading) return <p className="p-4 sm:p-6">Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-4 sm:p-6">
      {/* Cabeçalho */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <h1 className="text-xl sm:text-2xl font-bold">Produção de Leite</h1>
          <Link href="/dashboard" className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm">
            Dashboard
          </Link>
        </div>
        <Link href="/milk/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm w-full sm:w-auto text-center">
          Nova Produção
        </Link>
      </div>

      {/* Acesso Rápido */}
      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-4">Acesso Rápido</h2>
        <div className="flex flex-wrap gap-2">
          <Link href="/animals" className="flex-1 min-w-[120px] text-center bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700">
            Gerenciar Animais
          </Link>
          <Link href="/milk" className="flex-1 min-w-[120px] text-center bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700">
            Produção de Leite
          </Link>
          <Link href="/finance" className="flex-1 min-w-[120px] text-center bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700">
            Financeiro
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Filtros */}
      <div className="mt-6 bg-gray-100 p-4 rounded">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
          <h2 className="text-lg sm:text-xl font-semibold">Filtros</h2>
          <button
            onClick={handleDownloadReport}
            className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 text-sm w-full sm:w-auto"
          >
            Baixar Relatório PDF
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <select
            name="animal_id"
            value={filters.animal_id}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 text-base"
          >
            <option value="">Todos os animais</option>
            {(animals || []).map(a => (
              <option key={a.id} value={a.id}>{a.name || a.tag_id}</option>
            ))}
          </select>
          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 text-base"
            placeholder="Data inicial"
          />
          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 text-base"
            placeholder="Data final"
          />
          <button
            onClick={applyFilters}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm"
          >
            Aplicar
          </button>
        </div>
      </div>

      {/* Resumo */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded">
          <h3 className="text-lg font-medium">Total de leite</h3>
          <p className="text-2xl sm:text-3xl font-bold">{(summary?.total_liters || 0).toFixed(2)} L</p>
        </div>
        <div className="bg-green-50 p-4 rounded">
          <h3 className="text-lg font-medium">Produção por animal</h3>
          <ul className="list-disc list-inside">
            {(summary?.per_animal || []).map((item) => (
              <li key={item.animal_id} className="text-sm">
                {item.animal_name || item.tag_id}: {(item.total || 0).toFixed(2)} L
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Registros */}
      <div className="mt-6">
        <h2 className="text-lg sm:text-xl font-semibold mb-2">Registros</h2>
        {productions.length === 0 ? (
          <p>Nenhuma produção registrada.</p>
        ) : (
          <>
            {/* Versão mobile (cards) */}
            <div className="block sm:hidden space-y-4">
              {(productions || []).map(p => (
                <div key={p.id} className="bg-white p-4 rounded shadow border">
                  <p><strong>Data:</strong> {p.production_date ? p.production_date.split('-').reverse().join('/') : '—'}</p>
                  <p><strong>Animal:</strong> {getAnimalName(p.animal_id)}</p>
                  <p><strong>Litros:</strong> {p.liters_produced}</p>
                  <p><strong>Período:</strong> {p.period || '—'}</p>
                  <p><strong>Gordura:</strong> {p.fat_content || '—'}</p>
                  <p><strong>Proteína:</strong> {p.protein_content || '—'}</p>
                  <div className="flex justify-end gap-4 mt-2">
                    <Link href={`/milk/${p.id}/edit`} className="text-blue-600 hover:underline">
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
                  </div>
                </div>
              ))}
            </div>

            {/* Versão desktop (tabela) */}
            <div className="hidden sm:block overflow-x-auto">
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
                  {(productions || []).map(p => (
                    <tr key={p.id}>
                      <td className="border px-4 py-2">{p.production_date ? p.production_date.split('-').reverse().join('/') : '—'}</td>
                      <td className="border px-4 py-2">{getAnimalName(p.animal_id)}</td>
                      <td className="border px-4 py-2">{p.liters_produced}</td>
                      <td className="border px-4 py-2">{p.period || '—'}</td>
                      <td className="border px-4 py-2">{p.fat_content || '—'}</td>
                      <td className="border px-4 py-2">{p.protein_content || '—'}</td>
                      <td className="border px-4 py-2 whitespace-nowrap">
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
            </div>
          </>
        )}
      </div>
    </div>
  );
}