// LexSuiteONE · RADAR JUDICIAL: confere a licença (código de cliente), registra quem usa cada computador e o uso.
// Chamada pelo programa instalado no escritório e pelo instalador, sem chave nenhuma (verify_jwt = false). A chave de
// serviço só existe aqui dentro, no Supabase. Tabelas: nuvem/supabase/lex-licencas.sql.
//
// Modelo: a licença é do escritório (código); a unidade estável é o computador (instalação, identificação aleatória);
// a pessoa é o e-mail ligado ao computador agora. Trocar o e-mail num computador = outra pessoa usando; a anterior
// fica no histórico e deixa de contar como ativa. Ativa = ligada a um computador e vista nos últimos 30 dias.
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
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

  // Registro técnico de erro (instalador ou programa). Aceito sem código de cliente: o instalador falha antes dele.
  // Limites: tamanho dos campos e no máximo 30 registros por instalação (ou sem instalação) por hora.
  if (e.acao === "registro") {
    const origem = e.origem === "programa" ? "programa" : "instalador";
    const inst = INSTALACAO.test(texto(e.instalacao, 16).toLowerCase()) ? texto(e.instalacao, 16).toLowerCase() : null;
    const desde = new Date(Date.now() - 3600_000).toISOString();
    let q = sb.from("lex_registros").select("id", { count: "exact", head: true }).gte("criado_em", desde);
    q = inst ? q.eq("instalacao", inst) : q.is("instalacao", null);
    const { count } = await q;
    if ((count ?? 0) >= 30) return json({ ok: false, motivo: "limite" });
    const cod = texto(e.codigo, 13).toUpperCase();
    await sb.from("lex_registros").insert({ origem, etapa: texto(e.etapa, 60), mensagem: texto(e.mensagem, 2000), versao: texto(e.versao, 20),
      windows: texto(e.windows, 80), instalacao: inst, codigo: CODIGO.test(cod) ? cod : null });
    return json({ ok: true });
  }

  const codigo = texto(e.codigo, 13).toUpperCase();
  const instalacao = texto(e.instalacao, 16).toLowerCase();
  const versao = texto(e.versao, 20);
  if (!CODIGO.test(codigo)) return json({ ok: false, motivo: "codigo_invalido" });
  if (!INSTALACAO.test(instalacao)) return json({ ok: false, motivo: "dados_invalidos" });

  const { data: conta, error } = await sb.from("lex_contas").select("codigo, escritorio, documento, max_pessoas, ativo, validade, mensagem").eq("codigo", codigo).maybeSingle();
  if (error) return json({ ok: false, motivo: "erro" }, 500);
  if (!conta) return json({ ok: false, motivo: "codigo_desconhecido" });

  const agora = new Date().toISOString();
  const hoje = agora.slice(0, 10);
  const { data: instAntes } = await sb.from("lex_instalacoes").select("email, codigo").eq("instalacao", instalacao).maybeSingle();
  const evento = (tipo: string, email: string | null, detalhe = "") =>
    sb.from("lex_eventos").insert({ codigo, instalacao, email, tipo, detalhe: detalhe.slice(0, 300) });

  let email: string | null = (instAntes && instAntes.codigo === codigo) ? instAntes.email : null;
  if (e.acao === "cadastrar") {
    const novo = texto(e.email, 120).toLowerCase();
    const nome = texto(e.nome, 60), papel = texto(e.papel, 40);
    const docTipo = ["cnpj", "cpf", "passaporte"].includes(String(e.doc_tipo)) ? String(e.doc_tipo) : "";
    const documento = texto(e.documento, 20).toUpperCase().replace(/[^0-9A-Z]/g, "");
    if (!EMAIL.test(novo) || !nome || !docTipo || documento.length < 5) return json({ ok: false, motivo: "dados_invalidos" });
    const { data: ja } = await sb.from("lex_usuarios").select("codigo, nome, papel").eq("email", novo).maybeSingle();
    if (ja && ja.codigo !== codigo) return json({ ok: false, motivo: "email_em_outro_escritorio" });
    // Limite: só pessoas ativas contam; a pessoa que está saindo deste computador não ocupa vaga.
    if (conta.max_pessoas) {
      const { data: ativas } = await sb.from("lex_pessoas").select("email").eq("codigo", codigo).eq("ativa", true);
      const outras = (ativas ?? []).map((p) => p.email).filter((x) => x !== novo && x !== email);
      if (outras.length >= conta.max_pessoas) return json({ ok: false, motivo: "limite_de_pessoas" });
    }
    const r1 = await sb.from("lex_usuarios").upsert({ email: novo, codigo, nome, papel, atualizado_em: agora, ultima_vez: agora }, { onConflict: "email" });
    if (r1.error) return json({ ok: false, motivo: "erro" }, 500);
    if (!conta.documento) await sb.from("lex_contas").update({ doc_tipo: docTipo, documento }).eq("codigo", codigo);
    if (!email) await evento("cadastro", novo, nome);
    else if (email !== novo) await evento("troca_de_pessoa", novo, `antes: ${email}`);
    else if (ja && (ja.nome !== nome || ja.papel !== papel)) await evento("alteracao_de_dados", novo, `nome: ${ja.nome} -> ${nome}; função: ${ja.papel} -> ${papel}`);
    email = novo;
  }

  const inst: Record<string, unknown> = { instalacao, codigo, versao, ultima_vez: agora };
  if (email) inst.email = email;
  await sb.from("lex_instalacoes").upsert(inst, { onConflict: "instalacao" });

  // Uso: última vez da pessoa deste computador e um evento de acesso por dia.
  if (email && e.acao !== "cadastrar") {
    const { data: u } = await sb.from("lex_usuarios").select("ultima_vez").eq("email", email).maybeSingle();
    await sb.from("lex_usuarios").update({ ultima_vez: agora }).eq("email", email);
    if (!u || !u.ultima_vez || String(u.ultima_vez).slice(0, 10) < hoje) await evento("acesso", email, versao);
  }

  const vencida = conta.validade && conta.validade < hoje;
  const ok = conta.ativo && !vencida;
  return json({ ok, motivo: ok ? "" : (conta.ativo ? "vencido" : "desativado"), escritorio: conta.escritorio,
                validade: conta.validade ?? "", mensagem: conta.mensagem ?? "" });
});
