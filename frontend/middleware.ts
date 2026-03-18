import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  locales: ['pt', 'en'],
  defaultLocale: 'pt',
  localePrefix: 'never'
});

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)']
};
