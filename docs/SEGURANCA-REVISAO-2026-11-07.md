# Revisão de segurança e privacidade — LexSuiteONE robô v0.7.1 (07/Nov/2026)

Revisão feita com a skill `seguranca-lgpd-gdpr` (varredura de segredos e dados pessoais, Bandit, Gitleaks na CI,
checklist OWASP/ASVS, checklist de robôs de dados públicos, triagem LGPD). Triagem técnica, não parecer jurídico.

## 1. Resumo executivo

Nota geral: **Baixo** depois das correções desta revisão (era **Médio** antes delas). O robô não guarda segredos,
não tem login nem servidor na internet, fala só HTTPS, valida tudo o que baixa e assina as atualizações. Os riscos
que restam são de operação (quem tem o computador controla o robô) e de uso dos dados (decisão do escritório).
As três ações mais urgentes, todas feitas nesta revisão: (1) impedir injeção de fórmula no CSV exportado;
(2) recusar pedidos à tela com cabeçalho Host estranho (DNS rebinding); (3) retenção automática e opção de não
mostrar nomes de sócios.

## 2. Achados (ordenados por severidade)

| ID | Severidade | Onde | O que é | Correção | Referência |
|---|---|---|---|---|---|
| S1 | Médio → corrigido | `lexsuite/saidas.py`, `radar_modelo.html` (exportar) | Nome de empresa vindo do Diário começando com `=`, `+`, `-` ou `@` viraria fórmula ao abrir o CSV no Excel (injeção de fórmula CSV) | células com esses inícios recebem um apóstrofo; o `.xlsx` já usava texto puro | OWASP CSV Injection |
| S2 | Médio → corrigido | `lexsuite/app.py` | A tela aceitava qualquer `Host`; um site malicioso com DNS rebinding poderia ler `/dados` (POST já era bloqueado pelo cabeçalho da página) | só `127.0.0.1` e `localhost` na porta do robô; o resto recebe 403 | OWASP A01/A05 |
| S3 | Médio → corrigido | `lexsuite/rede.py`, `lexsuite/djen.py` | Download sem teto e caderno descompactado sem limite (zip bomb de uma fonte comprometida) | teto de 2 GB no download, lido em pedaços; limite de descompressão do caderno | CWE-400, CWE-409 |
| S4 | Médio → corrigido (dia 07) | `lexsuite/rede.py`, `lexsuite/avisar.py` | `urlopen` aceitava qualquer esquema | só `https://`; URLs do Telegram fixas | Bandit B310 |
| S5 | Médio → corrigido (dia 07) | `lexsuite/planilha.py` | XML da planilha sem bloqueio de DTD | planilha com `<!DOCTYPE` ou `<!ENTITY` é recusada; limite de 50 MB | Bandit B314, XXE |
| P1 | Médio → corrigido | `lexsuite/banco.py`, `lexsuite/radar.py` | Texto curto das publicações (com nomes de reclamantes) acumulava sem prazo | retenção automática: 365 dias (`radar.guardar_dias`), apagando ações, publicações e execuções antigas | LGPD art. 6º III e art. 15 |
| P2 | Médio → corrigido | `lexsuite/preferencias.py`, `lexsuite/radar.py` | Nomes de sócios e administradores (pessoas) sempre exibidos | ajuste "Mostrar sócios e administradores" na aba Preferências; desligado, não vão para a tela nem para a planilha | LGPD art. 6º III (necessidade) |
| P3 | Baixo → corrigido | `radar_modelo.html` | Fonte carregada do Google Fonts: um pedido externo por abertura da tela | removida; a tela não faz nenhum pedido externo | minimização |
| I1 | Info | `.gitignore` | `.env` não listado (não há `.env` no projeto) | adicionado | boas práticas |
| I2 | Info | tela local | Não há autenticação na tela: qualquer programa ou usuário do mesmo computador pode usá-la | aceito: computador de uso individual; documentado em `SEGURANCA.md` | ASVS V2 |
| I3 | Info | aba Controle | "Desligar pelo suporte" é cortesia, não trava | documentado no manual do escritório e no `LEIA-ME.md` | transparência |

Varreduras: `scan_secrets.py` sem segredos; `scan_pii.py` só com CNPJs, telefones e CPFs **fictícios** em exemplos e
testes (os dados reais ficam em `saida/` e `lexsuite.db`, fora do repositório); `bandit -ll` sem achados médios ou
altos; Gitleaks verde na automação do GitHub.

## 3. Mapa de dados pessoais

| Dado | Pessoal? | Sensível? | Finalidade | Base legal provável | Onde fica | Por quanto tempo | Quem acessa | Quem recebe |
|---|---|---|---|---|---|---|---|---|
| Nome de reclamante no trecho da publicação | sim | pode conter saúde (acidente, doença) | separar ação contra empresa e classificar assunto | dado manifestamente público (art. 7º §§3º-4º), com finalidade compatível (triagem) | `lexsuite.db` (trecho de 600 caracteres), só no computador do escritório | 365 dias | o computador do escritório | ninguém: nunca sai para a planilha, a tela ou o diagnóstico (mascarado) |
| Razão social, CNPJ, endereço, telefone e e-mail da empresa | dado de pessoa jurídica | não | ficha da empresa | cadastro público (Receita); uso comercial é decisão do controlador | `lexsuite.db` e planilha no Drive do escritório | 365 dias no banco; planilha é do escritório | escritório e suporte (planilha) | suporte, por compartilhamento do escritório |
| Nome e qualificação de sócios e administradores | sim | não | saber com quem falar | legítimo interesse (art. 7º IX), com teste de balanceamento a cargo do escritório | idem | idem | idem | idem; pode ser desligado na aba Preferências |
| Nome de advogado nas publicações | sim | não | não é usado pelo radar | não coletado para a lista | só no trecho de 600 caracteres | 365 dias | computador do escritório | ninguém |
| Registro de rodadas (contagens, versão, computador, erro) | não (nome do computador pode identificar) | não | suporte e auditoria do serviço | execução de contrato | aba Log/Sobre da planilha | enquanto a planilha existir | escritório e suporte | suporte |

Teste de minimização: a lista funciona sem nome de pessoa física (já é assim); sem sócios (ajuste); e o trecho de
600 caracteres poderia ser reduzido a rótulos (assunto, rito) numa versão futura, o que eliminaria o único dado
sensível possível do banco. Registrado em `PENDENCIAS.md`.

## 4. Lacunas de privacidade (do escritório, como controlador)

- Registro das operações de tratamento (art. 37) e, se o uso comercial dos contatos for adotado, teste de legítimo
  interesse documentado e, de preferência, RIPD (art. 38). O manual do escritório diz isso em linguagem simples.
- Canal do titular e encarregado: são do escritório; a SolverONE atua como prestador e não acessa o computador.
- Política de privacidade da SolverONE para a trilha SaaS (não se aplica ao robô local).
- Transferência internacional: nenhuma; os dados ficam no computador e no Google Drive do escritório (a localização
  do Drive é uma escolha do escritório com o Google).

## 5. Plano de correção

- **Hoje (feito):** S1, S2, S3, P1, P2, P3, I1, mais S4 e S5 do dia 07. Testes novos cobrem CSV, Host, retenção e sócios.
- **Esta semana:** no GitHub, ligar proteção do ramo `main` (PR obrigatório, checks obrigatórios), Dependabot alerts
  (sem dependências, serve para as ações da CI) e 2FA na conta; fixar as ações da CI por SHA.
- **Este mês:** reduzir o trecho guardado a rótulos; pre-commit com gitleaks e bandit; plano de incidente de uma página
  (quem revoga a chave de assinatura, como publicar versão de correção, como avisar os escritórios).

## 6. O que não foi verificado e por quê

- Comportamento no Windows real (schtasks, Drive para computador, Excel abrindo o `.xlsx`): só testado em Linux e
  com leitor próprio e openpyxl; o ensaio em casa é o teste de verdade.
- Cabeçalhos HTTP de domínio: não há site publicado ainda (`lexsuiteone.solverone.com.br` não existe).
- `pip-audit`/`trivy`: sem dependências externas no robô; não se aplicam.
- Conformidade do uso comercial dos contatos: decisão jurídica do escritório, fora desta revisão.
