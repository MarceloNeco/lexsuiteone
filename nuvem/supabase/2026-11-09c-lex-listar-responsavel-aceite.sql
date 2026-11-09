-- =====================================================================================
-- 2026-11-09c-lex-listar-responsavel-aceite.sql  —  projeto solverone-app (Supabase)
-- admin_lex_listar passa a devolver três campos a mais. Só esta função muda; nenhuma tabela, nenhum dado.
-- Atende o pedido nº 1 da conversa do RootifyONE (rootify-one/entrega/solverone-app/PEDIDOS-LEXSUITEONE.md) e a
-- decisão de 09/Nov (documentacao/DECISAO-B2B-QUEM-FAZ-O-QUE-2026-11-09.md). PRÉ-REQUISITO: 2026-11-09b-sol-aceites.sql.
--
-- CAMPOS NOVOS (contrato para o RootifyONE):
--   email_responsavel  texto ou null. Faltava: a ficha abria vazia e salvar apagava o responsável.
--   boas_vindas        { ok: true|false, para: e-mail, em: data/hora } do último envio pela lex-equipe, ou null se nunca.
--   aceite             { aceito: true, versao, aceito_em, nome, email, protocolo } do último aceite dos termos da suíte
--                      (sol_aceites, termo 'lexsuiteone-termos'), ou { aceito: false }.
--   (ultima_vez já existia e continua: último uso de qualquer computador da licença.)
-- Permissões: as mesmas (só equipe logada; eh_admin_equipe() dentro da função).
-- APLICADO em 09/Nov/2026 pelo conector, com o "pode aplicar" do dono.
-- DESFAZER: reaplicar o bloco admin_lex_listar de 2026-11-08c-lex-modalidade.sql.
-- =====================================================================================
create or replace function public.admin_lex_listar()
returns jsonb language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_equipe() then raise exception 'Só dono ou admin da equipe' using errcode = '42501'; end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object(
      'codigo', c.codigo, 'escritorio', c.escritorio, 'doc_tipo', c.doc_tipo, 'documento', c.documento,
      'ativo', c.ativo, 'validade', c.validade, 'max_pessoas', c.max_pessoas, 'max_computadores', c.max_computadores,
      'mensagem', c.mensagem, 'criado_em', c.criado_em, 'dominios', c.dominios, 'email_boas_vindas', c.email_boas_vindas,
      'email_responsavel', c.email_responsavel,
      'boas_vindas', (select jsonb_build_object('ok', e.tipo = 'aviso_enviado', 'para', e.email, 'em', e.criado_em)
                        from public.lex_eventos e
                       where e.codigo = c.codigo and e.tipo in ('aviso_enviado', 'aviso_falhou') and e.detalhe like 'boas-vindas%'
                       order by e.criado_em desc limit 1),
      'aceite', coalesce((select jsonb_build_object('aceito', true, 'versao', a.versao, 'aceito_em', a.aceito_em, 'nome', a.nome, 'email', a.email,
                                                    'protocolo', 'ACE-' || pg_catalog.lpad(a.id::text, 6, '0') || '-' || pg_catalog.upper(pg_catalog.left(a.hash, 6)))
                            from public.sol_aceites a
                           where a.app = 'radar-judicial' and a.licenca = c.codigo and a.termo = 'lexsuiteone-termos'
                           order by a.aceito_em desc limit 1), jsonb_build_object('aceito', false)),
      'exigir_aprovacao', c.exigir_aprovacao, 'modalidade', c.modalidade, 'modalidade_desde', c.modalidade_desde,
      'dominios_pessoas', coalesce((select jsonb_agg(distinct pg_catalog.split_part(u.email, '@', 2)) from public.lex_usuarios u where u.codigo = c.codigo), '[]'::jsonb),
      'pessoas_ativas', (select count(*) from public.lex_pessoas p where p.codigo = c.codigo and p.ativa and p.aprovacao = 'aprovado'),
      'pessoas_total', (select count(*) from public.lex_usuarios u where u.codigo = c.codigo),
      'pessoas_aguardando', (select count(*) from public.lex_usuarios u where u.codigo = c.codigo and u.aprovacao = 'aguardando'),
      'computadores', (select count(*) from public.lex_computadores i where i.codigo = c.codigo and i.esquecida_em is null),
      'computadores_ativos', (select count(*) from public.lex_computadores i where i.codigo = c.codigo and i.ativo),
      'ultima_vez', (select max(i.ultima_vez) from public.lex_instalacoes i where i.codigo = c.codigo),
      'erros_7d', (select count(*) from public.lex_registros r where r.codigo = c.codigo and r.criado_em > pg_catalog.now() - interval '7 days'),
      'avisos_falhos', (select count(*) from public.lex_avisos a where a.codigo = c.codigo and a.estado = 'falhou')
    ) order by c.criado_em desc)
    from public.lex_contas c), '[]'::jsonb);
end $$;
revoke all on function public.admin_lex_listar() from public, anon;
grant execute on function public.admin_lex_listar() to authenticated;

-- Conferência (só leitura): tudo "true"
select
  (select prosrc like '%email_responsavel%' and prosrc like '%boas_vindas%' and prosrc like '%sol_aceites%'
     from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'admin_lex_listar') as listar_ok;
