// LexSuiteONE · RADAR JUDICIAL · lex-conta v4 (revisão 2, com modalidade): confere a licença (código de cliente), registra quem usa cada computador,
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
const REMETENTE = "SolverONE <nao-responda@solverone.com.br>";
const AVISOS_POR_DIA = 20;

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
    .select("codigo, escritorio, documento, max_pessoas, max_computadores, ativo, validade, mensagem, dominios, email_boas_vindas, exigir_aprovacao, modalidade")
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
  const resposta: Record<string, unknown> = { ok, motivo, escritorio: conta.escritorio, validade: conta.validade ?? "", mensagem: conta.mensagem ?? "",
    modalidade: conta.modalidade ?? "instalado" };   // item F: "nuvem" = a tela avisa e continua lendo
  if (aprovacaoPessoa) resposta.aprovacao = aprovacaoPessoa;
  if (emUso) resposta.em_uso = emUso;
  // E-mail de boas-vindas sugerido só enquanto a licença não tem pessoa aprovada (quem tem o código já tem esse e-mail).
  if (!temAprovada && conta.email_boas_vindas && acao === "verificar") resposta.email_sugerido = conta.email_boas_vindas;
  return json(resposta);
});

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
  const chave = Deno.env.get("RESEND_API_KEY");
  for (const d of destinos) {
    const assunto = tipo === "pessoa_nova" ? `RADAR JUDICIAL · pessoa nova em ${escritorio}` : `RADAR JUDICIAL · computador novo em ${escritorio}`;
    const corpo = d.interno
      ? `Licença ${codigo} (${escritorio}): ${oque}. Detalhes no RootifyONE, Licenças do RADAR.\n\nLicense ${codigo} (${escritorio}): ${tipo === "pessoa_nova" ? "a new person signed up" : "a new computer started using"} RADAR JUDICIAL. Details in RootifyONE.`
      : `Olá,\n\nNo escritório ${escritorio}, ${oque}. Se não reconhece essa pessoa ou esse computador, responda este e-mail ou escreva para ${CONTATO}.\n\nSolverONE · LexSuiteONE\n\n---\nHello, at ${escritorio} ${tipo === "pessoa_nova" ? "a new person signed up for" : "a new computer started using"} RADAR JUDICIAL. If you do not recognize it, reply to this e-mail or write to ${CONTATO}.`;
    const { data: aviso } = await sb.from("lex_avisos").insert({ codigo, tipo, para: d.para, assunto,
      ref: d.interno ? { dominio: ref.dominio ?? "", nome_pc: ref.nome_pc ?? "" } : ref }).select("id").single();
    if (!aviso) continue;
    if (!chave) { await sb.from("lex_avisos").update({ estado: "pendente", erro: "sem RESEND_API_KEY nos Secrets" }).eq("id", aviso.id); continue; }
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
