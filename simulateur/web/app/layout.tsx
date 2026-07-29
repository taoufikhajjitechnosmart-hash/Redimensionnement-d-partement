import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Simulateur de dimensionnement — Techno Smart',
  description:
    'Dimensionnement des secteurs techniciens : délai J+2, effectif, kilomètres et couverture.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
