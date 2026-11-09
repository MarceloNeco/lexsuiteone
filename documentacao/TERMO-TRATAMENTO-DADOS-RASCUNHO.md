# Termo de tratamento de dados pessoais · RASCUNHO para revisão (Arquitetura, 09/Nov/2026)

**Rascunho técnico, não é parecer jurídico.** O dono e o Leandro (KR Law) revisam; um advogado valida antes de assinar.
Base: LGPD (Lei 13.709/2018), em especial art. 7º, 37, 39, 46 a 49. Referência de data: 09/Nov/2026. Escrito em
linguagem simples de propósito; a redação formal fica com o advogado.

## Partes

- **Controladora**: o escritório de advocacia (aqui, KR Law Advogados, CNPJ a preencher), que decide para que os dados
  servem e usa o RADAR JUDICIAL no seu computador.
- **Operadora**: SolverONE (razão social e CNPJ a preencher), que fornece o programa RADAR JUDICIAL (suíte LexSuiteONE)
  e guarda, em nome do escritório, os dados descritos abaixo.
- **Suboperador**: Supabase Inc., que hospeda o banco de dados da SolverONE na região de São Paulo (sa-east-1), e
  Resend Inc., que entrega os e-mails automáticos. Nenhum dado sai do Brasil pela SolverONE.

## 1. O que o RADAR faz e onde os dados ficam

1. O programa roda **no computador do escritório**. Lê o Diário de Justiça Eletrônico Nacional (dado público) e o
   cadastro público de empresas da Receita Federal, monta a lista de ações novas contra empresas e grava a lista no
   computador e na planilha do Google Drive **do escritório**. Esses dados não passam pela SolverONE.
2. A SolverONE **recebe e guarda**, em seu banco de dados, apenas: (a) os dados da licença do escritório (nome, CNPJ,
   código de cliente, validade, modalidade); (b) nome, e-mail profissional e função de cada pessoa do escritório que
   usa o programa, e a identificação aleatória de cada computador; (c) registros técnicos de erro, sem conteúdo de
   processos e sem caminhos pessoais do Windows; (d) **totais por situação** dos processos entregues, por dia, tribunal,
   frente e faixa de valor, **sem nome de empresa, número de processo, CNPJ ou qualquer pessoa**.
3. A SolverONE **não recebe**: a lista de ações, nomes de reclamantes ou de qualquer pessoa física citada nos processos,
   contatos de empresas ou de sócios, textos de publicações, anotações do escritório. Esses dados são tratados
   exclusivamente pelo escritório, no seu computador e no seu Drive, sob sua responsabilidade.

## 2. Finalidades

- Dados da licença e das pessoas (item 1.2 a e b): prestar o serviço, conferir a licença, dar suporte, avisar o
  responsável quando entra pessoa ou computador novo, cobrar.
- Registros técnicos (1.2 c): corrigir defeitos do programa.
- Totais por situação (1.2 d): medir o resultado do serviço e melhorar o produto. O escritório vê, na Configuração do
  programa, exatamente a tabela enviada.

## 3. Obrigações da SolverONE (operadora)

1. Tratar os dados só conforme este termo e as instruções documentadas do escritório (art. 39).
2. Segurança: acesso ao banco só por funções com permissão mínima, regras de linha (RLS), segredos fora do código,
   registro de acessos da equipe, revisão de segurança a cada versão que mexe no banco.
3. Confidencialidade da equipe da SolverONE; a equipe vê dados de licença, pessoas e totais, **nunca** o conteúdo
   das listas do escritório (que nem chega à SolverONE).
4. Retenção: registros técnicos por 90 dias; dados de pessoas enquanto a pessoa usar o programa e por até 12 meses
   depois; totais por situação sem limite (são estatísticas sem dado pessoal); dados da licença enquanto houver
   contrato e pelo prazo legal de guarda de documentos fiscais.
5. Ao fim do contrato: a pedido do escritório, exportar os dados de pessoas e da licença e, em até 30 dias, anonimizar
   as pessoas e encerrar a licença (os totais ficam, por não identificarem ninguém).
6. Incidente de segurança que afete dados do escritório: comunicar o responsável do escritório em até 48 horas do
   conhecimento, com o que aconteceu, o que foi afetado e o que foi feito (art. 48).
7. Suboperadores: só os nomeados acima; troca ou inclusão com aviso prévio de 30 dias.
8. Atender pedidos de titulares encaminhados pelo escritório (acesso, correção, exclusão) em até 15 dias.

## 4. Obrigações do escritório (controlador)

1. Responder pelo uso que faz da lista, dos contatos de empresas e sócios e das anotações, inclusive perante a OAB
   (Provimento 205/2021) e a LGPD, com a sua área de compliance.
2. Garantir que só advogados e pessoas autorizadas usem o programa, informar a SolverONE quando alguém sair (ou trocar
   a pessoa do computador), e guardar o código de cliente como dado de contrato.
3. Manter o computador e o Google Drive onde a lista fica com os cuidados usuais (senha, atualização, acesso restrito).
4. Encaminhar à SolverONE, quando precisar, os pedidos de titulares que digam respeito aos dados guardados por ela.
5. Aceitar o envio dos totais por situação (item 1.2 d) como parte do serviço, sabendo que não contêm dado pessoal.

## 5. Direitos dos titulares e canais

- Pessoas do escritório: acesso, correção e exclusão pelo próprio programa (perfil) ou pelo escritório; a SolverONE
  anonimiza a pedido.
- Canal da SolverONE: privacidade@solverone.com.br (encarregado a nomear). Canal do escritório: a definir pelo escritório.

## 6. Vigência, alteração e foro

Vale enquanto durar o uso do RADAR JUDICIAL. Alterações por escrito, com 30 dias de aviso. Foro: a definir (comarca
de a preencher). Este termo é anexo ao contrato de licença de uso; em conflito, prevalece o que protege mais o titular.

## Anexo A · Tabela do que vai à SolverONE a cada leitura (modelo)

| data | tribunal | frente | faixa de valor | situação | quantidade |
|---|---|---|---|---|---|
| 2026-11-20 | TRT2 | trabalhista | 100 a 300 mil | novo | 12 |
| 2026-11-20 | TRT2 | trabalhista | 100 a 300 mil | em contato | 3 |
| 2026-11-20 | TRT15 | trabalhista | acima de 1 milhão | virou cliente | 1 |

Situações: novo, visto, em análise, em contato, virou cliente, descartado, arquivado. Nenhuma outra coluna é enviada.

## O que falta preencher antes de assinar

Razões sociais e CNPJs das partes, encarregado (DPO) da SolverONE, canal do escritório, foro, prazo do contrato,
referência ao contrato de licença. Revisão do advogado sobre art. 7º (base legal do uso dos contatos pelo escritório) e
sobre o Provimento 205/2021 da OAB.
