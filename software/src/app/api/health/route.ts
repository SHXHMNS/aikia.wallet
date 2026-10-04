import { NextResponse } from 'next/server';
import { walletStatus } from '@/lib/wallet/provider';

export const dynamic = 'force-dynamic';

export async function GET() {
  const databaseConfigured = Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
    (process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) &&
    (process.env.SUPABASE_SECRET_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY),
  );
  return NextResponse.json({
    app: 'aikia.wallet',
    wallet: walletStatus(),
    databaseConfigured,
    customerJoinRateLimitConfigured: Boolean(process.env.JOIN_RATE_LIMIT_SECRET),
  });
}
