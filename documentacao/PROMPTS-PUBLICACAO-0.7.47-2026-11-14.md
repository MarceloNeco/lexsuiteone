# Prompts para publicar a 0.7.47 e sincronizar as três conversas (Produto, 14/Nov/2026)

Ordem: 1) colar o prompt A na conversa **judicial operação**; 2) colar o prompt B na conversa **judicial arquitetura**;
3) a Arquitetura devolve um prompt de sincronização: colar na **judicial produto** e na **judicial operação**.
Os dois primeiros podem ir ao mesmo tempo: um não depende do outro (conferido no código da `lex-conta`: os campos novos são
ignorados sem erro enquanto a v20 não estiver no ar).

## Prompt A — judicial operação

```
publica a versão 0.7.47

Contexto (Produto, 14/Nov): só existe a 0.7.47 para publicar. Ela já contém a 0.7.46 (Área logada v2) e a main está em 0.7.47;
quem atualizar da 0.7.45 vê as Novidades das duas. Não publique a 0.7.46 à parte.

Passo a passo:
1. git pull e leia docs/QUADRO.md (linha "0.7.47 pronta para publicar" na seção Produto e o pedido "Produto → Operação" de 14/Nov).
2. Traga os instaladores novos, que ficaram fora da main de propósito (o site os serve na hora):
   git fetch origin claude/lexsuiteone-judicial-product-22f871
   git cherry-pick 849904a
   (instalador/INSTALAR.bat, INSTALAR-COMPLETO.bat, os dois zips de docs/downloads e robo/testes/test_v0747_instalador.py).
   Depois: python ferramentas/marca.py e python ferramentas/marca.py --conferir; se algo mudou, envie junto.
3. Rode tudo antes de publicar: cd robo && python -m unittest discover -s testes, e bash robo/testes/tela/rodar_tudo.sh
   (tem que terminar com TUDO OK).
4. Revise como de costume (revisor, DoD de 5 pontos). Lembretes: termos sem mudança; e-mail de boas-vindas e site já
   atualizados (link da página de antivírus, "Extrair tudo"); os .bat não rodaram num Windows de verdade.
5. Envie para a main e dispare "Publicar versão assinada" (publicar.yml). Confira versao.json = 0.7.47, assinatura e
   hash, os pacotes e o instalador novo no site (Instalar-LexSuiteONE.zip e o completo).
6. Anote no quadro: 0.7.46 e 0.7.47 publicadas juntas, a tag, e marque o pedido Produto → Operação como feito.
```

## Prompt B — judicial arquitetura

```
Pode aplicar a parte de nuvem da 0.7.47 (CNJ fora e antivírus). A Operação está publicando a 0.7.47 agora.

1. Nuvem da 0.7.47 (desenho documentacao/DESENHO-LEITURA-E-ANTIVIRUS-2026-11-14.md; decisões 34 a 39): lex-conta v20 com
   a ação estado_cnj (hoje uma ação desconhecida cai em "verificar" e gasta o limite de 6 por minuto da instalação: trate
   explicitamente), os campos antivirus, antivirus_ligado e sinal no registro, avisar_cnj na verificar; SQL de lex_registros
   e lex_instalacoes; na lex-saude, o alerta à SolverONE, o e-mail a quem marcou o aviso (queda de mais de 4 h em dia útil,
   um na queda e um na volta) e a sonda da consulta. O formato que o programa já espera está no pedido "Produto → Arquitetura"
   de 14/Nov no quadro (antivirus_ligado "sim"/"não"; estado_cnj {ok: n, fora: [..] ou n, desde: "HH:MM"}).
   Arquivo datado em nuvem/supabase/ com o desfazer, anotação no quadro.
2. Confira dois pontos da Produto no quadro: (a) desvio de desenho: a leitura automática é criada sempre pelo XML gravado em
   C:\LexSuiteONE\tarefa.xml (a tarefa simples /sc daily não roda na bateria nem compensa horário perdido); (b) o desenho curto
   da limpeza automática (decisões 40 a 42: resumir com 6 meses, apagar com 24, trabalhados nunca saem, prazos em
   Armazenamento, estatísticas sempre guardadas) e o filtro de cidade (0.7.48).
3. Perguntas abertas 21 a 28 do quadro. Eu já respondi isso em interações anteriores com você (visita à KR Law, prompts e
   resultados): procure as respostas no histórico, nos resultados da visita (visita-kr-law/resultados/) e nos documentos de
   desenho, registre em "Decisões do dono" e marque "respondida". Só me traga o que de fato ninguém respondeu. São elas:
   - 21. PJe: o Leandro autoriza a extensão Claude in Chrome a ler os próprios autos no PJe, até 30 processos por dia, só
     leitura, com o prompt v2 (nunca abrir login.seam, expedientes nem "Baixar processo completo")? (A área logada v2 da
     0.7.46/0.7.47 já foi construída assim, com o limite por pedido.)
   - 22. PJe: precisa de processos de terceiros (onde a KR Law não atua), sabendo do risco de bloqueio por excesso de acesso?
     A recomendação era: não no início, só os próprios autos.
   - 23. Astrea: o Leandro aceita receber as empresas escolhidas como contato PJ com a etiqueta JUDICIAL, digitadas pela
     extensão na sessão dele, ou prefere uma planilha para a equipe digitar? Recomendação: planilha primeiro.
   - 24. Astrea: ele exporta os contatos de tempos em tempos para o RADAR marcar os clientes (só CNPJ) como empresas
     excluídas? Recomendação: mensal, o RADAR lendo só a coluna CNPJ.
   - 25. Aurum (dona do Astrea): o Leandro pergunta, como cliente, se existe API ou importação de contatos e o que os termos
     dizem sobre automação na tela? Recomendação: sim, antes de qualquer automação no Astrea.
   - 26. Ordem das integrações da visita: primeiro A (PJe → RADAR, já feito na 0.7.46/0.7.47) e C (clientes do Astrea
     como excluídas), depois B (planilha no formato do Astrea)?
   - 27. Prints da visita: ficam só na minha pasta restrita, fora do repositório; os do PJe (CPF e endereço de pessoas) são
     apagados depois do desenho, e os do Astrea guardados com acesso restrito?
   - 28. A petição inicial do PJe pode ser fonte do endereço da empresa ré, marcada "a conferir", com o cadastro da parte
     tendo prioridade? (Já está assim no programa desde a 0.7.45.)
4. Ao terminar, me devolva UM prompt de sincronização, que eu colo na judicial produto e na judicial operação, dizendo: o que
   foi aplicado na nuvem, as decisões registradas (21 a 28 e o que mais mudou), o que cada sessão faz agora e o que ainda
   depende de mim. As listas antigas de "Preciso do dono" de cada seção do quadro devem ser revistas e limpas por quem é
   dono da seção.
```
