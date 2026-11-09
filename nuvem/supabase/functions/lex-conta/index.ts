// LexSuiteONE · RADAR JUDICIAL · lex-conta v8 (v7 + ação 'aceite': a página pública de termos grava por aqui, com e-mail de confirmação): confere a licença (código de cliente), registra quem usa cada computador,
// avisa quando entra pessoa ou computador novo e recebe erros técnicos. Desenhos: documentacao/DESENHO-LICENCA-EM-USO.md
// e documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md (etapa 0 de segurança).
//
// Chamada pelo programa instalado e pelo instalador, sem chave nenhuma (verify_jwt = false, DE PROPÓSITO: o programa não
// tem segredo). O que protege: validar tudo, limitar chamadas (lex_contar_chamada), devolver o mínimo e nunca confirmar
// se um e-mail existe em outra licença. A chave de serviço e a chave do Resend existem só nos Secrets do Supabase.
//
// Modelo: a licença é do escritório (código); o computador é a instalação (id aleatório guardado pelo programa fora da
// pasta dele, para reinstalar reaproveitar); a pessoa é o e-mail ligado ao computador agora. E-mail do domínio do
// escritório é aprovado na hora; de fora (Gmail etc.) fica "aguardando" a equipe, sem bloquear (a não ser que a
// licença tenha exigir_aprovacao). Limite: HTTP 429 → o programa trata como "sem resposta" e segue com a última boa.
import { createClient } from "jsr:@supabase/supabase-js@2";

const CODIGO = /^LEX-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/;
const INSTALACAO = /^[0-9a-f]{16}$/;
const EMAIL = /^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$/;
// Provedores públicos: nunca viram "domínio do escritório".
const PUBLICOS = new Set(["gmail.com", "googlemail.com", "outlook.com", "outlook.com.br", "hotmail.com", "hotmail.com.br", "live.com",
  "msn.com", "yahoo.com", "yahoo.com.br", "ymail.com", "icloud.com", "me.com", "aol.com", "uol.com.br", "bol.com.br", "terra.com.br",
  "globo.com", "ig.com.br", "zipmail.com.br", "proton.me", "protonmail.com", "pm.me", "tutanota.com", "gmx.com", "mail.com"]);
const CONTATO = "judicial@solverone.com.br";
const LINK_ACEITE = "https://judicial.solverone.com.br/aceite.html";
const REMETENTE = "SolverONE <nao-responda@solverone.com.br>";
const AVISOS_POR_DIA = 20;
// Retorno dos processos à SolverONE (decisão do dono, 09/Nov): só contagens por situação. Situações do programa:
const SITUACOES = new Set(["novo", "visto", "em_analise", "em_contato", "virou_cliente", "descartado", "arquivado"]);

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });
}
const texto = (v: unknown, max: number) => String(v ?? "").trim().slice(0, max);
const dominioDe = (email: string) => email.split("@")[1] ?? "";
// Tira do texto de erro a pasta do usuário do Windows (traz o nome da pessoa) e e-mails.
function semDadoPessoal(t: string) {
  return t.replace(/([a-z]:[\\/]+users[\\/]+)[^\\/"'\s]+/gi, "$1~").replace(/[^\s@"']+@[^\s@"']+\.[^\s@"']+/g, "[e-mail]");
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ ok: false, motivo: "metodo" }, 405);
  let e: Record<string, unknown>;
  try { e = await req.json(); } catch { return json({ ok: false, motivo: "dados_invalidos" }, 400); }
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

  // Limite por chave: true = pode seguir. Se o contador falhar (banco fora), deixa passar: a licença vale mais que o limite.
  async function pode(chave: string, limite: number, segundos: number) {
    const { data, error } = await sb.rpc("lex_contar_chamada", { p_chave: chave, p_limite: limite, p_segundos: segundos });
    return error ? true : data === true;
  }
  const limite = () => json({ ok: false, motivo: "limite" }, 429);

  // ---- Registro técnico de erro (instalador ou programa). Aceito sem código: o instalador falha antes dele. ----
  if (e.acao === "registro") {
    const origem = e.origem === "programa" ? "programa" : "instalador";
    const instTxt = texto(e.instalacao, 16).toLowerCase();
    const inst = INSTALACAO.test(instTxt) ? instTxt : null;
    if (!(await pode(inst ? `inst:${inst}:registro` : "sem:registro", inst ? 30 : 300, 3600))) return limite();
    const cod = texto(e.codigo, 13).toUpperCase();
    const { error } = await sb.from("lex_registros").insert({ origem, etapa: texto(e.etapa, 60), mensagem: semDadoPessoal(texto(e.mensagem, 2000)),
      versao: texto(e.versao, 20), windows: texto(e.windows, 80), instalacao: inst, codigo: CODIGO.test(cod) ? cod : null });
    return json({ ok: !error });
  }

  // ---- Aceite dos termos (página pública aceite.html). Só esta função grava em sol_aceites: a chave publicável não
  //      executa a função de escrita. Valida, limita, grava, registra o evento e manda e-mail de confirmação. ----
  if (e.acao === "aceite") {
    const codigo = texto(e.codigo, 13).toUpperCase();
    const email = texto(e.email, 120).toLowerCase();
    if (!CODIGO.test(codigo)) return json({ ok: false, motivo: "codigo_invalido" });
    if (!EMAIL.test(email)) return json({ ok: false, motivo: "email_invalido" });
    if (!(await pode(`cod:${codigo}:aceite`, 30, 86400))) return limite();
    const ip = (req.headers.get("x-forwarded-for") ?? "").split(",")[0].trim();
    const { data: r, error: erro } = await sb.rpc("sol_aceite_registrar", { p: {
      app: "radar-judicial", licenca: codigo, termo: texto(e.termo, 60), versao: texto(e.versao, 20), hash: texto(e.hash, 64).toLowerCase(),
      nome: texto(e.nome, 120), email, navegador: texto(e.navegador, 120), origem: e.origem === "site" ? "site" : "email", ip } });
    if (erro || !r || typeof r !== "object") {
      const m = String(erro?.message ?? "");
      const motivo = /desconhecido/i.test(m) ? "codigo_desconhecido" : /tentativas/i.test(m) ? "limite" : /responsável/i.test(m) ? "email_nao_e_do_responsavel"
        : /nome completo/i.test(m) ? "nome_incompleto" : /e-mail/i.test(m) ? "email_invalido" : /termo/i.test(m) ? "dados_invalidos" : "erro";
      return json({ ok: false, motivo }, motivo === "erro" ? 500 : 200);
    }
    const a = r as Record<string, unknown>;
    const quando = new Date(String(a.aceito_em)).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" });
    await sb.from("lex_eventos").insert({ codigo, email, tipo: "licenca_alterada", quem: `cliente:${email}`,
      detalhe: `termos aceitos: versão ${a.versao}, protocolo ${a.protocolo}, por ${a.nome}` });
    // Confirmação para quem aceitou (prova em mãos do escritório) e cópia para a SolverONE. Nunca trava a resposta.
    try {
      const assunto = `LexSuiteONE · aceite dos termos registrado · ${a.protocolo}`;
      const corpo = `Olá, ${a.nome}.\n\nRegistramos o aceite dos termos de uso, da política de privacidade e do termo de tratamento de dados da LexSuiteONE em nome de ${a.escritorio} (código ${codigo}).\n\nProtocolo: ${a.protocolo}\nVersão dos termos: ${a.versao}\nData e hora: ${quando} (Brasília)\nAceito por: ${a.nome} <${email}>\n\nOs termos ficam sempre em ${LINK_ACEITE}. Se você não fez este aceite, responda este e-mail agora.\n\nSolverONE · LexSuiteONE\n\n---\nHello, ${a.nome}. We recorded the acceptance of the LexSuiteONE terms on behalf of ${a.escritorio} (code ${codigo}). Protocol ${a.protocolo}, version ${a.versao}, ${quando} (Brasília). If this was not you, reply to this e-mail now.`;
      await enviarEmail(email, assunto, corpo);
      await enviarEmail(CONTATO, `${assunto} · ${a.escritorio}`, `Licença ${codigo} (${a.escritorio}): termos v${a.versao} aceitos por ${a.nome} <${email}> em ${quando}. Protocolo ${a.protocolo}. Detalhes no RootifyONE.`);
    } catch { /* o registro já está feito; o e-mail é cortesia */ }
    return json({ ok: true, protocolo: a.protocolo, aceito_em: a.aceito_em, escritorio: a.escritorio });
  }

  // ---- Conferência da licença (padrão) e cadastro ----
  const codigo = texto(e.codigo, 13).toUpperCase();
  const instalacao = texto(e.instalacao, 16).toLowerCase();
  const versao = texto(e.versao, 20);
  const acao = e.acao === "cadastrar" ? "cadastrar" : "verificar";
  if (!CODIGO.test(codigo)) return json({ ok: false, motivo: "codigo_invalido" });
  if (!INSTALACAO.test(instalacao)) return json({ ok: false, motivo: "dados_invalidos" });
  if (!(await pode(`inst:${instalacao}:${acao}`, acao === "cadastrar" ? 10 : 6, acao === "cadastrar" ? 3600 : 60))) return limite();
  if (!(await pode(`cod:${codigo}:${acao}`, 120, 3600))) return limite();

  const { data: conta, error } = await sb.from("lex_contas")
    .select("codigo, escritorio, documento, max_pessoas, max_computadores, ativo, validade, mensagem, dominios, email_boas_vindas, exigir_aprovacao, modalidade, exigir_aceite, email_responsavel")
    .eq("codigo", codigo).maybeSingle();
  if (error) return json({ ok: false, motivo: "erro" }, 500);
  if (!conta) return json({ ok: false, motivo: "codigo_desconhecido" });

  const agora = new Date().toISOString();
  const hoje = agora.slice(0, 10);
  const dominios: string[] = Array.isArray(conta.dominios) ? conta.dominios : [];
  const { data: instAntes } = await sb.from("lex_instalacoes").select("email, codigo, esquecida_em").eq("instalacao", instalacao).maybeSingle();
  const instNova = !instAntes || instAntes.codigo !== codigo;
  const evento = (tipo: string, email: string | null, detalhe = "") =>
    sb.from("lex_eventos").insert({ codigo, instalacao, email, tipo, detalhe: detalhe.slice(0, 300) });

  // Pessoas já aprovadas nesta licença (decide "primeira pessoa", e-mail sugerido e limite).
  const { data: aprovadas } = await sb.from("lex_pessoas").select("email, ativa").eq("codigo", codigo).eq("aprovacao", "aprovado");
  const temAprovada = (aprovadas ?? []).length > 0;

  // Instalação nova para este código: contagens para o aviso "código já em uso" (nunca nomes ou e-mails).
  let emUso: Record<string, unknown> | null = null;
  if (instNova) {
    const { data: comps } = await sb.from("lex_computadores").select("primeira_vez, ativo").eq("codigo", codigo).is("esquecida_em", null);
    const lista = comps ?? [];
    if (lista.length > 0 || temAprovada) {
      const primeira = lista.map((c) => String(c.primeira_vez)).sort()[0] ?? agora;
      emUso = { pessoas: (aprovadas ?? []).filter((p) => p.ativa).length, computadores: lista.filter((c) => c.ativo).length, desde: primeira.slice(0, 7) };
    }
    if (lista.length >= (conta.max_computadores ?? 20) + 5) return json({ ok: false, motivo: "limite_de_computadores", escritorio: conta.escritorio });
  }

  // Equipe tinha "esquecido" este computador e ele voltou: limpa e registra.
  if (instAntes && instAntes.codigo === codigo && instAntes.esquecida_em) {
    await sb.from("lex_instalacoes").update({ esquecida_em: null }).eq("instalacao", instalacao);
    await evento("computador_voltou", instAntes.email ?? null);
  }

  let email: string | null = (instAntes && instAntes.codigo === codigo) ? instAntes.email : null;
  const avisos: Array<{ tipo: string; ref: Record<string, string> }> = [];

  if (acao === "cadastrar") {
    const novo = texto(e.email, 120).toLowerCase();
    const nome = texto(e.nome, 60), papel = texto(e.papel, 40);
    const docTipo = ["cnpj", "cpf", "passaporte"].includes(String(e.doc_tipo)) ? String(e.doc_tipo) : "";
    const documento = texto(e.documento, 20).toUpperCase().replace(/[^0-9A-Z]/g, "");
    if (!EMAIL.test(novo) || !nome || !docTipo || documento.length < 5) return json({ ok: false, motivo: "dados_invalidos" });
    const { data: ja } = await sb.from("lex_usuarios").select("codigo, nome, papel, aprovacao").eq("email", novo).maybeSingle();
    // E-mail de outra licença: resposta genérica (não confirma a um estranho que o e-mail existe em outro lugar).
    if (ja && ja.codigo !== codigo) return json({ ok: false, motivo: "dados_invalidos" });
    if (ja && ja.aprovacao === "recusado") return json({ ok: false, motivo: "email_recusado" });

    const dominio = dominioDe(novo);
    const doDominio = dominios.includes(dominio);
    let aprovacao = ja?.aprovacao === "aprovado" ? "aprovado" : (doDominio || !temAprovada) ? "aprovado" : "aguardando";
    if (ja?.aprovacao === "aguardando" && !doDominio) aprovacao = "aguardando";

    // Limite de pessoas: só aprovadas e ativas contam; quem está saindo deste computador não ocupa vaga.
    if (conta.max_pessoas && aprovacao === "aprovado") {
      const outras = (aprovadas ?? []).filter((p) => p.ativa).map((p) => p.email).filter((x) => x !== novo && x !== email);
      if (outras.length >= conta.max_pessoas) return json({ ok: false, motivo: "limite_de_pessoas" });
    }
    const linha: Record<string, unknown> = { email: novo, codigo, nome, papel, atualizado_em: agora, ultima_vez: agora, aprovacao };
    if (aprovacao === "aprovado" && ja?.aprovacao !== "aprovado") { linha.aprovado_por = doDominio ? "dominio" : "primeira_pessoa"; linha.aprovado_em = agora; }
    const r1 = await sb.from("lex_usuarios").upsert(linha, { onConflict: "email" });
    if (r1.error) return json({ ok: false, motivo: "erro" }, 500);
    // Primeira pessoa com e-mail de domínio próprio define o domínio do escritório; o documento só se ainda estiver vazio.
    const ajuste: Record<string, unknown> = {};
    if (!temAprovada && dominios.length === 0 && !PUBLICOS.has(dominio)) ajuste.dominios = [dominio];
    if (!conta.documento) { ajuste.doc_tipo = docTipo; ajuste.documento = documento; }
    if (Object.keys(ajuste).length) await sb.from("lex_contas").update(ajuste).eq("codigo", codigo);

    if (!ja) { await evento("cadastro", novo, nome); avisos.push({ tipo: "pessoa_nova", ref: { nome, dominio } }); }
    else if (email && email !== novo) await evento("troca_de_pessoa", novo, `antes: ${email}`);
    else if (ja.nome !== nome || ja.papel !== papel) await evento("alteracao_de_dados", novo, `nome: ${ja.nome} -> ${nome}; função: ${ja.papel} -> ${papel}`);
    if (aprovacao === "aguardando" && ja?.aprovacao !== "aguardando") await evento("pessoa_aguardando", novo, dominio);
    email = novo;
  }

  const inst: Record<string, unknown> = { instalacao, codigo, versao, ultima_vez: agora };
  if (email) inst.email = email;
  const nomePc = texto(e.nome_pc, 60);
  if (nomePc) inst.nome_pc = nomePc;
  await sb.from("lex_instalacoes").upsert(inst, { onConflict: "instalacao" });
  if (instNova) avisos.push({ tipo: "computador_novo", ref: { nome_pc: nomePc || "(sem nome)", versao } });

  // Uso: última vez da pessoa deste computador e um evento de acesso por dia.
  if (email && acao !== "cadastrar") {
    const { data: u } = await sb.from("lex_usuarios").select("ultima_vez").eq("email", email).maybeSingle();
    await sb.from("lex_usuarios").update({ ultima_vez: agora }).eq("email", email);
    if (!u || !u.ultima_vez || String(u.ultima_vez).slice(0, 10) < hoje) await evento("acesso", email, versao);
  }

  // Avisos por e-mail (caixa de saída + envio pelo Resend, se a chave estiver nos Secrets). Nunca travam a resposta.
  for (const a of avisos) {
    try { await enviarAviso(sb, pode, conta as Record<string, unknown>, a.tipo, a.ref); } catch { /* fica na caixa de saída como falhou */ }
  }

  // Retorno dos processos (só totais; nunca nome, processo, CNPJ ou pessoa). Campo opcional da ação verificar.
  // Linha: {data, tribunal, frente, faixa_valor, situacao, qtd}. Até 2.000 linhas; 1 envio a cada 10 min por instalação.
  let retorno: Record<string, number> | null = null;
  if (acao === "verificar" && Array.isArray(e.retorno)) {
    if (!(await pode(`inst:${instalacao}:retorno`, 1, 600))) {
      retorno = { gravadas: 0, recusadas: 0, limite: 1 };
    } else {
      const linhas: Array<Record<string, unknown>> = [];
      let recusadas = 0;
      for (const l of (e.retorno as unknown[]).slice(0, 2000)) {
        const r = (l && typeof l === "object") ? l as Record<string, unknown> : {};
        const data = texto(r.data, 10), sit = texto(r.situacao, 40).toLowerCase(), qtd = Number(r.qtd);
        if (!/^\d{4}-\d{2}-\d{2}$/.test(data) || !SITUACOES.has(sit) || !Number.isInteger(qtd) || qtd < 0 || qtd > 1_000_000) { recusadas++; continue; }
        linhas.push({ data, dim1: texto(r.tribunal, 40), dim2: texto(r.frente, 40), dim3: texto(r.faixa_valor, 40), situacao: sit, qtd });
      }
      let gravadas = 0;
      if (linhas.length) {
        const { data: n, error: errR } = await sb.rpc("sol_retorno_gravar", { p_app: "radar-judicial", p_licenca: codigo, p_linhas: linhas });
        gravadas = errR ? 0 : Number(n) || 0;
        if (errR) recusadas += linhas.length;
      }
      retorno = { gravadas, recusadas };
    }
  }

  // Situação da pessoa deste computador (para a tela mostrar "aguardando" ou pedir outro e-mail).
  let aprovacaoPessoa = "";
  if (email) {
    const { data: u } = await sb.from("lex_usuarios").select("aprovacao").eq("email", email).maybeSingle();
    aprovacaoPessoa = u?.aprovacao ?? "";
  }
  const vencida = conta.validade && conta.validade < hoje;
  let ok = !!conta.ativo && !vencida;
  let motivo = ok ? "" : (conta.ativo ? "vencido" : "desativado");
  if (ok && conta.exigir_aprovacao && aprovacaoPessoa === "aguardando") { ok = false; motivo = "aguardando_aprovacao"; }
  // Aceite dos termos (decisão do dono, 09/Nov): a licença fica ativa, mas o uso só é liberado depois que o responsável
  // aceita os termos na página pública (sol_aceites). O "cadastrar" passa (registrar a pessoa não é usar); o "verificar" trava.
  let mensagem = conta.mensagem ?? "";
  const { data: aceite } = await sb.rpc("sol_tem_aceite", { p_app: "radar-judicial", p_licenca: codigo, p_termo: "lexsuiteone-termos" });
  const aceiteInfo = (aceite && typeof aceite === "object") ? aceite as Record<string, unknown> : { aceito: false };
  if (ok && conta.exigir_aceite && acao === "verificar" && !aceiteInfo.aceito) {
    ok = false; motivo = "aceite_pendente";
    const link = `${LINK_ACEITE}?codigo=${codigo}` + (conta.email_responsavel || conta.email_boas_vindas ? `&email=${encodeURIComponent(String(conta.email_responsavel || conta.email_boas_vindas))}` : "");
    mensagem = `Antes do primeiro uso, o responsável do escritório precisa aceitar os termos (leva 3 minutos): ${link}`;
    (aceiteInfo as Record<string, unknown>).link = link;
  }
  const resposta: Record<string, unknown> = { ok, motivo, escritorio: conta.escritorio, validade: conta.validade ?? "", mensagem,
    modalidade: conta.modalidade ?? "instalado", aceite: aceiteInfo };   // item F: "nuvem" = a tela avisa e continua lendo
  if (aprovacaoPessoa) resposta.aprovacao = aprovacaoPessoa;
  if (emUso) resposta.em_uso = emUso;
  if (retorno) resposta.retorno = retorno;
  // E-mail de boas-vindas sugerido só enquanto a licença não tem pessoa aprovada (quem tem o código já tem esse e-mail).
  if (!temAprovada && conta.email_boas_vindas && acao === "verificar") resposta.email_sugerido = conta.email_boas_vindas;
  return json(resposta);
});

// Envio simples pelo Resend (texto puro). Sem chave nos Secrets, não envia e não falha.
async function enviarEmail(para: string, assunto: string, corpo: string) {
  const chave = Deno.env.get("RESEND_API_KEY_LEX") || Deno.env.get("RESEND_API_KEY");
  if (!chave || !EMAIL.test(para)) return;
  await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${chave}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: REMETENTE, to: [para], reply_to: CONTATO, subject: assunto, text: corpo }) });
}

// Grava o aviso em lex_avisos e tenta enviar pelo Resend. Para o responsável do escritório: nome da pessoa e domínio
// (gente do próprio escritório). Para a SolverONE: escritório e domínio, sem o e-mail (o detalhe está no RootifyONE).
async function enviarAviso(sb: ReturnType<typeof createClient>, pode: (c: string, l: number, s: number) => Promise<boolean>,
                           conta: Record<string, unknown>, tipo: string, ref: Record<string, string>) {
  const codigo = String(conta.codigo);
  if (!(await pode(`cod:${codigo}:aviso`, AVISOS_POR_DIA, 86400))) return;
  const escritorio = String(conta.escritorio ?? "");
  const destinos: Array<{ para: string; interno: boolean }> = [{ para: CONTATO, interno: true }];
  const resp = String(conta.email_boas_vindas ?? "");
  if (EMAIL.test(resp) && resp !== CONTATO) destinos.push({ para: resp, interno: false });
  const oque = tipo === "pessoa_nova"
    ? `uma pessoa nova se cadastrou no RADAR JUDICIAL${ref.nome ? ` (${ref.nome}, e-mail @${ref.dominio})` : ""}`
    : `um computador novo começou a usar o RADAR JUDICIAL${ref.nome_pc ? ` (${ref.nome_pc})` : ""}`;
  // RESEND_API_KEY_LEX é a chave só de envio desta função (criada em 08/Nov); RESEND_API_KEY já existia no projeto para
  // outra função e não deve ser substituída. Fica como reserva.
  const chave = Deno.env.get("RESEND_API_KEY_LEX") || Deno.env.get("RESEND_API_KEY");
  for (const d of destinos) {
    const assunto = tipo === "pessoa_nova" ? `RADAR JUDICIAL · pessoa nova em ${escritorio}` : `RADAR JUDICIAL · computador novo em ${escritorio}`;
    const corpo = d.interno
      ? `Licença ${codigo} (${escritorio}): ${oque}. Detalhes no RootifyONE, Licenças do RADAR.\n\nLicense ${codigo} (${escritorio}): ${tipo === "pessoa_nova" ? "a new person signed up" : "a new computer started using"} RADAR JUDICIAL. Details in RootifyONE.`
      : `Olá,\n\nNo escritório ${escritorio}, ${oque}. Se não reconhece essa pessoa ou esse computador, responda este e-mail ou escreva para ${CONTATO}.\n\nSolverONE · LexSuiteONE\n\n---\nHello, at ${escritorio} ${tipo === "pessoa_nova" ? "a new person signed up for" : "a new computer started using"} RADAR JUDICIAL. If you do not recognize it, reply to this e-mail or write to ${CONTATO}.`;
    const { data: aviso } = await sb.from("lex_avisos").insert({ codigo, tipo, para: d.para, assunto,
      ref: d.interno ? { dominio: ref.dominio ?? "", nome_pc: ref.nome_pc ?? "" } : ref }).select("id").single();
    if (!aviso) continue;
    if (!chave) { await sb.from("lex_avisos").update({ estado: "pendente", erro: "sem RESEND_API_KEY_LEX nos Secrets" }).eq("id", aviso.id); continue; }
    try {
      const r = await fetch("https://api.resend.com/emails", { method: "POST",
        headers: { Authorization: `Bearer ${chave}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from: REMETENTE, to: [d.para], reply_to: CONTATO, subject: assunto, text: corpo }) });
      if (r.ok) {
        await sb.from("lex_avisos").update({ estado: "enviado", tentativas: 1, enviado_em: new Date().toISOString() }).eq("id", aviso.id);
        await sb.from("lex_eventos").insert({ codigo, tipo: "aviso_enviado", detalhe: `${tipo} → ${d.interno ? "SolverONE" : "responsável"}` });
      } else {
        await sb.from("lex_avisos").update({ estado: "falhou", tentativas: 1, erro: `HTTP ${r.status}` }).eq("id", aviso.id);
        await sb.from("lex_eventos").insert({ codigo, tipo: "aviso_falhou", detalhe: `${tipo}: HTTP ${r.status}` });
      }
    } catch (err) {
      await sb.from("lex_avisos").update({ estado: "falhou", tentativas: 1, erro: String(err && (err as Error).message ? (err as Error).message : err).slice(0, 200) }).eq("id", aviso.id);
    }
  }
}
