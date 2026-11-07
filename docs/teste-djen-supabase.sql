-- LexSuiteONE · Teste de 5 minutos: o Supabase (projeto solverone-app, São Paulo) consegue falar com o DJEN?
--
-- Como usar (Marcelo):
--   1. Revisar este arquivo (regra C10: nada roda antes da revisão).
--   2. Supabase → projeto solverone-app → SQL Editor → colar o BLOCO 1 → Run.
--   3. Esperar uns 20 segundos e rodar o BLOCO 2. Copiar o resultado e me mandar.
--
-- O que ele faz: liga a extensão pg_net (chamadas HTTP feitas pelo próprio banco) e faz UM pedido de
-- leitura ao DJEN, pedindo 5 publicações do TRT2 de um dia. Não grava nada do escritório, não cria tabela.
-- Para desfazer tudo depois: drop extension pg_net;

-- ===== BLOCO 1 =====
create extension if not exists pg_net with schema extensions;

select net.http_get(
  url := 'https://comunicaapi.pje.jus.br/api/v1/comunicacao?siglaTribunal=TRT2&itensPorPagina=5&pagina=1'
         || '&dataDisponibilizacaoInicio=' || to_char(current_date - 1, 'YYYY-MM-DD')
         || '&dataDisponibilizacaoFim=' || to_char(current_date, 'YYYY-MM-DD'),
  headers := '{"Accept": "application/json", "User-Agent": "LexSuiteONE-Teste/0.4 (+https://solverone.com.br)"}'::jsonb,
  timeout_milliseconds := 20000
) as pedido_id;

-- ===== BLOCO 2 (uns 20 segundos depois) =====
select
  created,
  status_code,
  error_msg,
  left(content, 400) as inicio_da_resposta
from net._http_response
order by created desc
limit 1;

-- Como ler o resultado:
--   status_code 200 e o início da resposta parecendo JSON ({"status":"success","count":...})
--       → o Supabase em São Paulo pode ser o coletor. Sem servidor extra.
--   status_code 403 com "block access from your country"
--       → o CNJ trata o datacenter como "fora do Brasil"; o coletor fica no PC ou numa VM em São Paulo.
--   status_code 403 sem essa frase, ou 429
--       → proteção anti-robô / limite; também cai para PC ou VM.
--   error_msg preenchido (timeout etc.)
--       → repetir o BLOCO 1 uma vez; se persistir, mesmo caminho do 403.
