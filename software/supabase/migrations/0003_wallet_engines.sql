-- Wallet engines: PassKit today, our own Google/Apple adapters later.
-- A member can now hold one card per provider (e.g. Google and Apple side by side),
-- and each venue can point at its own engine-side program (PassKit program ID).

alter table public.wallet_passes drop constraint wallet_passes_pkey;
alter table public.wallet_passes add primary key (member_id, provider);

alter table public.wallet_passes drop constraint wallet_passes_provider_check;
alter table public.wallet_passes add constraint wallet_passes_provider_check check (provider in ('google', 'apple', 'passkit'));

create index if not exists wallet_passes_venue_object_idx on public.wallet_passes(venue_id, provider_object_id);

alter table public.venues add column if not exists wallet_program_id text
  check (wallet_program_id is null or wallet_program_id ~ '^[A-Za-z0-9_-]{1,64}$');
