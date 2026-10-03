import { NextResponse, type NextRequest } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');
  const next = request.nextUrl.searchParams.get('next');
  const safeNext = next?.startsWith('/') && !next.startsWith('//') ? next : '/';
  if (!code) return NextResponse.redirect(new URL('/login?error=missing_code', request.url));
  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.auth.exchangeCodeForSession(code);
  if (error) return NextResponse.redirect(new URL('/login?error=sign_in_failed', request.url));
  return NextResponse.redirect(new URL(safeNext, request.url));
}
