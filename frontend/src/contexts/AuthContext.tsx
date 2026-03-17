'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import api, { extractErrorMessage } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
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

interface RegisterData {
  email: string;
  password: string;
  farm_name: string;
  owner_name: string;
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

  const fetchUser = async () => {
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
    } catch (err) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (email: string, password: string) => {
    validatePasswordLength(password);
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    try {
      await api.post('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
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
      await login(data.email, data.password);
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
