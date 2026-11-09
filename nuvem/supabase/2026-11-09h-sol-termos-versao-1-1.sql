-- 2026-11-09h-sol-termos-versao-1-1.sql — projeto solverone-app. Registro do que foi aplicado em 09/Nov/2026 (noite):
-- termos 1.1 aprovados pelo dono e pelo Leandro (documentacao/TERMOS-V1.1-PROPOSTA.html → paginas/aceite.html), página
-- publicada na main; a vigência passou de 1.0 para 1.1 nos dois termos da suíte, sem reaceite obrigatório (não havia aceite).
-- Feito por update direto (o botão "Publicar versão" do RootifyONE ainda não existe; desenho 5d), com registro no log.
update public.sol_termos set versao = '1.1', vigente_desde = now(), atualizado_em = now(), reaceite_obrigatorio = false,
       hash_texto = case when termo = 'lexsuiteone-termos' then 'a8d98a4dd3d11288f3355656872307d588a54a7f4625846211944116c7cbc596' else hash_texto end,
       link = case when termo = 'lexsuiteone-termos' then 'https://judicial.solverone.com.br/aceite.html' else 'https://judicial.solverone.com.br/aceite.html?ler=uso' end
 where suite = 'lexsuiteone' and versao = '1.0';
-- (lab_registrar_log('sol_termo_publicar', …) chamado na mesma transação, com o motivo.)
-- DESFAZER: update public.sol_termos set versao = '1.0' where suite = 'lexsuiteone';
