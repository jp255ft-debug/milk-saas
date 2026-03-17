'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  // Se não estiver logado, não exibe a navbar (ou exibe uma versão simplificada)
  if (!user) return null;

  const isActive = (path: string) => pathname.startsWith(path);

  return (
    <nav className="bg-white shadow-md border-b border-gray-200 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600 hover:text-blue-800">
            Milk SaaS
          </Link>
          <div className="flex space-x-4">
            <Link
              href="/animals"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/animals')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Animais
            </Link>
            <Link
              href="/milk"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/milk')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Produção de Leite
            </Link>
            <Link
              href="/finance"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/finance')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Financeiro
            </Link>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">
            {user.farm_name} ({user.owner_name})
          </span>
          <button
            onClick={logout}
            className="bg-red-600 text-white px-4 py-2 rounded-md text-sm hover:bg-red-700 transition-colors"
          >
            Sair
          </button>
        </div>
      </div>
    </nav>
  );
}