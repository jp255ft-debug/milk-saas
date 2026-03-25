'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import api, { extractErrorMessage } from '@/lib/api';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface MilkRecord {
  date: string;
  total: number;
}

interface TopAnimal {
  id?: string;
  name: string;
  total: number;
}

interface DashboardData {
  total_animals: number;
  lactating_animals: number;
  avg_production_per_animal: number;
  production_last_7_days: MilkRecord[];
  top_5_animals?: TopAnimal[];
}

export default function DashboardPage() {
  const t = useTranslations();
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const res = await api.get('/milk/dashboard');
      setData(res.data);
    } catch (err) {
      console.error('Erro ao buscar dados do dashboard:', err);
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const [chartHeight, setChartHeight] = useState(300);
  useEffect(() => {
    const handleResize = () => {
      setChartHeight(window.innerWidth < 640 ? 200 : 300);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (isLoading || loading) {
    return <div className="p-4 sm:p-6">{t('Common.loading')}</div>;
  }

  if (!user) return null;

  if (error) {
    return (
      <div className="p-4 sm:p-6">
        <p className="text-red-500">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full sm:w-auto"
        >
          {t('Common.tryAgain') || 'Tentar novamente'}
        </button>
      </div>
    );
  }

  if (!data) return null;

  // CORREÇÃO: Lê a variável correta que vem do FastAPI e formata a data para os gráficos
  const chartData = (data.production_last_7_days || []).map(record => ({
    date: new Date(record.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
    total: record.total || 0,
  }));

  const topAnimals = data.top_5_animals || [];

  return (
    <div className="p-4 sm:p-6">
      {/* Cabeçalho */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">{t('Common.dashboard')}</h1>
        <button
          onClick={logout}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 w-full sm:w-auto"
        >
          {t('Auth.logout')}
        </button>
      </div>

      {/* Cards de Resumo Modernos */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-100 p-4 rounded shadow border border-blue-200">
          <h3 className="text-sm sm:text-base font-semibold text-blue-800">Total de Animais</h3>
          <p className="text-2xl sm:text-4xl font-bold text-blue-900 mt-2">{data.total_animals || 0}</p>
        </div>
        
        <div className="bg-green-100 p-4 rounded shadow border border-green-200">
          <h3 className="text-sm sm:text-base font-semibold text-green-800">Animais em Lactação</h3>
          <p className="text-2xl sm:text-4xl font-bold text-green-900 mt-2">{data.lactating_animals || 0}</p>
        </div>
        
        <div className="bg-yellow-100 p-4 rounded shadow border border-yellow-200">
          <h3 className="text-sm sm:text-base font-semibold text-yellow-800">Média por Animal (30 d)</h3>
          <p className="text-2xl sm:text-4xl font-bold text-yellow-900 mt-2">{(data.avg_production_per_animal || 0).toFixed(2)} L</p>
        </div>
      </div>

      {/* Seção dos Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        
        {/* Gráfico de Linha (Últimos 7 dias) */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-4">Produção (Últimos 7 Dias)</h2>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="total" stroke="#3b82f6" name="Litros" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Gráfico de Barras / Lista (Top 5 Animais) */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-4">Top 5 Animais (30 Dias)</h2>
          {topAnimals.length === 0 ? (
            <p className="text-gray-500 text-sm">Nenhum dado de ranking disponível.</p>
          ) : (
            <>
              {/* Mobile: lista de texto */}
              <div className="block sm:hidden">
                <ul className="divide-y divide-gray-200">
                  {topAnimals.map((animal, index) => (
                    <li key={animal.id || index} className="py-2 flex justify-between">
                      <span className="font-medium">{index + 1}. {animal.name}</span>
                      <span className="text-green-600 font-bold">{(animal.total || 0).toFixed(2)} L</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Desktop: gráfico de barras */}
              <div className="hidden sm:block">
                <ResponsiveContainer width="100%" height={chartHeight}>
                  <BarChart data={topAnimals} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <Bar dataKey="total" fill="#10b981" name="Litros" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Acesso rápido */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-lg sm:text-xl font-semibold mb-4">{t('Common.quickAccess')}</h2>
        <div className="flex flex-wrap gap-2">
          <Link href="/animals" className="flex-1 min-w-[120px] text-center bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700">
            {t('Animals.manage')}
          </Link>
          <Link href="/milk" className="flex-1 min-w-[120px] text-center bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700">
            {t('Common.milkProduction')}
          </Link>
          <Link href="/finance" className="flex-1 min-w-[120px] text-center bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700">
            {t('Common.finance')}
          </Link>
        </div>
      </div>
    </div>
  );
}