import type { Metadata } from 'next';
import { connection } from 'next/server';
import './globals.css';
import { platform } from '@/config/platform';

export const metadata: Metadata = {
  title: `${platform.name} | Venue Console`,
  description: `${platform.name} venue membership and wallet-card operator console.`,
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  // The proxy sets a per-request CSP nonce, so every page must render per request to receive it.
  await connection();
  return <html lang="en"><body>{children}</body></html>;
}
