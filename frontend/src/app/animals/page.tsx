'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import api, { extractErrorMessage } from '@/lib/api';

interface Animal {
  id: string;
  tag_id: string;
  name: string;
  breed: string;
  status: string;
}

export default function AnimalsPage() {
  const t = useTranslations();
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [animals, setAnimals] = useState<Animal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  useEffect(() => {
    if (user) {
      api.get('/animals/')
        .then(res => setAnimals(res.data))
        .catch(err => {
          console.error(err);
          setError(extractErrorMessage(err));
        })
        .finally(() => setLoading(false));
    }
  }, [user]);

  if (isLoading || loading) return <p className="p-6">{t('Common.loading')}</p>;
  if (!user) return null;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">{t('Animals.title')}</h1>
          <Link href="/dashboard" className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
            {t('Common.dashboard')}
          </Link>
        </div>
        <Link href="/animals/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          {t('Animals.new')}
        </Link>
      </div>

      <div className="bg-white p-4 rounded shadow mb-6">
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

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {animals.length === 0 ? (
        <p>{t('Animals.noAnimals')}</p>
      ) : (
        <ul className="space-y-2">
          {animals.map(animal => {
            // Tenta obter a tradução; se não existir, usa o valor original
            const statusKey = `Animals.statusOptions.${animal.status}`;
            const translatedStatus = t(statusKey) !== statusKey ? t(statusKey) : animal.status;

            return (
              <li key={animal.id} className="border p-4 rounded">
                <p><strong>{t('Animals.earring')}:</strong> {animal.tag_id}</p>
                <p><strong>{t('Animals.name')}:</strong> {animal.name || '—'}</p>
                <p><strong>{t('Animals.breed')}:</strong> {animal.breed || '—'}</p>
                <p><strong>{t('Animals.status')}:</strong> {translatedStatus}</p>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}