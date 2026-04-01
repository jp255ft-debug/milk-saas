'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import api, { extractErrorMessage } from '@/lib/api';
import { useRouter, usePathname } from 'next/navigation';

interface User {
  id: string;
  email: string;
  farm_name: string;
  owner_name: string;
}

interface RegisterData {
  email: string;
  password: string;
  farm_name: string;
  owner_name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const MAX_PASSWORD_BYTES = 72;

const validatePasswordLength = (password: string) => {
  const byteLength = new TextEncoder().encode(password).length;
  if (byteLength > MAX_PASSWORD_BYTES) {
    throw new Error(`A senha excede o limite de ${MAX_PASSWORD_BYTES} bytes. Por favor, use uma senha mais curta.`);
  }
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const fetchUser = async () => {
    try {
      const res = await api.get('/auth/me');
      setUser({
        id: res.data.id,
        email: res.data.email,
        farm_name: res.data.farm_name,
        owner_name: res.data.owner_name || res.data.name || 'Produtor',
      });
    } catch (err) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Busca usuário sempre que a rota mudar (mantém estado sincronizado)
  useEffect(() => {
    fetchUser();
  }, [pathname]);

  const login = async (email: string, password: string) => {
    validatePasswordLength(password);
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      // Aguarda o fetchUser para garantir que o cookie já está sendo usado
      await fetchUser();

      router.push('/dashboard');
    } catch (err: any) {
      throw new Error(extractErrorMessage(err));
    }
  };

  const register = async (data: RegisterData) => {
    validatePasswordLength(data.password);
    try {
      await api.post('/auth/register', data);
      // Registro concluído; redireciona para login sem tentar logar automaticamente
      router.push('/login?registered=true');
    } catch (err: any) {
      throw new Error(extractErrorMessage(err));
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (err) {
      console.error('Erro no logout', err);
    } finally {
      setUser(null);
      router.push('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}