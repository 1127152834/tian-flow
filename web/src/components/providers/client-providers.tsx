'use client';

import { LanguageProvider } from '~/contexts/language-context';

interface ClientProvidersProps {
  children: React.ReactNode;
}

export function ClientProviders({ children }: ClientProvidersProps) {
  return (
    <LanguageProvider>
      {children}
    </LanguageProvider>
  );
}
