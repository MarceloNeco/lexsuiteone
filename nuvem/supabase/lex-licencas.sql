-- LexSuiteONE · RADAR JUDICIAL: licenças, quem usa e instalações.
-- Revisar antes de rodar. Rodar uma vez no SQL Editor do projeto solverone-app (Supabase).
-- Nenhuma tabela tem política de acesso: só a função lex-conta (com a chave de serviço, que fica no Supabase) lê e grava.

create table if not exists public.lex_contas (
  codigo     text primary key check (codigo ~ '^LEX-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$'),
  escritorio text not null,
  doc_tipo   text check (doc_tipo is null or doc_tipo in ('cnpj', 'cpf', 'passaporte')),
  documento  text check (documento is null or documento ~ '^[0-9A-Z]{5,20}$'),
  max_pessoas integer check (max_pessoas is null or max_pessoas > 0),
  ativo      boolean not null default true,
  validade   date,
  mensagem   text not null default '',
  criado_em  timestamptz not null default now()
);
comment on table public.lex_contas is 'RADAR JUDICIAL: uma linha por escritório (licença). Desativar: ativo = false. Vencer: validade. Limitar pessoas: max_pessoas (vazio = sem limite). mensagem aparece na tela do escritório. documento: CNPJ (com ou sem letras), CPF ou passaporte, só números e letras.';

create table if not exists public.lex_usuarios (
  email         text primary key check (email = lower(email) and email like '%_@_%._%'),
  codigo        text not null references public.lex_contas(codigo) on update cascade,
  nome          text not null,
  papel         text not null default '',
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);
comment on table public.lex_usuarios is 'RADAR JUDICIAL: quem usa. O e-mail é a chave: um e-mail pertence a um escritório só.';

create table if not exists public.lex_instalacoes (
  instalacao   text primary key check (instalacao ~ '^[0-9a-f]{16}$'),
  codigo       text not null references public.lex_contas(codigo) on update cascade,
  email        text references public.lex_usuarios(email) on update cascade on delete set null,
  versao       text not null default '',
  primeira_vez timestamptz not null default now(),
  ultima_vez   timestamptz not null default now()
);
comment on table public.lex_instalacoes is 'RADAR JUDICIAL: cada computador instalado (identificação aleatória, nada pessoal), a versão e a última vez que conferiu a licença.';

alter table public.lex_contas      enable row level security;
alter table public.lex_usuarios    enable row level security;
alter table public.lex_instalacoes enable row level security;
revoke all on public.lex_contas, public.lex_usuarios, public.lex_instalacoes from anon, authenticated;

-- Cria a licença de um escritório e devolve o código LEX-XXXX-XXXX (sem 0/O e 1/I).
-- Uso: select public.lex_criar_conta('KR Law');            (sem validade)
--      select public.lex_criar_conta('KR Law', '2027-01-31');
create or replace function public.lex_criar_conta(p_escritorio text, p_validade date default null)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  alfabeto constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  bytes bytea; corpo text; novo text;
begin
  loop
    bytes := extensions.gen_random_bytes(8);
    corpo := '';
    for i in 0..7 loop
      corpo := corpo || substr(alfabeto, 1 + (get_byte(bytes, i) % 32), 1);
    end loop;
    novo := 'LEX-' || substr(corpo, 1, 4) || '-' || substr(corpo, 5, 4);
    begin
      insert into public.lex_contas (codigo, escritorio, validade) values (novo, trim(p_escritorio), p_validade);
      return novo;
    exception when unique_violation then
      -- código repetido (raríssimo): tenta outro
    end;
  end loop;
end $$;
revoke all on function public.lex_criar_conta(text, date) from public, anon, authenticated;

-- Neste projeto, tabela nova não dá acesso automático à chave de serviço: a função lex-conta precisa disto.
grant select, insert, update on public.lex_contas, public.lex_usuarios, public.lex_instalacoes to service_role;
