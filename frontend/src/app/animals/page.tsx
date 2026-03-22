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

  const handleDelete = async (id: string) => {
    if (!confirm(t('Animals.confirmDelete'))) return;
    try {
      await api.delete(`/animals/${id}`);
      setAnimals(animals.filter(a => a.id !== id));
    } catch (err) {
      console.error(err);
      alert(extractErrorMessage(err) || t('Animals.deleteError'));
    }
  };

  if (isLoading || loading) return <p className="p-4 sm:p-6">{t('Common.loading')}</p>;
  if (!user) return null;

  return (
    <div className="p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <h1 className="text-xl sm:text-2xl font-bold">{t('Animals.title')}</h1>
          <Link href="/dashboard" className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm">
            {t('Common.dashboard')}
          </Link>
        </div>
        <Link href="/animals/new" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm w-full sm:w-auto text-center">
          {t('Animals.new')}
        </Link>
      </div>

      <div className="bg-white p-4 rounded shadow mb-6">
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

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {animals.length === 0 ? (
        <p className="text-sm">{t('Animals.noAnimals')}</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(animals || []).map(animal => {
         const statusKey = `Animals.statusOptions.${animal.status}`;
            const translatedStatus = t(statusKey) !== statusKey ? t(statusKey) : animal.status;

            return (
              <div key={animal.id} className="border p-4 rounded shadow-sm hover:shadow transition">
                <p className="mb-1"><strong className="text-sm sm:text-base">{t('Animals.earring')}:</strong> <span className="text-sm sm:text-base">{animal.tag_id}</span></p>
                <p className="mb-1"><strong className="text-sm sm:text-base">{t('Animals.name')}:</strong> <span className="text-sm sm:text-base">{animal.name || '—'}</span></p>
                <p className="mb-1"><strong className="text-sm sm:text-base">{t('Animals.breed')}:</strong> <span className="text-sm sm:text-base">{animal.breed || '—'}</span></p>
                <p className="mb-1"><strong className="text-sm sm:text-base">{t('Animals.status')}:</strong> <span className="text-sm sm:text-base">{translatedStatus}</span></p>
                <div className="flex gap-2 mt-3">
                  <Link
                    href={`/animals/${animal.id}/edit`}
                    className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600"
                  >
                    {t('Common.edit')}
                  </Link>
                  <button
                    onClick={() => handleDelete(animal.id)}
                    className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                  >
                    {t('Common.delete')}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}


