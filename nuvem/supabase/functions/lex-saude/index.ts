// Central LexSuiteONE · lex-saude v3 (14/Nov/2026, 0.7.47: alerta à SolverONE quando o CNJ cai, e-mail às instalações que marcaram
// "avisar" (queda de mais de 4 h em dia útil: um na queda, um na volta), sonda da consulta pública um tribunal por rodada,
// ?modo=estado). v1 (13/Nov/2026): conferência leve dos Diários do DJEN, por tribunal, chamada pelo pg_cron
// de 15 em 15 min com o cabeçalho x-region: sa-east-1. Desenho: documentacao/DESENHO-NUVEM-CENTRAL-2026-11-13.md, seção 3.
//
// Segurança: verify_jwt desligado DE PROPÓSITO (quem chama é o cron, sem sessão); a função só aceita o cabeçalho x-saude-chave
// cujo valor ela confere no Vault pela função lex_saude_chave_confere (uma fonte só; rotação = trocar no Vault; nenhum Secret
// a mais). Não usa a chave de serviço no cron. Grava com a chave de serviço do próprio ambiente da função, só na tabela
// lex_saude_diarios. Nenhum dado pessoal passa por aqui.
//
// O que faz: para cada TRT1..TRT24, UM GET à ficha do caderno de hoje (Brasília) no DJEN, sem baixar o ZIP, com 1,2 s entre
// pedidos (o DJEN limita a ~20 por minuto). Classifica e grava 24 linhas com a mesma `rodada` e a região em que rodou.
// ?modo=teste (passo 0): não grava; devolve região, IP de saída e a resposta do DJEN para um tribunal.
import { createClient } from "jsr:@supabase/supabase-js@2";

const URL_CADERNO = "https://comunicaapi.pje.jus.br/api/v1/caderno/{sigla}/{data}/D";   // o mesmo de robo/lexsuite/djen.py
const USER_AGENT = "LexSuiteONE-Central/1 (+https://judicial.solverone.com.br)";
const TRIBUNAIS = Array.from({ length: 24 }, (_, i) => `TRT${i + 1}`);
const INTERVALO_MS = 1200, LIMITE_MS = 15000, LENTO_MS = 4000;
// 0.7.47: sonda da consulta pública (o caminho alternativo do robô, rede.py SONDA_CONSULTA), um tribunal por rodada, em rodízio.
const URL_CONSULTA = "https://comunicaapi.pje.jus.br/api/v1/comunicacao?itensPorPagina=5&siglaTribunal={sigla}&dataDisponibilizacaoInicio={data}&dataDisponibilizacaoFim={data}";
// Alertas (desenho 1.2): CNJ "fora" = 6 ou mais tribunais fora em duas rodadas seguidas; um tribunal só = 4 rodadas seguidas.
const QUEDA_MIN_TRIBUNAIS = 6, TRIBUNAL_RODADAS = 4, CLIENTES_APOS_MS = 4 * 3600_000;
const CONTATO = "judicial@solverone.com.br", REMETENTE = "SolverONE <nao-responda@solverone.com.br>";
const LINK_AJUDA = "https://judicial.solverone.com.br/manual.html";

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });
}
const dormir = (ms: number) => new Promise((r) => setTimeout(r, ms));
function hojeBrasilia(): { data: string; hora: number; minuto: number } {
  const p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date());
  const g = (t: string) => p.find((x) => x.type === t)?.value ?? "00";
  return { data: `${g("year")}-${g("month")}-${g("day")}`, hora: Number(g("hour")) % 24, minuto: Number(g("minute")) };
}

type Linha = { tribunal: string; estado: string; http: number | null; ms: number; publicado_hoje: boolean; detalhe: string };

// Classifica a resposta da ficha do caderno (as mesmas regras do robô: causas.py 30-32, djen.py 22-40, rede.py 77-80).
async function conferir(sigla: string, data: string): Promise<Linha> {
  const inicio = Date.now();
  try {
    const r = await fetch(URL_CADERNO.replace("{sigla}", sigla).replace("{data}", data), {
      headers: { "Accept": "application/json", "User-Agent": USER_AGENT }, signal: AbortSignal.timeout(LIMITE_MS) });
    const ms = Date.now() - inicio;
    const texto = (await r.text()).slice(0, 2000);
    const base = { tribunal: sigla, http: r.status, ms };
    if (r.status === 200) {
      let status = "";
      try { status = String(JSON.parse(texto)?.status ?? ""); } catch { /* sem JSON: trata como publicado */ }
      const vazio = status.toLowerCase().startsWith("sem comunica");
      return { ...base, estado: ms > LENTO_MS ? "lento" : "ok", publicado_hoje: !vazio, detalhe: vazio ? "caderno sem comunicações" : "" };
    }
    if (r.status === 403 && /block access from your country/i.test(texto)) return { ...base, estado: "bloqueado", publicado_hoje: false, detalhe: "block access from your country (IP fora do Brasil)" };
    if (r.status === 403 && /acessados a partir das/i.test(texto)) return { ...base, estado: ms > LENTO_MS ? "lento" : "ok", publicado_hoje: false, detalhe: "antes das 3h" };
    if (r.status === 404) return { ...base, estado: ms > LENTO_MS ? "lento" : "ok", publicado_hoje: false, detalhe: "caderno de hoje não publicado" };
    if (r.status === 429) return { ...base, estado: "limitado", publicado_hoje: false, detalhe: "HTTP 429 (limite de pedidos)" };
    return { ...base, estado: "fora", publicado_hoje: false, detalhe: `HTTP ${r.status}` };
  } catch (err) {
    const m = String((err as Error)?.name === "TimeoutError" ? "tempo esgotado" : (err as Error)?.message ?? err).slice(0, 120);
    return { tribunal: sigla, estado: "fora", http: null, ms: Date.now() - inicio, publicado_hoje: false, detalhe: m };
  }
}

// Sonda da consulta pública: mesma classificação do caderno. 200 com JSON = ok; sem baixar nada além da primeira página de 5 itens.
async function sondarConsulta(sigla: string, data: string): Promise<Linha> {
  const inicio = Date.now();
  try {
    const r = await fetch(URL_CONSULTA.replace("{sigla}", sigla).replaceAll("{data}", data), {
      headers: { "Accept": "application/json", "User-Agent": USER_AGENT }, signal: AbortSignal.timeout(LIMITE_MS) });
    const ms = Date.now() - inicio;
    const texto = (await r.text()).slice(0, 2000);
    const base = { tribunal: sigla, http: r.status, ms, publicado_hoje: false };
    if (r.status === 200) return { ...base, estado: ms > LENTO_MS ? "lento" : "ok", detalhe: "" };
    if (r.status === 403 && /block access from your country/i.test(texto)) return { ...base, estado: "bloqueado", detalhe: "block access from your country" };
    if (r.status === 429) return { ...base, estado: "limitado", detalhe: "HTTP 429" };
    return { ...base, estado: "fora", detalhe: `HTTP ${r.status}` };
  } catch (err) {
    const m = String((err as Error)?.name === "TimeoutError" ? "tempo esgotado" : (err as Error)?.message ?? err).slice(0, 120);
    return { tribunal: sigla, estado: "fora", http: null, ms: Date.now() - inicio, publicado_hoje: false, detalhe: m };
  }
}

// E-mail pelo Resend (a mesma chave só de envio da lex-conta). Registra em lex_saude_alertas; nunca derruba a rodada.
// deno-lint-ignore no-explicit-any
async function enviar(sb: any, tipo: string, chave: string, para: string, assunto: string, corpo: string): Promise<boolean> {
  const key = Deno.env.get("RESEND_API_KEY_LEX") || Deno.env.get("RESEND_API_KEY");
  let ok = false, erro = "";
  if (!key) erro = "sem RESEND_API_KEY_LEX";
  else {
    try {
      const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from: REMETENTE, to: [para], reply_to: CONTATO, subject: assunto, text: corpo }), signal: AbortSignal.timeout(10000) });
      ok = r.ok; if (!r.ok) erro = `HTTP ${r.status}`;
    } catch (e) { erro = String((e as Error)?.message ?? e).slice(0, 120); }
  }
  await sb.from("lex_saude_alertas").insert({ tipo, chave, para, assunto, ok, erro: erro || null });
  return ok;
}
// deno-lint-ignore no-explicit-any
async function enviouHaPouco(sb: any, chave: string, horas: number): Promise<boolean> {
  const { data } = await sb.from("lex_saude_alertas").select("id").eq("chave", chave).eq("ok", true).gte("enviado_em", new Date(Date.now() - horas * 3600_000).toISOString()).limit(1);
  return Array.isArray(data) && data.length > 0;
}
const hhmm = (iso: string) => new Intl.DateTimeFormat("pt-BR", { timeZone: "America/Sao_Paulo", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(iso)).replace(":", "h");
const diaUtil = () => { const d = new Intl.DateTimeFormat("en-US", { timeZone: "America/Sao_Paulo", weekday: "short" }).format(new Date()); return !["Sat", "Sun"].includes(d); };

// Alertas depois da rodada: abre/fecha a queda, avisa a SolverONE (1 por hora por chave) e, na queda longa em dia útil, as
// instalações que marcaram "avisar" (um e-mail na queda, um na volta). Nunca derruba a rodada.
// deno-lint-ignore no-explicit-any
async function alertas(sb: any, rodada: string, linhas: Linha[], consulta: Linha | null) {
  const foraAgora = linhas.filter((l) => !["ok", "lento"].includes(l.estado)).map((l) => l.tribunal);
  const okN = linhas.length - foraAgora.length;
  // rodada anterior (24 linhas) para exigir duas seguidas
  const { data: ant } = await sb.from("lex_saude_diarios").select("rodada, tribunal, estado").lt("rodada", rodada).order("rodada", { ascending: false }).limit(24 * TRIBUNAL_RODADAS);
  const porRodada = new Map<string, Array<{ tribunal: string; estado: string }>>();
  for (const r of (ant ?? []) as Array<{ rodada: string; tribunal: string; estado: string }>) { const a = porRodada.get(r.rodada) ?? []; a.push(r); porRodada.set(r.rodada, a); }
  const rodadasAnt = [...porRodada.keys()].sort().reverse();
  const foraNa = (k: string) => (porRodada.get(k) ?? []).filter((x) => !["ok", "lento"].includes(x.estado)).map((x) => x.tribunal);
  const foraAnterior = rodadasAnt[0] ? foraNa(rodadasAnt[0]) : [];
  const { data: abertas } = await sb.from("lex_saude_quedas").select("*").is("fim", null).order("inicio", { ascending: false }).limit(1);
  const queda = (abertas ?? [])[0] as Record<string, unknown> | undefined;
  const consTxt = consulta ? `Consulta pública (${consulta.tribunal}): ${consulta.estado}${consulta.detalhe ? ` (${consulta.detalhe})` : ""}.` : "";

  if (queda) {
    if (foraAgora.length < QUEDA_MIN_TRIBUNAIS) {   // voltou
      const fim = new Date().toISOString();
      const inicio = String(queda.inicio);
      const dur = Math.round((Date.now() - new Date(inicio).getTime()) / 60000);
      const durTxt = `${Math.floor(dur / 60)}h${String(dur % 60).padStart(2, "0")}`;
      await sb.from("lex_saude_quedas").update({ fim, max_fora: Math.max(Number(queda.max_fora) || 0, foraAgora.length) }).eq("id", queda.id);
      const okS = await enviar(sb, "cnj_voltou", "solverone:cnj", CONTATO, `[CNJ] caderno voltou: ${okN} de ${linhas.length} tribunais ok (fora desde ${hhmm(inicio)}, ${durTxt})`,
        `O serviço de caderno do DJEN voltou às ${hhmm(fim)} (Brasília). Fora desde ${hhmm(inicio)}, ${durTxt}. Pior momento: ${queda.max_fora} tribunais fora. ${consTxt}\nCentral: aba Diários.`);
      if (okS) await sb.from("lex_saude_quedas").update({ volta_solverone_em: fim }).eq("id", queda.id);
      if (queda.aviso_clientes_em && !queda.volta_clientes_em) {
        const n = await avisarInstalacoes(sb, "cnj_voltou", `clientes:cnj:volta:${queda.id}`,
          `RADAR JUDICIAL · o Diário do CNJ voltou (${hhmm(fim)})`,
          `Olá.\n\nO serviço do Diário de Justiça Eletrônico Nacional (DJEN, do CNJ) voltou a funcionar às ${hhmm(fim)} (Brasília). Ficou fora desde ${hhmm(inicio)}. A próxima leitura do RADAR JUDICIAL pega o que faltou; não é preciso fazer nada.\n\nVocê recebe este aviso porque marcou "Avisar por e-mail quando o CNJ ficar fora" em Configuração; para parar, desmarque.\n\nSolverONE · LexSuiteONE\n\n---\nHello. The CNJ court gazette service (DJEN) is back since ${hhmm(fim)} (Brasília), after being down since ${hhmm(inicio)}. The next RADAR JUDICIAL reading catches up on its own. You get this because "E-mail me when the CNJ is down" is on in Settings.`);
        if (n > 0) await sb.from("lex_saude_quedas").update({ volta_clientes_em: fim }).eq("id", queda.id);
      }
      return;
    }
    // continua fora: atualiza o pior momento; queda longa em dia útil → avisa as instalações que marcaram (uma vez por queda)
    await sb.from("lex_saude_quedas").update({ max_fora: Math.max(Number(queda.max_fora) || 0, foraAgora.length), tribunais: foraAgora }).eq("id", queda.id);
    const inicio = String(queda.inicio);
    if (!queda.aviso_clientes_em && diaUtil() && Date.now() - new Date(inicio).getTime() >= CLIENTES_APOS_MS) {
      const n = await avisarInstalacoes(sb, "cnj_fora", `clientes:cnj:queda:${queda.id}`,
        `RADAR JUDICIAL · o Diário do CNJ está fora do ar desde ${hhmm(inicio)}`,
        `Olá.\n\nO serviço do Diário de Justiça Eletrônico Nacional (DJEN, do CNJ) está fora do ar desde ${hhmm(inicio)} (Brasília) para ${foraAgora.length} dos ${linhas.length} tribunais do trabalho. Não é problema do seu computador nem do RADAR JUDICIAL: o programa tenta de novo sozinho nos horários da leitura e avisaremos quando voltar.\n\nVocê recebe este aviso porque marcou "Avisar por e-mail quando o CNJ ficar fora" em Configuração; para parar, desmarque.\n\nSolverONE · LexSuiteONE\n\n---\nHello. The CNJ court gazette service (DJEN) has been down since ${hhmm(inicio)} (Brasília) for ${foraAgora.length} of ${linhas.length} labor courts. It is not your computer or RADAR JUDICIAL: the program retries on its own and we will e-mail you when it is back. You get this because "E-mail me when the CNJ is down" is on in Settings.`);
      await sb.from("lex_saude_quedas").update({ aviso_clientes_em: new Date().toISOString(), destinatarios: n }).eq("id", queda.id);
    }
    return;
  }

  // sem queda aberta: abre quando 6+ tribunais fora em duas rodadas seguidas; avisa a SolverONE (1 por hora)
  if (foraAgora.length >= QUEDA_MIN_TRIBUNAIS && foraAnterior.length >= QUEDA_MIN_TRIBUNAIS) {
    const inicio = rodadasAnt[0] ?? rodada;
    const { data: nova } = await sb.from("lex_saude_quedas").insert({ inicio, max_fora: foraAgora.length, tribunais: foraAgora }).select("id").single();
    if (!(await enviouHaPouco(sb, "solverone:cnj", 1))) {
      const ok = await enviar(sb, "cnj_fora", "solverone:cnj", CONTATO, `[CNJ] caderno fora: ${foraAgora.length} de ${linhas.length} tribunais desde ${hhmm(inicio)}`,
        `O serviço de caderno do DJEN está fora para ${foraAgora.length} de ${linhas.length} tribunais desde ${hhmm(inicio)} (Brasília), em duas rodadas seguidas.\nFora: ${foraAgora.join(", ")}.\n${consTxt}\nSe passar de 4 h em dia útil, as instalações que marcaram "avisar" recebem um e-mail. Central: aba Diários.`);
      if (ok && nova) await sb.from("lex_saude_quedas").update({ aviso_solverone_em: new Date().toISOString() }).eq("id", nova.id);
    }
    return;
  }
  // um tribunal só, fora há 4 rodadas seguidas: aviso à SolverONE, no máximo 1 a cada 6 h por tribunal
  if (rodadasAnt.length >= TRIBUNAL_RODADAS - 1) {
    for (const t of foraAgora) {
      const seguidas = rodadasAnt.slice(0, TRIBUNAL_RODADAS - 1).every((k) => foraNa(k).includes(t));
      if (seguidas && !(await enviouHaPouco(sb, `solverone:trib:${t}`, 6))) {
        const det = linhas.find((l) => l.tribunal === t)?.detalhe ?? "";
        await enviar(sb, "tribunal_fora", `solverone:trib:${t}`, CONTATO, `[CNJ] caderno do ${t} fora há ${TRIBUNAL_RODADAS} rodadas`, `O caderno do ${t} está fora há ${TRIBUNAL_RODADAS} rodadas seguidas (${det}). Os demais tribunais respondem. Central: aba Diários.`);
      }
    }
  }
}

// Um e-mail por endereço cadastrado nas instalações que marcaram "avisar" (licenças ativas; nunca o mesmo endereço duas vezes).
// deno-lint-ignore no-explicit-any
async function avisarInstalacoes(sb: any, tipo: string, chave: string, assunto: string, corpo: string): Promise<number> {
  const { data } = await sb.from("lex_instalacoes").select("email, codigo").eq("avisar_cnj", true).is("esquecida_em", null).not("email", "is", null);
  const { data: contas } = await sb.from("lex_contas").select("codigo").eq("ativo", true);
  const ativas = new Set(((contas ?? []) as Array<{ codigo: string }>).map((c) => c.codigo));
  const emails = [...new Set(((data ?? []) as Array<{ email: string; codigo: string }>).filter((i) => ativas.has(i.codigo))
    .map((i) => String(i.email).toLowerCase()).filter((e) => /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(e)))];
  let n = 0;
  for (const para of emails.slice(0, 200)) if (await enviar(sb, tipo, chave, para, assunto, corpo)) n++;
  return n;
}

Deno.serve(async (req) => {
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  const chave = (req.headers.get("x-saude-chave") ?? "").slice(0, 128);
  const { data: autorizado, error: erroChave } = chave ? await sb.rpc("lex_saude_chave_confere", { p_chave: chave }) : { data: false, error: null };
  if (erroChave || autorizado !== true) return json({ ok: false, motivo: "nao_autorizado" }, 401);
  const regiao = Deno.env.get("SB_REGION") ?? "";
  const { data, hora, minuto } = hojeBrasilia();
  const url = new URL(req.url);

  // Passo 0: região, IP de saída e uma resposta do DJEN, sem gravar nada.
  if (url.searchParams.get("modo") === "teste") {
    let ip = "";
    try { ip = String((await (await fetch("https://api.ipify.org?format=json", { signal: AbortSignal.timeout(8000) })).json()).ip ?? ""); } catch (e) { ip = `erro: ${String((e as Error)?.message ?? e).slice(0, 80)}`; }
    const amostra = await conferir(url.searchParams.get("tribunal") || "TRT2", data);
    return json({ ok: true, regiao, ip, data, amostra });
  }

  // Estado atual num objeto só (o mesmo que a lex-conta devolve em estado_cnj), para conferir sem gravar.
  if (url.searchParams.get("modo") === "estado") {
    const { data: est, error: erroEst } = await sb.rpc("lex_saude_estado");
    return json({ ok: !erroEst, estado: est ?? null, erro: erroEst ? erroEst.message : undefined });
  }

  // Madrugada (0h a 4h59 em Brasília): só a rodada da hora cheia.
  if (hora < 5 && minuto >= 15 && url.searchParams.get("forcar") !== "1") return json({ ok: true, pulou: true, motivo: "madrugada", hora, minuto });

  const rodada = new Date().toISOString();
  const linhas: Linha[] = [];
  for (const sigla of TRIBUNAIS) {
    linhas.push(await conferir(sigla, data));
    await dormir(INTERVALO_MS);
  }
  const { error } = await sb.from("lex_saude_diarios").insert(linhas.map((l) => ({ rodada, ...l, regiao })));
  // 0.7.47: sonda da consulta pública num tribunal por rodada (rodízio pelas rodadas de 15 min) e os alertas.
  let consulta: Linha | null = null;
  try {
    const sigla = TRIBUNAIS[Math.floor(Date.now() / 900_000) % TRIBUNAIS.length];
    await dormir(INTERVALO_MS);
    consulta = await sondarConsulta(sigla, data);
    await sb.from("lex_saude_consulta").insert({ rodada, tribunal: consulta.tribunal, estado: consulta.estado, http: consulta.http, ms: consulta.ms, detalhe: consulta.detalhe || null, regiao });
  } catch (e) { console.log("sonda da consulta falhou: " + String((e as Error)?.message ?? e).slice(0, 120)); }
  if (!error) { try { await alertas(sb, rodada, linhas, consulta); } catch (e) { console.log("alertas falharam: " + String((e as Error)?.message ?? e).slice(0, 160)); } }
  const resumo = { ok: !error, rodada, regiao, data, total: linhas.length,
    ok_n: linhas.filter((l) => l.estado === "ok").length, lentos: linhas.filter((l) => l.estado === "lento").length,
    fora: linhas.filter((l) => !["ok", "lento"].includes(l.estado)).length, publicados: linhas.filter((l) => l.publicado_hoje).length,
    consulta: consulta ? { tribunal: consulta.tribunal, estado: consulta.estado, ms: consulta.ms } : null,
    erro: error ? error.message.slice(0, 120) : undefined };
  console.log(JSON.stringify(resumo));
  return json(resumo, error ? 500 : 200);
});
