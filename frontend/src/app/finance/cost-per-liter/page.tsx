'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api from '@/lib/api';

interface CostResult {
  period_start: string;
  period_end: string;
  total_expenses: number;
  total_liters: number;
  cost_per_liter: number;
  details: Record<string, number>;
}

// Função auxiliar para formatar data ISO (YYYY-MM-DD) para DD/MM/YYYY
const formatDate = (dateStr: string): string => {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  return `${day}/${month}/${year}`;
};

export default function CostPerLiterPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [startDate, setStartDate] = useState(
    new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]
  );
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [result, setResult] = useState<CostResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isLoading && !user) {
    router.push('/login');
    return null;
  }

  const handleCalculate = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/finance/cost-per-liter?start_date=${startDate}&end_date=${endDate}`);
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao calcular custo por litro');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Custo por Litro</h1>
      <Link href="/finance" className="text-blue-600 hover:underline block mb-4">
        ← Voltar ao Financeiro
      </Link>

      <div className="bg-gray-100 p-4 rounded mb-6">
        <h2 className="text-xl font-semibold mb-2">Selecione o período</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Data inicial</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Data final</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleCalculate}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Calculando...' : 'Calcular'}
            </button>
          </div>
        </div>
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      {result && (
        <div className="bg-white p-6 rounded shadow">
          <h2 className="text-xl font-semibold mb-4">Resultado</h2>
          {/* Formatação manual das datas */}
          <p>
            <strong>Período:</strong> {formatDate(result.period_start)} a {formatDate(result.period_end)}
          </p>
          <p><strong>Total de litros:</strong> {result.total_liters.toFixed(2)} L</p>
          <p><strong>Total de despesas:</strong> {formatCurrency(result.total_expenses)}</p>
          <p className="text-2xl font-bold mt-2">
            <strong>Custo por litro:</strong> {formatCurrency(result.cost_per_liter)}
          </p>

          {Object.keys(result.details).length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2">Detalhamento por categoria</h3>
              <ul className="list-disc list-inside">
                {Object.entries(result.details).map(([cat, val]) => (
                  <li key={cat}>{cat}: {formatCurrency(val)}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}