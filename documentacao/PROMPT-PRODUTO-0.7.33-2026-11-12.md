# Prompt para a conversa da Produto (colar inteiro) · 12/Nov/2026

Leia primeiro `docs/QUADRO.md` inteiro, depois `documentacao/DESENHO-CRITERIOS-CHAMADOS-CNPJ-2026-11-12.md` (Arquitetura, 12/Nov).

**1. O que está decidido (dono, 12/Nov, e Arquitetura).** Os três pedidos do dono do teste da 0.7.31 têm desenho pronto e vão na
0.7.33, nesta ordem: (a) CNPJ alfanumérico, seção 3 (módulo `lexsuite/documento.py`, extração com DV e máscara ou contexto,
consulta com falha suave); (b) critérios da lista e empresas excluídas por pessoa, no computador, por área, seção 1
(`criterios.json` ao lado do `config.json`, migração única das abas Preferências e Exclusões, planilha compartilhada
**completa** e sem as duas abas, aba só de leitura "Critérios desta leitura", seletor de área e "Copiar para as outras áreas");
(c) chamados pelo AssistONE, seção 2 (botão "Abrir um chamado", categorias fixas + Outros, prévia do que vai junto, trilha só
com ids de elementos, `POST /chamado` no servidor local, fila sem internet com `cliente_id`; anexo fica para a 0.7.34).

**2. O que a nuvem já oferece (Arquitetura, publicado em 12/Nov).** `lex-conta` v17, ação `chamado`: o servidor local manda
`{acao:"chamado", codigo, instalacao, versao, categoria, texto, tela, titulo_tela, funcao, trilha:[{quando, alvo}], idioma, fuso,
quando_cliente, windows, python, email, pode_responder, cliente_id}` e recebe `{ok:true, numero, id, repetido}` ou
`{ok:false, motivo}` com `codigo_invalido`, `codigo_desconhecido`, `desativado`, `dados_invalidos`, `limite` (HTTP 429, 5 por dia por
computador e 20 por licença) ou `erro`. Categorias aceitas: `erro`, `duvida`, `sugestao`, `licenca-e-acesso`, `planilha-e-pasta`,
`leitura-do-diario`, `outros`. A ação `chamado_anexo` (URL assinada de envio, PNG/JPEG/WebP até 5 MB, 2 por chamado, 2 horas) já
existe para a 0.7.34. Teste: código desconhecido devolve `codigo_desconhecido`.

**3. Definição de pronto (5 pontos) para os três**, PT e EN: manual e (?) ("Estes critérios são seus, neste computador";
"Abrir um chamado"; "CNPJ novo, dados da Receita indisponíveis"); AssistONE (ajuda, tour, busca: "critérios", "excluir empresa",
"por área", "chamado", "suporte", "CNPJ com letras"); Novidades formais e curtas, uma linha por mudança começando por substantivo;
termos **sem mudança** (o chamado só manda o que a pessoa vê e aprova); e-mail de boas-vindas **sem mudança**. Testes do CNPJ com
os números fictícios do simulador oficial da Receita e o exemplo do Serpro `12ABC34501DE35`.

**4. Ao terminar**, anote no quadro "pronta para publicar" com o commit e a lista do que foi conferido nos 5 pontos; a Operação
revisa e publica com o "publica a versão 0.7.33" do dono. Dúvida de desenho vai como pedido à Arquitetura no quadro, não ao dono.
