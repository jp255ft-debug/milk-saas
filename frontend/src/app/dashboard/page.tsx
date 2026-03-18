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

  if (isLoading || loading) {
    return <div className="p-6">{t('Common.loading')}</div>;
  }

  if (!user) return null;

  if (error) {
    return (
      <div className="p-6">
        <p className="text-red-500">{error}</p>
        <button
          onClick={fetchDashboardData}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
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
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">{t('Common.dashboard')}</h1>
        <button
          onClick={logout}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          {t('Auth.logout')}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-100 p-4 rounded shadow">
          <h3 className="text-lg font-semibold">{t('Animals.total')}</h3>
          <p className="text-3xl font-bold">{data.total_animals}</p>
        </div>
        <div className="bg-green-100 p-4 rounded shadow">
          <h3 className="text-lg font-semibold">{t('Animals.lactating')}</h3>
          <p className="text-3xl font-bold">{data.lactating_animals}</p>
        </div>
        <div className="bg-yellow-100 p-4 rounded shadow">
          <h3 className="text-lg font-semibold">{t('Animals.avgProduction')}</h3>
          <p className="text-3xl font-bold">{data.avg_production_per_animal.toFixed(2)} L</p>
          <p className="text-sm">(últimos 30 dias)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">{t('Milk.dailyProduction')}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="total" stroke="#3b82f6" name={t('Milk.liters')} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">{t('Milk.topAnimals')}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.top_5_animals}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total" fill="#10b981" name={t('Milk.liters')} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">{t('Common.quickAccess')}</h2>
        <div className="flex flex-wrap gap-4">
          <Link href="/animals" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            {t('Animals.manage')}
          </Link>
          <Link href="/milk" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            {t('Common.milkProduction')}
          </Link>
          <Link href="/finance" className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
            {t('Common.finance')}
          </Link>
        </div>
      </div>
    </div>
  );
}