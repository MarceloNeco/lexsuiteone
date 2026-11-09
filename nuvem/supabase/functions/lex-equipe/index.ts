// LexSuiteONE · RADAR JUDICIAL · lex-equipe v1: ações da EQUIPE da SolverONE a partir do RootifyONE, com o login da
// equipe (verify_jwt = true: só chega aqui quem tem um token válido do projeto). A função ainda confere no banco que a
// pessoa é dono ou admin da equipe (eh_admin_equipe) antes de fazer qualquer coisa.
//
// Ações:
//   boas_vindas  → envia o e-mail de boas-vindas de uma licença pelo Resend (RESEND_API_KEY_LEX nos Secrets; a antiga
//                  RESEND_API_KEY só como reserva). A PRÉVIA (destinatário, assunto, texto) é montada no RootifyONE e o
//                  clique do dono depois da confirmação é a autorização (decisão do dono, 09/Nov). O código da licença
//                  vai no corpo do e-mail e nunca para o log: o histórico guarda só "boas-vindas enviado → <para>".
// Limites: 10 envios por hora por licença. Nenhum segredo no código; nada é gravado além do histórico.
import { createClient } from "jsr:@supabase/supabase-js@2";

const EMAIL = /^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$/;
const CODIGO = /^LEX-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/;
const REMETENTE = "SolverONE <nao-responda@solverone.com.br>";
const CONTATO = "judicial@solverone.com.br";

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, apikey, content-type", "Access-Control-Allow-Methods": "POST, OPTIONS" } });
}
const texto = (v: unknown, max: number) => String(v ?? "").trim().slice(0, max);

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return json({ ok: true });
  if (req.method !== "POST") return json({ ok: false, motivo: "metodo" }, 405);
  const auth = req.headers.get("Authorization") ?? "";
  if (!auth.startsWith("Bearer ")) return json({ ok: false, motivo: "sem_login" }, 401);
  let e: Record<string, unknown>;
  try { e = await req.json(); } catch { return json({ ok: false, motivo: "dados_invalidos" }, 400); }

  // Quem chama: cliente com o token da pessoa (para eh_admin_equipe e auth.uid valerem); gravações com a chave de serviço.
  const url = Deno.env.get("SUPABASE_URL")!;
  const comoPessoa = createClient(url, Deno.env.get("SUPABASE_ANON_KEY")!, { global: { headers: { Authorization: auth } }, auth: { persistSession: false } });
  const servico = createClient(url, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  const { data: ehAdmin, error: errAdmin } = await comoPessoa.rpc("eh_admin_equipe");
  if (errAdmin || ehAdmin !== true) return json({ ok: false, motivo: "so_equipe" }, 403);
  const { data: quem } = await comoPessoa.auth.getUser();
  const quemTxt = "equipe:" + (quem?.user?.id ?? "?");

  if (e.acao === "boas_vindas") {
    const codigo = texto(e.codigo, 13).toUpperCase();
    const para = texto(e.para, 120).toLowerCase();
    const assunto = texto(e.assunto, 150);
    const html = String(e.html ?? "").slice(0, 200_000);
    const txt = String(e.texto ?? "").slice(0, 50_000);
    if (!CODIGO.test(codigo) || !EMAIL.test(para) || !assunto || (!html && !txt)) return json({ ok: false, motivo: "dados_invalidos" });
    const { data: conta } = await servico.from("lex_contas").select("codigo, escritorio").eq("codigo", codigo).maybeSingle();
    if (!conta) return json({ ok: false, motivo: "codigo_desconhecido" });
    const { data: pode } = await servico.rpc("lex_contar_chamada", { p_chave: `cod:${codigo}:boas_vindas`, p_limite: 10, p_segundos: 3600 });
    if (pode === false) return json({ ok: false, motivo: "limite" }, 429);
    const chave = Deno.env.get("RESEND_API_KEY_LEX") || Deno.env.get("RESEND_API_KEY");
    if (!chave) return json({ ok: false, motivo: "sem_chave_resend" });
    const r = await fetch("https://api.resend.com/emails", { method: "POST",
      headers: { Authorization: `Bearer ${chave}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: REMETENTE, to: [para], reply_to: CONTATO, subject: assunto, html: html || undefined, text: txt || undefined }) });
    const corpo = await r.json().catch(() => ({}));
    await servico.from("lex_eventos").insert({ codigo, email: para, tipo: r.ok ? "aviso_enviado" : "aviso_falhou",
      detalhe: r.ok ? `boas-vindas enviado → ${para}` : `boas-vindas falhou: HTTP ${r.status}`, quem: quemTxt });
    await servico.rpc("lab_registrar_log", { p_acao: r.ok ? "lex_boas_vindas_enviado" : "lex_boas_vindas_falhou", p_quem: quem?.user?.id ?? null,
      p_depois: { codigo, para, assunto }, p_antes: null }).then(() => {}, () => {});
    if (!r.ok) return json({ ok: false, motivo: "resend", detalhe: `HTTP ${r.status}` }, 502);
    return json({ ok: true, id: (corpo as Record<string, unknown>).id ?? null });
  }
  return json({ ok: false, motivo: "acao_desconhecida" }, 400);
});
