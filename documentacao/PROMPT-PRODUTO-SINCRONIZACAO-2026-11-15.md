# Prompt para a conversa da Produto (colar inteiro) · sincronização completa · 15/Nov/2026

```
Sincronização da Arquitetura (15/Nov). O dono reclamou, com razão, que esta conversa esquece decisões (Astrea, limpeza, protótipo) e
repete perguntas já respondidas. A partir de agora existe UMA página de estado que você mantém e lê sempre:
documentacao/ESTADO-ATUAL-RADAR.md. Antes de tudo: git pull; leia essa página inteira, depois docs/QUADRO.md (Decisões do dono de
14 e 15/Nov; Pedidos Arquitetura → Produto de 14 e 15/Nov).

O QUE MUDOU DESDE A ÚLTIMA SINCRONIZAÇÃO:
1. Perguntas 23, 24 e 25 (Astrea/Aurum) estão FECHADAS: Astrea adiado até o escritório pedir; o dono NÃO vai procurar a Aurum agora
   ("ainda não estou maduro; estou explorando"). Nunca mais listar isso como pendência dele. Dossiê completo (navegação de 13/Nov, site
   mcp.ai, termos do Astrea, caminhos P1 a P5): documentacao/DOSSIE-ASTREA-MCP-AI-2026-11-15.md.
2. Comparação DJEN × PJe feita (documentacao/COMPARACAO-DJEN-X-PJE-2026-11-15.md): o PJe acrescenta CNPJ, valor da causa, data de
   distribuição, endereço e às vezes e-mail da ré; telefone não vem de nenhum. Dúvida aberta: a visita foi num processo do próprio
   escritório; a consulta de terceiros pode mostrar menos. Teste de 5 min com advogado logado:
   documentacao/visita-kr-law/PROMPT-TESTE-GAP-PJE-2026-11-15.md (o dono decide quando).
3. PLANO GUARDADO, SEM DATA (não entra na 0.7.48): varredura pela área logada (PJe e Astrea) dos processos recentes sem contato ou valor
   no Diário, com o RADAR escolhendo sozinho os processos e montando os lotes: documentacao/PLANO-VARREDURA-AREA-LOGADA-SEM-DATA.md.
   Anote na PENDENCIAS como "planejado, sem data" e nada mais.
4. Protótipo da 0.7.48 pronto (feito pela Arquitetura): documentacao/prototipos/0.7.48/prototipo.html, 4 abas: Configurações →
   Armazenamento (prazos 6 e 24 meses, última limpeza, "Limpar agora"), Lista com filtro de cidade (busca, contagem, "Sem cidade"),
   as 4 cenas de quando o CNJ cai e a leitura pela consulta, e o Histórico com a linha "Limpeza". O dono vai olhar DEPOIS de testar a
   0.7.47 e ANTES de mandar codar; a 0.7.48 só começa com o "pode codar a 0.7.48" dele. Se ele pedir ajuste no protótipo, o ajuste é
   da Arquitetura (pedido no quadro); a implementação é sua, seguindo o protótipo e o desenho da limpeza
   (documentacao/DESENHO-LIMPEZA-AUTOMATICA-2026-11-14.md: termos não mudam, manual muda).
5. Nuvem da 0.7.47 aplicada e testada (lex-conta v20, lex-saude v3); recursos por licença aplicados (KR Law desligada).

O QUE VOCÊ FAZ AGORA:
a. Assume documentacao/ESTADO-ATUAL-RADAR.md: atualize a cada entrega e decisão; quando o dono perguntar "o que falta" ou "o que eu
   tenho que testar", responda a partir dessa página, curta, sem inventar pendência que não esteja lá. TESTES-DO-DONO.md vira só a
   seção 5 dessa página (ou aponta para ela), sem a pergunta ao Leandro.
b. Não começa a 0.7.48 antes do "pode codar" do dono. Enquanto espera, só o que não muda o programa: preparar o plano de testes da
   0.7.48 a partir do protótipo e revisar manual/AssistONE/Novidades que vão mudar.
c. Termine esta sincronização mostrando ao dono, em até 10 linhas, a seção 5 da página de estado (testes pendentes da 0.7.47) e a
   frase: "quando terminar, diga 'pode codar a 0.7.48'".
```
