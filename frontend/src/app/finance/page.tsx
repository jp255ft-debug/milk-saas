'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import api, { extractErrorMessage } from '@/lib/api';

interface Category {
  id: string;
  name: string;
  type: string;
}

interface Transaction {
  id: string;
  category_id: string;
  description: string;
  amount: number;
  transaction_date: string;
  is_paid: boolean;
  category?: Category;
}

// ATUALIZADO: Nomes batendo com o novo retorno do FastAPI
interface MonthlySummary {
  receitas: number;
  despesas: number;
  saldo_liquido: number;
}

export default function FinancePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    type: '',
  });

  // ATUALIZADO: Inicialização com chaves em português
  const [summary, setSummary] = useState<MonthlySummary>({ 
    receitas: 0, 
    despesas: 0, 
    saldo_liquido: 0 
  });

  useEffect(() => {
    if (!isLoading && !user) router.push('/login');
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      Promise.all([
        fetchCategories(),
        fetchTransactions(),
        fetchMonthlySummary()
      ]).catch(err => {
        console.error('Erro ao carregar dados financeiros:', err);
        const msg = extractErrorMessage(err);
        setError(typeof msg === 'string' ? msg : 'Erro desconhecido');
      });
    }
  }, [user]);

  const fetchCategories = async () => {
    try {
      const res = await api.get('/finance/categories');
      setCategories(res.data);
    } catch (err) {
      console.error('Erro ao buscar categorias:', err);
      throw err;
    }
  };

  const fetchTransactions = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.type) params.append('type', filters.type);
      const res = await api.get(`/finance/transactions?${params.toString()}`);
      setTransactions(res.data);
    } catch (err) {
      console.error('Erro ao buscar transações:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchMonthlySummary = async () => {
    try {
      const now = new Date();
      // O backend agora retorna receitas, despesas e saldo_liquido
      const res = await api.get(`/finance/summary?year=${now.getFullYear()}&month=${now.getMonth() + 1}`);
      setSummary(res.data);
    } catch (err) {
      console.error('Erro ao buscar resumo:', err);
      throw err;
    }
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const applyFilters = async () => {
    try {
      await fetchTransactions();
    } catch (err) {
      const msg = extractErrorMessage(err);
      setError(typeof msg === 'string' ? msg : 'Erro ao aplicar filtros');
    }
  };

  const handleDownloadReport = async () => {
    if (!filters.start_date || !filters.end_date) {
      alert('Selecione as datas inicial e final para gerar o relatório.');
      return;
    }
    setError('');
    try {
      // CORRIGIDO: Rota agora é /report/pdf
      const response = await api.get(`/finance/report/pdf?start_date=${filters.start_date}&end_date=${filters.end_date}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `relatorio_financeiro_${filters.start_date}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro ao baixar relatório:', err);
      const msg = extractErrorMessage(err);
      setError(typeof msg === 'string' ? msg : 'Erro ao baixar relatório');
    }
  };

  const getCategoryName = (catId: string) => {
    const cat = categories.find(c => c.id === catId);
    return cat ? cat.name : catId;
  };

  const formatCurrency = (value: number) => {
    // PROTEÇÃO: Garante que se o valor for nulo ou NaN, mostre 0
    const safeValue = value || 0;
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(safeValue);
  };

  if (isLoading) return <p className="p-4 sm:p-6">Carregando...</p>;
  if (!user) return null;

  return (
    <div className="p-4 sm:p-6">
      {/* Cabeçalho */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <h1 className="text-xl sm:text-2xl font-bold">Financeiro</h1>
          <Link href="/dashboard" className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm">
            Dashboard
          </Link>
        </div>
        <Link href="/finance/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm w-full sm:w-auto text-center">
          Nova Transação
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

      {/* Resumo do mês (CORRIGIDO) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-green-100 p-4 rounded shadow border border-green-200">
          <h3 className="text-sm sm:text-base font-semibold text-green-800">Receitas</h3>
          <p className="text-2xl sm:text-3xl font-bold text-green-700">{formatCurrency(summary.receitas)}</p>
        </div>
        <div className="bg-red-100 p-4 rounded shadow border border-red-200">
          <h3 className="text-sm sm:text-base font-semibold text-red-800">Despesas</h3>
          <p className="text-2xl sm:text-3xl font-bold text-red-700">{formatCurrency(summary.despesas)}</p>
        </div>
        <div className="bg-blue-100 p-4 rounded shadow border border-blue-200">
          <h3 className="text-sm sm:text-base font-semibold text-blue-800">Saldo</h3>
          <p className={`text-2xl sm:text-3xl font-bold ${summary.saldo_liquido >= 0 ? 'text-blue-700' : 'text-red-700'}`}>
            {formatCurrency(summary.saldo_liquido)}
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-gray-100 p-4 rounded mb-6">
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
          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 text-base"
          />
          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 text-base"
          />
          <select
            name="type"
            value={filters.type}
            onChange={handleFilterChange}
            className="border rounded px-3 py-2 text-base"
          >
            <option value="">Todos os tipos</option>
            <option value="variable_cost">Despesas Variáveis</option>
            <option value="fixed_cost">Despesas Fixas</option>
            <option value="revenue">Receitas</option>
          </select>
          <button
            onClick={applyFilters}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm"
          >
            Aplicar
          </button>
        </div>
      </div>

      {/* Lista de transações */}
      <h2 className="text-lg sm:text-xl font-semibold mb-2">Transações</h2>
      {loading ? (
        <p>Carregando...</p>
      ) : transactions.length === 0 ? (
        <p>Nenhuma transação registrada.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border">
            <thead>
              <tr className="bg-gray-50">
                <th className="border px-4 py-2 text-left">Data</th>
                <th className="border px-4 py-2 text-left">Categoria</th>
                <th className="border px-4 py-2 text-left">Descrição</th>
                <th className="border px-4 py-2 text-left">Valor</th>
                <th className="border px-4 py-2 text-left">Pago</th>
                <th className="border px-4 py-2 text-left">Ações</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(t => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="border px-4 py-2">{t.transaction_date.split("-").reverse().join("/")}</td>
                  <td className="border px-4 py-2">{getCategoryName(t.category_id)}</td>
                  <td className="border px-4 py-2">{t.description || '—'}</td>
                  <td className={`border px-4 py-2 font-bold ${t.category?.type === 'revenue' ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(t.amount)}
                  </td>
                  <td className="border px-4 py-2">{t.is_paid ? 'Sim' : 'Não'}</td>
                  <td className="border px-4 py-2">
                    <div className="flex gap-3">
                      <Link href={`/finance/${t.id}/edit`} className="text-blue-600 hover:underline">Editar</Link>
                      <button
                        onClick={async () => {
                          if (confirm('Remover esta transação?')) {
                            try {
                              await api.delete(`/finance/transactions/${t.id}`);
                              await Promise.all([fetchTransactions(), fetchMonthlySummary()]);
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
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Link para custo por litro */}
      <div className="mt-6">
        <Link href="/finance/cost-per-liter" className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 text-sm inline-block">
          Calcular Custo por Litro
        </Link>
      </div>
    </div>
  );
}