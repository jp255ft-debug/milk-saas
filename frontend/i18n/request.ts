import {getRequestConfig} from 'next-intl/server';

const messageImports = {
  pt: () => import('../messages/pt.json').then(m => m.default),
  en: () => import('../messages/en.json').then(m => m.default),
} as const;

export default getRequestConfig(async ({locale}) => {
  const localeKey = locale === 'en' ? 'en' : 'pt';
  const messages = await messageImports[localeKey]();
  return { messages, locale: localeKey };
});