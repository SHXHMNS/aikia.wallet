import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AIKIA.WALLET | Venue Console',
  description: 'AIKIA.WALLET venue membership and Google Wallet operator console.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
