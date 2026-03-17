import {NextIntlClientProvider} from 'next-intl';
import {getMessages, getLocale} from 'next-intl/server';
import { AuthProvider } from '@/contexts/AuthContext';
import './globals.css';

export default async function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          <AuthProvider>
            {children}
          </AuthProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}