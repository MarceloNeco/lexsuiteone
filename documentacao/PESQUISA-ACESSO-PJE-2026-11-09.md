# Pesquisa: dados não públicos do processo com o login do advogado (09/Nov/2026)

Pedido do dono no item 59 de `FEEDBACK-TESTE-2026-11-09.md`. A pesquisa foi feita na web e marca o que é fato e o que é
inferência. Nada aqui é parecer jurídico.

## Em uma frase

Não existe hoje um caminho oficial e simples para um programa de terceiros puxar, com a credencial do advogado, o valor
da causa, as partes, o endereço e a petição inicial. E o **contato (telefone, e-mail) da empresa quase nunca está no
processo**: ele vem do cadastro público do CNPJ, que o RADAR já consulta.

## O que existe (fato, com fonte)

- **MNI** (Modelo Nacional de Interoperabilidade, Res. Conjunta 3/2013, versão 2.2.2): padrão de troca entre sistemas,
  usado pelo Escritório Digital. Não confirmado se aceita advogado não habilitado no processo; varia por tribunal.
  https://www.cnj.jus.br/integracao-para-os-tribunais/
- **PDPJ-Br** (Res. 335/2020; Res. 574/2024): terceiros só com credenciamento "quando houver interesse
  institucional"; o CNJ pode limitar ou bloquear uso abusivo. https://atos.cnj.jus.br/atos/detalhar/5792
- **DataJud API pública**: só metadados (número, tribunal, órgão, data de ajuizamento, sigilo). Os termos proíbem
  coletar dados pessoais de terceiros. https://www.cnj.jus.br/sistemas/datajud/api-publica/
- **Advogado sem procuração**: o Estatuto da OAB (art. 7º, XIII) permite examinar autos não sigilosos; no PJe o acesso
  de quem não está no processo é limitado e varia (Res. CNJ 121/2010; o CNJ manteve os limites em 2022).
  https://www.conjur.com.br/2022-set-25/cnj-mantem-limites-acesso-pje-resguardar-dados/
- **Bloqueio por volume**: o TRT6 anuncia bloqueio do usuário do PJe-JT que abrir mais de 1.500 processos de terceiros
  em 30 dias. https://www.trt6.jus.br/portal/node/1169550
- **Petição inicial trabalhista** (CLT art. 840 §1º): qualificação das partes, fatos, pedidos com valor. Na prática:
  razão social, CNPJ e endereço da ré; telefone e e-mail da ré são raros (inferência). O valor da causa costuma
  estar na petição.
- **OAB, Provimento 205/2021**: veda captação de clientela e mala direta a destinatário indeterminado. A abordagem
  ativa a uma empresa que não pediu contato é ponto sensível, mesmo para defendê-la (pedir parecer).

## Não confirmado (testar com o advogado da KR Law)

- No PJe do TRT15, logado, o advogado que não está no processo vê a petição inicial e o valor da causa de uma ação
  recém-distribuída (antes da citação)?
- Como Astrea, Jusbrasil, Escavador, Judit e outros obtêm esses dados (não há fonte pública confiável).

## Recomendação

**Para quinta (reunião com o cliente):**
1. RADAR como está: lista do Diário + cadastro do CNPJ (endereço, telefone e e-mail cadastrais).
2. O advogado testa, logado no TRT15, **poucos** processos (algumas dezenas) e anota o que aparece.
3. Claude in Chrome só como piloto supervisionado, com volume baixo e o consentimento do escritório.
4. Perguntar ao escritório sobre o Provimento 205 (como abordam a empresa).

**Para depois:** consultar o TRT15 e o CSJT sobre credenciamento (PDPJ-Br ou MNI); avaliar um fornecedor licenciado
de dados processuais (API paga) em vez de automação no navegador; parecer sobre LGPD e Provimento 205.

## Consequência para o produto

- O selo de contato (item 52) deve usar sobretudo o cadastro do CNPJ; "área logada" serve para valor da causa,
  endereço e petição, não para telefone e e-mail.
- O fluxo de arquivo para o Claude in Chrome (itens 41 e 59) precisa de limite de volume por dia, avisar do risco de
  bloqueio e ficar claro que quem abre é o advogado, com a credencial dele.
