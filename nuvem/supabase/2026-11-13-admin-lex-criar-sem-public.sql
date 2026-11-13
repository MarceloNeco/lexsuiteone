-- Correção de segurança (achado da Produto, 13/Nov, BAIXA): a versão de 6 argumentos de admin_lex_criar, criada em 12/Nov
-- (contas de teste), nasceu com EXECUTE para PUBLIC, padrão do Postgres ao criar função. Regra: admin_* nunca para anon ou PUBLIC.
-- A função já conferia a equipe por dentro (eh_admin_equipe), então não havia uso indevido possível, só a ACL fora do padrão.
-- Aplicado pela Arquitetura em 13/Nov como migração 'admin_lex_criar_sem_public' (correção do script já aprovado pelo dono).
revoke execute on function public.admin_lex_criar(text, date, integer, text, text[], boolean) from public, anon;
grant execute on function public.admin_lex_criar(text, date, integer, text, text[], boolean) to authenticated;

-- Conferência (deve dar false; conferido em 13/Nov: false nas 3 versões):
-- select (p.proacl::text like '{=X/%' or p.proacl::text like '%,=X/%') from pg_proc p where p.proname = 'admin_lex_criar';

-- DESFAZER (volta ao estado de 12/Nov; não recomendado):
-- grant execute on function public.admin_lex_criar(text, date, integer, text, text[], boolean) to public;
