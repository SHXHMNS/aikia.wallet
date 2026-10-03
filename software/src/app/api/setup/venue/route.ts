import { NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';

export async function POST(request: Request) {
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Sign in first.' }, { status: 401 });
  let input: unknown;
  try { input = await request.json(); } catch { return NextResponse.json({ error: 'Expected JSON.' }, { status: 400 }); }
  const body = input as { name?: unknown; slug?: unknown };
  const name = typeof body.name === 'string' ? body.name.trim() : '';
  const slug = typeof body.slug === 'string' ? body.slug.trim().toLowerCase() : '';
  if (name.length < 2 || name.length > 80 || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    return NextResponse.json({ error: 'Enter a venue name and a URL-safe slug.' }, { status: 400 });
  }
  const { data, error } = await supabase.rpc('create_venue', { p_name: name, p_slug: slug });
  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ venueId: data }, { status: 201 });
}
