# O que o dono precisa testar (lista única, atualizada pela Produto)

Última revisão: 14/Nov/2026. Tudo aqui foi conferido no repositório; onde algo não pôde ser conferido, está escrito.
Quando terminar um item, marque `[x]` ou avise a Produto, que marca.

## 0. Onde as versões estão hoje

| Versão | Situação |
|---|---|
| 0.7.47 (CNJ fora e antivírus, com a 0.7.46 Área logada v2 dentro) | **Publicada** em 14/Nov (tag v0.7.47), com o instalador novo no site |
| Nuvem da 0.7.47 (`lex-conta` v20, alerta e e-mail do CNJ) | **Aplicada** pela Arquitetura em 14/Nov |

## 1. Ligar e desligar a área logada por escritório

**Onde se liga** (RootifyONE 0.18.31 em diante, conferido no código `rootify-lex.js`):

1. Abra o **RootifyONE** → **LexSuiteONE** → aba **Licenças**.
2. Abra a ficha da licença (por exemplo, a de teste ou a da KR Law).
3. Desça até o bloco **"🎚 Recursos desta licença"**. Na linha **Área logada** escolha uma das três opções:
   - **segue o global**: vale o interruptor do Controle dos apps (para todos os escritórios);
   - **ligado nesta licença**;
   - **desligado nesta licença**.
4. Se quiser, escreva o motivo ("Por que muda", fica no histórico) e clique em **"💾 Salvar recursos desta licença"** → confirme.
5. A ficha passa a mostrar a etiqueta "exceção", e o histórico da licença registra a mudança.

**Como estava em 14/Nov** (quadro, registro da Arquitetura): KR Law = **desligado**; licença de teste = **ligado**.

**Quando o programa percebe a mudança**:
- Ao abrir o programa, antes de cada leitura, de 30 em 30 minutos com a tela aberta e ao voltar para a janela (0.7.47).

**O que você deve ver no programa**:
- [ ] **Desligado:** somem o botão "Trazer dados da área logada…" da barra que aparece ao marcar processos, o grupo "Área logada"
      do menu ☰ e o botão no cartão do processo (e o filtro, o selo e a faixa da área logada). A partir da 0.7.46.
- [ ] **Ligado:** os três voltam.
- [ ] A partir da 0.7.47: Configurações → Sobre este computador → **Recursos da licença** mostra "Trazer dados da área logada:
      ligado" ou "desligado pela licença".

## 2. Roteiros de cada versão

Cada um tem os passos e o que deve aparecer. Faça depois da publicação daquela versão.

- [ ] `documentacao/ROTEIRO-TESTE-0.7.45.md`: leitura feita pela tela aberta quando o Windows não roda a hora marcada.
      **Falta testar num Windows com o Bitdefender** (anotado na PENDENCIAS desde a 0.7.44).
- [ ] `documentacao/ROTEIRO-TESTE-0.7.46.md`: Área logada v2 (pedido em 4 passos, pedido pendente, resposta colada ou em arquivo,
      relatório do que mudou, filtro e selo).
- [ ] `documentacao/ROTEIRO-TESTE-0.7.47.md`: instalador novo (abrir de dentro do .zip, antivírus encontrado, leitura automática
      criada no passo "5 de 6"), Sobre este computador, aviso por e-mail do CNJ. **Os instaladores não rodaram num Windows de
      verdade**: os passos 1 e 2 desse roteiro são os mais importantes.

Roteiros mais antigos (0.7.36 a 0.7.44) também estão em `documentacao/`. Não há registro no repositório de quais você já fez; se
algum ficou para trás, diga qual e a Produto confere o que ainda vale.

## 3. Coisas que dependem de você (não são teste)

- [ ] Entregar ao Leandro as perguntas 23 a 25 (Astrea e Aurum; texto completo no quadro) e o prompt v2 do PJe.
- [ ] Criar o repositório `central-lexsuiteone` no GitHub (Central LexSuiteONE; nenhuma sessão pode criar repositório).
- [ ] Os itens da Arquitetura que pedem você (painel do Supabase, RootifyONE, staging depois da KR Law): lista na seção
      Arquitetura → "Preciso do dono" do quadro.

## 4. Licença de teste

O código da licença de teste não fica escrito em lugar nenhum (regra do projeto). Para ver: RootifyONE → LexSuiteONE → Licenças
→ ficha da licença de teste; ou o e-mail de boas-vindas que chegou no seu e-mail.

## 5. Planejado (ainda não feito)

- 0.7.48: filtro de cidade na Lista e no Painel, ao lado de Estado (escolher o estado limita as cidades; não vale na
  planilha); leitura pela consulta quando o caderno do CNJ cai.
- Limpeza automática (suas decisões 40 a 42, de 14/Nov): com 6 meses sai o texto pesado; com 24 meses o processo sai do
  programa e fica só nas estatísticas; os trabalhados nunca saem; prazos ajustáveis em Configurações → Armazenamento, com a
  última limpeza à vista. Desenho da Arquitetura pronto (`documentacao/DESENHO-LIMPEZA-AUTOMATICA-2026-11-14.md`); entra na 0.7.48.
