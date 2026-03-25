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

  // Como estamos usando Cookies Seguros (HttpOnly), não precisamos ler o localStorage.
  // Basta perguntar ao backend quem somos sempre que a página carrega ou a rota muda.
  useEffect(() => {
    fetchUser();
  }, [pathname]);

  const login = async (email: string, password: string) => {
    validatePasswordLength(password);
    try {
      // 1. O FastAPI exige envio via Formulário (URLSearchParams)
      // 2. O campo deve obrigatoriamente se chamar "username"
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      // Dispara o login
      await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      // Se passou, o backend já salvou o Cookie de acesso no navegador.
      // Agora buscamos os dados do usuário para preencher a tela.
      await fetchUser();
      
      // Redireciona para o painel
      router.push('/dashboard');
    } catch (err: any) {
      throw new Error(extractErrorMessage(err));
    }
  };

  const register = async (data: RegisterData) => {
    validatePasswordLength(data.password);
    try {
      // Registro continua sendo JSON normal
      await api.post('/auth/register', data);
      await login(data.email, data.password);
    } catch (err: any) {
      throw new Error(extractErrorMessage(err));
    }
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout'); // O backend apaga o cookie
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