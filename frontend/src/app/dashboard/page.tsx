'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import api, { extractErrorMessage } from '@/lib/api';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DashboardData {
  total_animals: number;
  lactating_animals: number;
  avg_production_per_animal: number;
  production_last_7_days: { date: string; total: number }[];
  top_5_animals: { id: string; name: string; total: number }[];
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

  // Altura responsiva dos gráficos
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

  const chartData = data.production_last_7_days.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  }));

  return (
    <div className="p-4 sm:p-6">
      {/* Cabeçalho responsivo */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">{t('Common.dashboard')}</h1>
        <button
          onClick={logout}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 w-full sm:w-auto"
        >
          {t('Auth.logout')}
        </button>
      </div>

      {/* Cards KPI */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-100 p-4 rounded shadow">
          <h3 className="text-sm sm:text-base font-semibold">{t('Animals.total')}</h3>
          <p className="text-2xl sm:text-3xl font-bold">{data.total_animals}</p>
        </div>
        <div className="bg-green-100 p-4 rounded shadow">
          <h3 className="text-sm sm:text-base font-semibold">{t('Animals.lactating')}</h3>
          <p className="text-2xl sm:text-3xl font-bold">{data.lactating_animals}</p>
        </div>
        <div className="bg-yellow-100 p-4 rounded shadow sm:col-span-2 lg:col-span-1">
          <h3 className="text-sm sm:text-base font-semibold">{t('Animals.avgProduction')}</h3>
          <p className="text-2xl sm:text-3xl font-bold">{data.avg_production_per_animal.toFixed(2)} L</p>
          <p className="text-xs sm:text-sm">(últimos 30 dias)</p>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-4">{t('Milk.dailyProduction')}</h2>
          <ResponsiveContainer width="100%" height={chartHeight}>
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="total" stroke="#3b82f6" name={t('Milk.liters')} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top 5 Animais - com fallback para lista no celular */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg sm:text-xl font-semibold mb-4">{t('Milk.topAnimals')}</h2>
          
          {/* Mobile: lista */}
          <div className="block sm:hidden">
            <ul className="divide-y divide-gray-200">
              {data.top_5_animals.map((animal, index) => (
                <li key={animal.id} className="py-2 flex justify-between">
                  <span className="font-medium">{index + 1}. {animal.name}</span>
                  <span className="text-green-600 font-bold">{animal.total.toFixed(2)} L</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Desktop: gráfico */}
          <div className="hidden sm:block">
            <ResponsiveContainer width="100%" height={chartHeight}>
              <BarChart data={data.top_5_animals} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="total" fill="#10b981" name={t('Milk.liters')} />
              </BarChart>
            </ResponsiveContainer>
          </div>
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