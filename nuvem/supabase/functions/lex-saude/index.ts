// Central LexSuiteONE · lex-saude v1 (13/Nov/2026): conferência leve dos Diários do DJEN, por tribunal, chamada pelo pg_cron
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

  // Madrugada (0h a 4h59 em Brasília): só a rodada da hora cheia.
  if (hora < 5 && minuto >= 15 && url.searchParams.get("forcar") !== "1") return json({ ok: true, pulou: true, motivo: "madrugada", hora, minuto });

  const rodada = new Date().toISOString();
  const linhas: Linha[] = [];
  for (const sigla of TRIBUNAIS) {
    linhas.push(await conferir(sigla, data));
    await dormir(INTERVALO_MS);
  }
  const { error } = await sb.from("lex_saude_diarios").insert(linhas.map((l) => ({ rodada, ...l, regiao })));
  const resumo = { ok: !error, rodada, regiao, data, total: linhas.length,
    ok_n: linhas.filter((l) => l.estado === "ok").length, lentos: linhas.filter((l) => l.estado === "lento").length,
    fora: linhas.filter((l) => !["ok", "lento"].includes(l.estado)).length, publicados: linhas.filter((l) => l.publicado_hoje).length,
    erro: error ? error.message.slice(0, 120) : undefined };
  console.log(JSON.stringify(resumo));
  return json(resumo, error ? 500 : 200);
});
