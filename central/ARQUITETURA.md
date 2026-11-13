# Central LexSuiteONE: arquitetura (0.1.0, 13/Nov/2026)

Painel da equipe SolverONE para os softwares jurídicos da LexSuiteONE, começando pelo RADAR JUDICIAL. Desenho e decisões:
`lexsuiteone/documentacao/DESENHO-CENTRAL-LEXSUITEONE-2026-11-13.md` e as perguntas 30 a 33 do quadro (respondidas em 13/Nov).

**Provisório:** esta pasta mora no repositório `lexsuiteone` até o repositório próprio existir (decisão do dono: repositório
novo, endereço próprio). Ela não é publicada: o GitHub Pages do `lexsuiteone` serve só `docs/`.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `index.html` | a casca: entrada (senha, código do celular) e o aplicativo; CSP só com o próprio site e o Supabase |
| `central.js` | toda a lógica: Supabase por REST (sem biblioteca), MFA TOTP, sessão na aba, telas, PT/EN |
| `central-config.js` | **o único arquivo por ambiente**: endereço do Supabase e a chave pública (publishable), versão, atalho do RootifyONE |
| `central.css` | aparência (claro e escuro), a mesma paleta do RADAR |
| `manifest.json`, `icone.svg`, `sw.js` | aplicativo instalável (PWA); o `sw.js` guarda só o código, nunca dado; cache `central-lexsuiteone-*` |
| `versoes.json` | o que cada versão trouxe (PT/EN) |

## Segurança

- Entrada: Supabase Auth com senha **e** código do aplicativo autenticador (MFA TOTP, sessão `aal2`). Sem login com Google
  (diretriz: administração não tem login social). Primeira vez: o aplicativo mostra o QR do Supabase para cadastrar o código.
- Depois do código, `eh_equipe()`: conta fora da tabela `equipe` sai na hora.
- Sessão só nesta aba (`sessionStorage`): recarregar não pede de novo; fechar a aba, "Sair" ou 15 minutos parado encerram
  (logout `scope=local`).
- Dados só por funções `admin_*` do banco, que conferem a equipe. As novas da Central (`admin_lex_central`) devem conferir
  também `aal2` (pedido à Arquitetura). Nenhum pedido externo além do Supabase; nada de script, fonte ou imagem de fora.

## Dados

- **Licenças:** `admin_lex_listar()` (já existe).
- **Visão geral, Saúde dos Diários, Escritórios e computadores, Erros, Estatísticas:** `admin_lex_central()` (a criar pela
  Arquitetura, fase 1). Formato combinado (jsonb, cada parte opcional): `diarios` [{trib, est ("ok"|"lento"|"fora"), ms,
  hoje, hora}], `hist24` [n], `instalacoes` [{esc, pc, ver, dias, hora}], `erros` [{q, o, e, m, v}], `dias30` [n],
  `por_trib` [[trib, n]], `por_sit` [[situação, n]]. Enquanto a função não existir, a aba mostra a demonstração com a faixa
  amarela "Demonstração".
- **Leituras dos escritórios:** fase 2 (pergunta 33: "sim, depois da fase 1"), com versão nova do RADAR e termos revisados.
