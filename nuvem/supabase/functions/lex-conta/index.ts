// LexSuiteONE · RADAR JUDICIAL: confere a licença (código de cliente) e registra quem usa e cada instalação.
// Chamada pelo programa instalado no escritório, sem chave nenhuma (verify_jwt = false). A chave de serviço só
// existe aqui dentro, no Supabase. Tabelas: nuvem/supabase/lex-licencas.sql.
import { createClient } from "jsr:@supabase/supabase-js@2";

const CODIGO = /^LEX-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/;
const INSTALACAO = /^[0-9a-f]{16}$/;
const EMAIL = /^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$/;

function json(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });
}
const texto = (v: unknown, max: number) => String(v ?? "").trim().slice(0, max);

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ ok: false, motivo: "metodo" }, 405);
  let e: Record<string, unknown>;
  try { e = await req.json(); } catch { return json({ ok: false, motivo: "dados_invalidos" }, 400); }
  const codigo = texto(e.codigo, 13).toUpperCase();
  const instalacao = texto(e.instalacao, 16).toLowerCase();
  const versao = texto(e.versao, 20);
  if (!CODIGO.test(codigo)) return json({ ok: false, motivo: "codigo_invalido" });
  if (!INSTALACAO.test(instalacao)) return json({ ok: false, motivo: "dados_invalidos" });

  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
  const { data: conta, error } = await sb.from("lex_contas").select("codigo, escritorio, cnpj, ativo, validade, mensagem").eq("codigo", codigo).maybeSingle();
  if (error) return json({ ok: false, motivo: "erro" }, 500);
  if (!conta) return json({ ok: false, motivo: "codigo_desconhecido" });

  const agora = new Date().toISOString();
  let email: string | null = null;
  if (e.acao === "cadastrar") {
    email = texto(e.email, 120).toLowerCase();
    const nome = texto(e.nome, 60), papel = texto(e.papel, 40), cnpj = texto(e.cnpj, 14).replace(/\D/g, "");
    if (!EMAIL.test(email) || !nome || cnpj.length !== 14) return json({ ok: false, motivo: "dados_invalidos" });
    const { data: ja } = await sb.from("lex_usuarios").select("codigo").eq("email", email).maybeSingle();
    if (ja && ja.codigo !== codigo) return json({ ok: false, motivo: "email_em_outro_escritorio" });
    const r1 = await sb.from("lex_usuarios").upsert({ email, codigo, nome, papel, atualizado_em: agora }, { onConflict: "email" });
    if (r1.error) return json({ ok: false, motivo: "erro" }, 500);
    if (!conta.cnpj) await sb.from("lex_contas").update({ cnpj }).eq("codigo", codigo);
  }
  const inst: Record<string, unknown> = { instalacao, codigo, versao, ultima_vez: agora };
  if (email) inst.email = email;
  await sb.from("lex_instalacoes").upsert(inst, { onConflict: "instalacao" });

  const hoje = new Date().toISOString().slice(0, 10);
  const vencida = conta.validade && conta.validade < hoje;
  const ok = conta.ativo && !vencida;
  return json({ ok, motivo: ok ? "" : (conta.ativo ? "vencido" : "desativado"), escritorio: conta.escritorio,
                validade: conta.validade ?? "", mensagem: conta.mensagem ?? "" });
});
