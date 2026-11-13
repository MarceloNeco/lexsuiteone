# LexSuiteONE · JUDICIAL

JUDICIAL é o produto; LexSuiteONE é a suíte jurídica da SolverONE. Endereço: judicial.solverone.com.br.
Frente atual: Radar Trabalhista. Próximas: Tributário, Cível e empresarial.

Robô que lê o Diário de Justiça Eletrônico Nacional (DJEN, do CNJ) e monta, todo dia, o catálogo de **processos novos
contra empresas** nos tribunais escolhidos (os 24 TRTs por padrão; TJs, TRFs, STJ e TST disponíveis), com a ficha
da empresa (cadastro público da Receita) e do processo. Roda no computador do escritório, **sem inteligência
artificial, sem senha de ninguém e sem servidor**. A lista vai para uma planilha na pasta do Google Drive do
escritório, com abas ocultas de log, saúde e controle para o suporte. Um produto [SolverONE](https://solverone.com.br).

**English:** a stdlib-only Python robot that reads Brazil's national electronic court gazette (DJEN) and builds a
daily catalog of new lawsuits against companies, enriched with the public company registry. No AI, no credentials,
no server: it runs on the law firm's own computer and writes to a spreadsheet in its Google Drive folder. Signed
updates (Ed25519) arrive through the shared folder or GitHub Releases.

## Pasta `robo/`

| Arquivo | Para quê |
|---|---|
| `INSTALAR-PYTHON.bat` | baixa o Python portátil oficial para dentro da pasta (só na primeira vez) |
| `ABRIR.bat` | abre a tela no navegador: configuração, tribunais, período, atualizar agora, lista e ficha |
| `RODAR.bat`, `AGENDAR.bat` | uma rodada sem tela; leitura automática no Agendador do Windows (horários da Configuração; padrão 20h e 8h) |
| `DIAGNOSTICO.bat` | relatório do que o robô guardou, sem dado de pessoa física, para calibrar a regra |
| `PREPARAR-PARA-CLIENTE.bat` | limpa os dados de teste antes de copiar a pasta para um cliente |
| `LEIA-ME.md`, `ROTEIRO-INSTALACAO.md`, `SEGURANCA.md`, `MANUTENCAO.md`, `ARQUITETURA.md`, `PENDENCIAS.md` | manuais |
| `lexsuite/` | o motor (Python 3.11+, só biblioteca padrão) |
| `testes/` | `python -m unittest discover -s testes` |
| `ferramentas/publicar.py` | gera o par de chaves e empacota uma versão assinada (ferramenta do suporte) |

## Princípios

1. O produto não usa IA; a manutenção pode usar qualquer agente de IA (leia `robo/MANUTENCAO.md`).
2. Nenhuma senha, chave de API ou certificado no código, no repositório ou em arquivo. A chave privada de assinatura
   nunca sai do computador do suporte.
3. Captcha nunca é burlado; pessoa física nunca sai do robô; poucos pedidos, com intervalo.
4. Nuvem portátil (Postgres padrão) e núcleo de código aberto (MIT). A camada de serviço (contas, cobrança, coletor
   central) fica fora deste repositório.

## Licença

MIT. Veja `LICENSE`.
