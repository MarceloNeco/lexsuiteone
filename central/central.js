"use strict";
/* Central LexSuiteONE 0.1.0 (13/Nov/2026). Painel da equipe SolverONE. JS puro, sem biblioteca e sem build.
   Entrada: Supabase Auth (senha) + código do aplicativo autenticador (MFA TOTP, sessão aal2). A sessão fica só nesta aba
   (sessionStorage): recarregar não pede de novo; fechar a aba, "Sair" ou 15 min parado encerram.
   Dados: só funções admin_* do banco, que conferem a equipe. Aba sem função ainda mostra demonstração, marcada. */
var CFG = window.CENTRAL_CFG || {};
var lang = "pt";
var T = {
  pt: {
    e_sub: "Área da equipe SolverONE. Só entra quem está na lista da equipe.", e_email: "E-mail", e_senha: "Senha", e_entrar: "Entrar",
    e_nota: "Sem login com Google: a administração entra só com senha e o código de 6 números do celular.",
    c_x: "Primeira vez: no celular, abra o aplicativo autenticador (Google Authenticator ou Microsoft Authenticator), toque em + e leia este quadrado.",
    c_ou: "Se não der para ler, digite esta chave no aplicativo:", c_cod: "Código de 6 números que apareceu no aplicativo", c_ok: "Confirmar",
    m_cod: "Código de 6 números do aplicativo autenticador", m_ok: "Entrar", m_voltar: "Voltar",
    er_senha: "E-mail ou senha não conferem.", er_cod: "Código errado ou vencido. Confira no aplicativo e digite o código de agora.",
    er_equipe: "Esta conta não está na lista da equipe.", er_rede: "Sem resposta da nuvem. Confira a internet e tente de novo.",
    er_mfa: "O código do celular não está ligado na nuvem (Authentication → MFA). Avise a Arquitetura.", tranc: "Trancado por inatividade. Entre de novo.",
    demo: "Demonstração: esta aba ainda mostra dados fictícios. A nuvem dela está pedida à Arquitetura (fase 1).",
    real: "Dados de verdade, lidos agora da nuvem.", lic_ativas: "ativa", lic_pausada: "pausada", carregando: "Carregando…",
    proto: "Protótipo com dados FICTÍCIOS · nada aqui é real e nada sai deste arquivo",
    sair: "Sair", prod: "RADAR JUDICIAL",
    a_geral: "Visão geral", a_diarios: "Saúde dos Diários", a_inst: "Escritórios e computadores", a_leit: "Leituras dos escritórios",
    a_erros: "Erros", a_est: "Estatísticas", a_lic: "Licenças",
    g_t: "Como estão as coisas agora", g_s: "Atualizado às 15:30 (horário de Brasília). Cada quadro abre o detalhe.",
    k_trib: "Diários do CNJ", k_trib_d: "{f} fora · {l} lentos", k_inst: "Computadores ativos", k_inst_d: "{n} sem conferir há 3 dias",
    k_ver: "Na versão atual", k_ver_d: "{n} em versão antiga", k_err: "Erros em 24 h", k_err_d: "{n} computadores",
    k_proc: "Processos novos hoje", k_proc_d: "soma de todos os escritórios", k_lic: "Licenças", k_lic_d: "{a} ativas · {t} de teste",
    d_t: "Saúde dos Diários (CNJ)", d_s: "A cada 15 minutos, a nuvem da SolverONE pergunta ao CNJ pela ficha do Diário de cada tribunal (um pedido leve, sem baixar o Diário). Verde: respondeu; amarelo: respondeu devagar; vermelho: erro ou sem resposta.",
    d_hoje: "Diário de hoje", d_pub: "publicado", d_nao: "ainda não", d_resp: "resposta", d_ult: "conferido às {h}",
    d_hist: "Últimas 24 horas (todos os tribunais)", d_hist_s: "Cada barra é uma conferência; a altura é quantos tribunais responderam bem.",
    i_t: "Escritórios e computadores", i_s: "Cada computador com o programa, a versão e a última vez que conferiu a licença.",
    i_esc: "Escritório", i_pc: "Computador", i_ver: "Versão", i_ult: "Última conferência", i_sit: "Situação", i_ok: "em dia", i_velha: "versão antiga", i_parado: "parado há {d} dias",
    l_t: "Leituras dos escritórios", l_s: "O que cada leitura do programa conseguiu, por tribunal (só contagens: lido, CNJ fora, erro).",
    l_falta: "Falta para existir: o programa ainda não manda este resumo. Precisa de uma versão nova do RADAR e de revisar o que vai à SolverONE (termos, seção dos dados enviados). Pergunta ao dono no quadro.",
    e_t: "Erros", e_s: "O que o instalador e o programa mandaram (sem caminho de pasta nem dado pessoal).",
    e_quando: "Quando", e_orig: "Origem", e_etapa: "Etapa", e_msg: "Mensagem", e_ver: "Versão",
    s_t: "Estatísticas", s_s: "Só contagens que os escritórios mandam (por dia, tribunal, frente e situação). Nenhum nome de empresa nem número de processo.",
    s_dia: "Processos novos por dia (todos os escritórios, 30 dias)", s_trib: "Por tribunal (30 dias)", s_sit: "Por situação (30 dias)",
    lic_t: "Licenças", lic_s: "Cadastro, ativar e pausar, e-mails e termos continuam no RootifyONE (B2B → LexSuiteONE). Aqui só o resumo e o atalho.",
    lic_abrir: "Abrir no RootifyONE ↗", lic_cod: "Código", lic_mod: "Modalidade", lic_val: "Validade", lic_pc: "Computadores",
    sit: { novo: "Novo", analise: "Em análise", contato: "Contatado", cliente: "Virou cliente", descartado: "Descartado" } },
  en: {
    e_sub: "SolverONE team area. Only people on the team list can sign in.", e_email: "E-mail", e_senha: "Password", e_entrar: "Sign in",
    e_nota: "No Google sign-in: administration uses only password and the 6-digit phone code.",
    c_x: "First time: on your phone, open the authenticator app (Google Authenticator or Microsoft Authenticator), tap + and scan this square.",
    c_ou: "If scanning does not work, type this key in the app:", c_cod: "6-digit code shown in the app", c_ok: "Confirm",
    m_cod: "6-digit code from the authenticator app", m_ok: "Sign in", m_voltar: "Back",
    er_senha: "E-mail or password do not match.", er_cod: "Wrong or expired code. Check the app and type the current code.",
    er_equipe: "This account is not on the team list.", er_rede: "No answer from the cloud. Check the internet and try again.",
    er_mfa: "The phone code is not enabled in the cloud (Authentication → MFA). Tell the Architecture session.", tranc: "Locked for inactivity. Sign in again.",
    demo: "Demo: this tab still shows fictitious data. Its cloud part was requested from the Architecture session (phase 1).",
    real: "Real data, read now from the cloud.", lic_ativas: "active", lic_pausada: "paused", carregando: "Loading…",
    proto: "Prototype with FICTITIOUS data · nothing here is real and nothing leaves this file",
    sair: "Sign out", prod: "RADAR JUDICIAL",
    a_geral: "Overview", a_diarios: "Gazette health", a_inst: "Firms and computers", a_leit: "Firm readings",
    a_erros: "Errors", a_est: "Statistics", a_lic: "Licences",
    g_t: "How things are right now", g_s: "Updated at 15:30 (Brasília time). Each card opens the detail.",
    k_trib: "CNJ gazettes", k_trib_d: "{f} down · {l} slow", k_inst: "Active computers", k_inst_d: "{n} not checked in 3 days",
    k_ver: "On current version", k_ver_d: "{n} on old version", k_err: "Errors in 24 h", k_err_d: "{n} computers",
    k_proc: "New cases today", k_proc_d: "sum of all firms", k_lic: "Licences", k_lic_d: "{a} active · {t} trial",
    d_t: "Gazette health (CNJ)", d_s: "Every 15 minutes, the SolverONE cloud asks the CNJ for each court's gazette record (a light request, without downloading the gazette). Green: answered; yellow: answered slowly; red: error or no answer.",
    d_hoje: "Today's gazette", d_pub: "published", d_nao: "not yet", d_resp: "response", d_ult: "checked at {h}",
    d_hist: "Last 24 hours (all courts)", d_hist_s: "Each bar is one check; the height is how many courts answered well.",
    i_t: "Firms and computers", i_s: "Each computer with the program, its version and the last time it checked the licence.",
    i_esc: "Firm", i_pc: "Computer", i_ver: "Version", i_ult: "Last check", i_sit: "Status", i_ok: "up to date", i_velha: "old version", i_parado: "idle for {d} days",
    l_t: "Firm readings", l_s: "What each program reading achieved, per court (counts only: read, CNJ down, error).",
    l_falta: "Missing to exist: the program does not send this summary yet. It needs a new RADAR version and a review of what goes to SolverONE (terms, section on data sent). Question to the owner on the board.",
    e_t: "Errors", e_s: "What the installer and the program sent (no folder paths, no personal data).",
    e_quando: "When", e_orig: "Source", e_etapa: "Step", e_msg: "Message", e_ver: "Version",
    s_t: "Statistics", s_s: "Only counts the firms send (per day, court, practice and status). No company names, no case numbers.",
    s_dia: "New cases per day (all firms, 30 days)", s_trib: "By court (30 days)", s_sit: "By status (30 days)",
    lic_t: "Licences", lic_s: "Registration, activate/pause, e-mails and terms stay in RootifyONE (B2B → LexSuiteONE). Here, only the summary and the shortcut.",
    lic_abrir: "Open in RootifyONE ↗", lic_cod: "Code", lic_mod: "Plan", lic_val: "Valid until", lic_pc: "Computers",
    sit: { novo: "New", analise: "Under review", contato: "Contacted", cliente: "Became client", descartado: "Discarded" } }
};
function t(k, v) { var s = (T[lang][k] != null ? T[lang][k] : T.pt[k]); if (s == null) s = k; Object.keys(v || {}).forEach(function (x) { s = s.split("{" + x + "}").join(v[x]); }); return s; }
function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
function $(id) { return document.getElementById(id); }
function num(n) { return Number(n || 0).toLocaleString(lang === "en" ? "en-US" : "pt-BR"); }

/* ---------- nuvem (Supabase por REST, sem biblioteca) ---------- */
var CHAVE_SESSAO = "central-lexsuiteone.sessao";
var sessao = null; try { sessao = JSON.parse(sessionStorage.getItem(CHAVE_SESSAO) || "null"); } catch (e) { sessao = null; }
function guardarSessao(s) { sessao = s; try { if (s) sessionStorage.setItem(CHAVE_SESSAO, JSON.stringify(s)); else sessionStorage.removeItem(CHAVE_SESSAO); } catch (e) {} }
function pedir(caminho, corpo, metodo) {
  var h = { "apikey": CFG.chavePublica, "Content-Type": "application/json" };
  if (sessao && sessao.access_token) h.Authorization = "Bearer " + sessao.access_token;
  return fetch(CFG.supabase + caminho, { method: metodo || (corpo ? "POST" : "GET"), headers: h, body: corpo ? JSON.stringify(corpo) : undefined, credentials: "omit", referrerPolicy: "no-referrer" })
    .then(function (r) { return r.text().then(function (x) { var j = null; try { j = x ? JSON.parse(x) : null; } catch (e) { j = { texto: x }; } if (!r.ok) { var e = new Error((j && (j.msg || j.message || j.error_description || j.error)) || ("HTTP " + r.status)); e.status = r.status; e.corpo = j; throw e; } return j; }); });
}
function novaSessao(j) { return { access_token: j.access_token, refresh_token: j.refresh_token, expira: Date.now() + (Number(j.expires_in) || 3600) * 1000, email: j.user && j.user.email }; }
function renovarSePreciso() {
  if (!sessao || !sessao.refresh_token || sessao.expira - Date.now() > 120000) return Promise.resolve();
  return pedir("/auth/v1/token?grant_type=refresh_token", { refresh_token: sessao.refresh_token }).then(function (j) { var s = novaSessao(j); s.aal2 = sessao.aal2; guardarSessao(s); });
}
function rpc(nome, args) { return renovarSePreciso().then(function () { return pedir("/rest/v1/rpc/" + nome, args || {}); }); }

/* ---------- entrada: senha, depois código do celular ---------- */
var fator = null;
function erro(k) { $("e-erro").textContent = k ? t(k) : ""; }
function mostrarPasso(id) { ["p-senha", "p-cadastrar", "p-codigo"].forEach(function (p) { $(p).hidden = p !== id; }); var f = $(id).querySelector("input"); if (f) f.focus(); }
function ocupado(on) { $("entrada").classList.toggle("carregando", !!on); }
$("p-senha").addEventListener("submit", function (ev) {
  ev.preventDefault(); erro(""); ocupado(true);
  pedir("/auth/v1/token?grant_type=password", { email: $("e-email").value.trim(), password: $("e-senha").value })
    .then(function (j) { $("e-senha").value = ""; guardarSessao(novaSessao(j)); return pedir("/auth/v1/user"); })
    .then(function (u) {
      var ok = (u.factors || []).filter(function (f) { return f.factor_type === "totp" && f.status === "verified"; });
      if (ok.length) { fator = ok[0].id; mostrarPasso("p-codigo"); return; }
      return pedir("/auth/v1/factors", { factor_type: "totp", friendly_name: "Central LexSuiteONE " + new Date().toISOString().slice(0, 16) }).then(function (f) {
        fator = f.id; $("c-qr").src = f.totp.qr_code; $("c-segredo").textContent = f.totp.secret; mostrarPasso("p-cadastrar");
      });
    })
    .catch(function (e) { guardarSessao(null); erro(e.status === 400 ? "er_senha" : e.status === 422 || e.status === 403 ? "er_mfa" : "er_rede"); })
    .then(function () { ocupado(false); });
});
function confirmarCodigo(campo) {
  erro(""); ocupado(true);
  var cod = $(campo).value.replace(/\D/g, "");
  return pedir("/auth/v1/factors/" + fator + "/challenge", {})
    .then(function (c) { return pedir("/auth/v1/factors/" + fator + "/verify", { challenge_id: c.id, code: cod }); })
    .then(function (j) { var s = novaSessao(j); s.aal2 = true; s.email = s.email || (sessao && sessao.email); guardarSessao(s); $(campo).value = ""; return rpc("eh_equipe"); })
    .then(function (eq) { if (eq !== true) { sair(); erro("er_equipe"); return; } abrirApp(); })
    .catch(function (e) { erro(e.status === 422 || e.status === 400 ? "er_cod" : "er_rede"); })
    .then(function () { ocupado(false); });
}
$("p-cadastrar").addEventListener("submit", function (ev) { ev.preventDefault(); confirmarCodigo("c-cod"); });
$("p-codigo").addEventListener("submit", function (ev) { ev.preventDefault(); confirmarCodigo("m-cod"); });
$("m-voltar").addEventListener("click", function () { sair(); });
function sair(motivo) {
  var tok = sessao && sessao.access_token;
  if (tok) pedir("/auth/v1/logout?scope=local", {}).catch(function () {});
  guardarSessao(null); $("app").hidden = true; $("entrada").hidden = false; mostrarPasso("p-senha"); erro(motivo || "");
}
/* trava por inatividade */
var ultimoUso = Date.now();
["pointerdown", "keydown", "scroll"].forEach(function (ev) { window.addEventListener(ev, function () { ultimoUso = Date.now(); }, { passive: true }); });
setInterval(function () { if (sessao && Date.now() - ultimoUso > (CFG.inatividadeMin || 15) * 60000) sair("tranc"); }, 30000);

/* ---------- dados ---------- */
var DADOS = { licencas: null, central: null };
/* ---------- dados FICTÍCIOS (sorteio fixo, sempre igual) ---------- */
var semente = 7; function rnd() { semente = (semente * 9301 + 49297) % 233280; return semente / 233280; }
var TRTS = []; for (var n = 1; n <= 24; n++) TRTS.push("TRT" + n);
var DIARIOS = TRTS.map(function (s, i) {
  var est = i === 8 ? "fora" : (i === 3 || i === 16) ? "lento" : "ok";
  return { trib: s, est: est, ms: est === "ok" ? 300 + Math.round(rnd() * 900) : est === "lento" ? 6000 + Math.round(rnd() * 4000) : null,
           hoje: est !== "fora" && rnd() > .35, hora: "15:" + (15 + Math.round(rnd() * 14)) };
});
var HIST24 = []; for (var h = 0; h < 96; h++) HIST24.push(h > 52 && h < 60 ? 14 + Math.round(rnd() * 6) : 22 + Math.round(rnd() * 2));
var ESC = ["Escritório Fictício A", "Escritório Fictício B", "Escritório Fictício C (teste)"];
var INST = [
  { esc: ESC[0], pc: "PC-RECEPCAO", ver: "0.7.45", dias: 0, hora: "15:12" }, { esc: ESC[0], pc: "NOTEBOOK-1", ver: "0.7.44", dias: 1, hora: "08:03" },
  { esc: ESC[1], pc: "ESTACAO-02", ver: "0.7.45", dias: 0, hora: "14:58" }, { esc: ESC[1], pc: "ESTACAO-05", ver: "0.7.40", dias: 4, hora: "20:01" },
  { esc: ESC[2], pc: "DESKTOP-XYZ", ver: "0.7.45", dias: 0, hora: "15:20" }, { esc: ESC[2], pc: "LAPTOP-ABC", ver: "0.7.41", dias: 9, hora: "10:13" } ];
var ERROS = [
  { q: "13/11 14:54", o: "programa", e: "leitura", m: "CNJ respondeu 500 no Diário de hoje (TRT9)", v: "0.7.42" },
  { q: "13/11 13:10", o: "instalador", e: "descompactar", m: "errorlevel=1 tar e powershell", v: "0.7.43" },
  { q: "13/11 11:47", o: "programa", e: "agendar", m: "Acesso negado ao criar a tarefa do Windows", v: "0.7.44" },
  { q: "12/11 20:05", o: "programa", e: "planilha", m: "Planilha aberta no Excel; gravada depois", v: "0.7.39" } ];
var DIAS30 = []; for (var d = 0; d < 30; d++) DIAS30.push((d % 7 === 5 || d % 7 === 6) ? 200 + Math.round(rnd() * 300) : 1100 + Math.round(rnd() * 900));
var POR_TRIB = [["TRT2", 14230], ["TRT15", 9870], ["TRT9", 5120], ["TRT1", 4300], ["TRT3", 3980], ["TRT4", 2750]];
var POR_SIT = [["novo", 31200], ["analise", 4100], ["contato", 1300], ["cliente", 210], ["descartado", 2900]];
var LIC = [{ c: "LEX-AAAA-••••", e: ESC[0], m: "Mensal", v: "13/Dez/2026", p: "2 de 3" }, { c: "LEX-BBBB-••••", e: ESC[1], m: "Anual", v: "01/Nov/2027", p: "2 de 5" },
           { c: "LEX-CCCC-••••", e: ESC[2], m: "Teste", v: "27/Nov/2026", p: "2 de 2" }];

function carregarDados() {
  return Promise.all([
    rpc("admin_lex_listar").then(function (l) { DADOS.licencas = l || []; }).catch(function () { DADOS.licencas = null; }),
    rpc("admin_lex_central").then(function (c) { DADOS.central = c || null; }).catch(function () { DADOS.central = null; })  // fase 1 (Arquitetura)
  ]).then(function () {
    if (DADOS.licencas) LIC = DADOS.licencas.map(function (c) {
      return { c: String(c.codigo || "").slice(0, 9) + "••••", e: c.escritorio || "—", m: c.modalidade || (c.teste ? "Teste" : "—"), v: c.validade || "—",
               p: num(c.computadores_ativos) + " / " + (c.max_computadores || "∞"), ativo: c.ativo, teste: c.teste, erros: c.erros_7d || 0, ultima: c.ultima_vez };
    });
    var C = DADOS.central;
    if (C) {  // formato combinado com a Arquitetura (desenho, seção 2); o que não vier fica com a demonstração
      if (C.diarios) DIARIOS = C.diarios; if (C.hist24) HIST24 = C.hist24; if (C.instalacoes) INST = C.instalacoes;
      if (C.erros) ERROS = C.erros; if (C.dias30) DIAS30 = C.dias30; if (C.por_trib) POR_TRIB = C.por_trib; if (C.por_sit) POR_SIT = C.por_sit;
    }
  });
}
function selo(m, real) { m.appendChild(el("div", real ? "nota" : "demo", t(real ? "real" : "demo"))); }
/* ---------- telas ---------- */
var ABAS = ["geral", "diarios", "inst", "leit", "erros", "est", "lic"], aba = "geral";
var REAL = { lic: function () { return !!DADOS.licencas; }, geral: function () { return !!DADOS.central; }, diarios: function () { return !!(DADOS.central && DADOS.central.diarios); }, inst: function () { return !!(DADOS.central && DADOS.central.instalacoes); }, erros: function () { return !!(DADOS.central && DADOS.central.erros); }, est: function () { return !!(DADOS.central && DADOS.central.dias30); }, leit: function () { return false; } };
function titulo(m, k, s) { m.appendChild(el("h2", null, t(k))); m.appendChild(el("p", "sub", t(s))); if (aba !== "leit") selo(m, REAL[aba]()); }
function kpi(rot, v, det, cls, destino) { var b = el("button", "kpi" + (cls ? " " + cls : "")); b.type = "button";
  b.appendChild(el("div", "r", rot)); b.appendChild(el("div", "v", v)); b.appendChild(el("div", "d", det)); b.onclick = function () { ir(destino); }; return b; }
var TELAS = {
  geral: function (m) {
    titulo(m, "g_t", "g_s");
    var k = el("div", "kpis"), fora = DIARIOS.filter(function (x) { return x.est === "fora"; }).length, lento = DIARIOS.filter(function (x) { return x.est === "lento"; }).length;
    k.appendChild(kpi(t("k_trib"), (24 - fora) + "/24", t("k_trib_d", { f: fora, l: lento }), fora ? "alerta" : lento ? "atencao" : "", "diarios"));
    k.appendChild(kpi(t("k_inst"), INST.length, t("k_inst_d", { n: INST.filter(function (x) { return x.dias >= 3; }).length }), "", "inst"));
    var velhas = INST.filter(function (x) { return x.ver !== "0.7.45"; }).length;
    k.appendChild(kpi(t("k_ver"), (INST.length - velhas) + "/" + INST.length, t("k_ver_d", { n: velhas }), velhas ? "atencao" : "", "inst"));
    k.appendChild(kpi(t("k_err"), 3, t("k_err_d", { n: 3 }), "atencao", "erros"));
    k.appendChild(kpi(t("k_proc"), num(DIAS30[29]), t("k_proc_d"), "", "est"));
    k.appendChild(kpi(t("k_lic"), LIC.length, t("k_lic_d", { a: LIC.filter(function (x) { return x.ativo !== false; }).length, t: LIC.filter(function (x) { return x.teste; }).length }), "", "lic"));
    m.appendChild(k);
    var g = el("div", "grade2"); var c1 = el("div", "cartao"); c1.appendChild(el("h3", null, t("a_diarios"))); c1.appendChild(gradeTrts(true)); g.appendChild(c1);
    var c2 = el("div", "cartao"); c2.appendChild(el("h3", null, t("s_dia"))); c2.appendChild(barras(DIAS30)); g.appendChild(c2); m.appendChild(g);
  },
  diarios: function (m) {
    titulo(m, "d_t", "d_s"); var c = el("div", "cartao"); c.appendChild(gradeTrts(false)); m.appendChild(c);
    var h = el("div", "cartao"); h.appendChild(el("h3", null, t("d_hist"))); h.appendChild(el("p", "nota", t("d_hist_s"))); h.appendChild(barras(HIST24, 24)); m.appendChild(h);
  },
  inst: function (m) {
    titulo(m, "i_t", "i_s");
    tabela(m, [t("i_esc"), t("i_pc"), t("i_ver"), t("i_ult"), t("i_sit")], INST.map(function (x) {
      var sit = x.dias >= 3 ? ["fora", t("i_parado", { d: x.dias })] : x.ver !== "0.7.45" ? ["lento", t("i_velha")] : ["ok", t("i_ok")];
      return [x.esc, x.pc, x.ver, (x.dias ? x.dias + "d · " : "") + x.hora, { selo: sit }];
    }));
  },
  leit: function (m) { titulo(m, "l_t", "l_s"); m.appendChild(el("div", "falta", t("l_falta"))); },
  erros: function (m) { titulo(m, "e_t", "e_s"); tabela(m, [t("e_quando"), t("e_orig"), t("e_etapa"), t("e_msg"), t("e_ver")], ERROS.map(function (x) { return [x.q, x.o, x.e, x.m, x.v]; })); },
  est: function (m) {
    titulo(m, "s_t", "s_s"); var c = el("div", "cartao"); c.appendChild(el("h3", null, t("s_dia"))); c.appendChild(barras(DIAS30)); m.appendChild(c);
    var g = el("div", "grade2"); g.appendChild(listaBarras(t("s_trib"), POR_TRIB)); g.appendChild(listaBarras(t("s_sit"), POR_SIT.map(function (x) { return [T[lang].sit[x[0]], x[1]]; }))); m.appendChild(g);
  },
  lic: function (m) {
    titulo(m, "lic_t", "lic_s");
    tabela(m, [t("lic_cod"), t("i_esc"), t("lic_mod"), t("lic_val"), t("lic_pc")], LIC.map(function (x) { return [x.c, x.e, x.m, x.v, x.p]; }));
    var b = el("button", "kpi", t("lic_abrir")); b.type = "button"; b.style.width = "auto"; b.onclick = function () { window.open(CFG.rootify, "_blank", "noopener"); }; m.appendChild(b);
  }
};
function gradeTrts(resumo) {
  var g = el("div", "trts");
  DIARIOS.forEach(function (x) {
    var b = el("button", "trt " + x.est); b.type = "button"; b.onclick = function () { ir("diarios"); };
    b.appendChild(el("b", null, x.trib)); b.appendChild(el("span", "selo " + x.est, x.est === "ok" ? "ok" : x.est === "lento" ? (lang === "en" ? "slow" : "lento") : (lang === "en" ? "down" : "fora")));
    if (!resumo) {
      b.appendChild(el("small", null, " " + t("d_resp") + ": " + (x.ms ? (x.ms / 1000).toFixed(1) + " s" : "—")));
      b.appendChild(el("small", null, " · " + t("d_hoje") + ": " + (x.hoje ? t("d_pub") : t("d_nao"))));
      b.appendChild(el("small", null, " · " + t("d_ult", { h: x.hora })));
    }
    g.appendChild(b);
  });
  return g;
}
function barras(v, max) { var w = el("div"), b = el("div", "barras"), mx = max || Math.max.apply(null, v);
  v.forEach(function (x) { var i = el("i"); i.style.height = Math.max(2, Math.round(x / mx * 100)) + "%"; i.title = num(x); b.appendChild(i); });
  w.appendChild(b); var l = el("div", "leg"); l.appendChild(el("span", null, lang === "en" ? "oldest" : "mais antigo")); l.appendChild(el("span", null, lang === "en" ? "now" : "agora")); w.appendChild(l); return w; }
function listaBarras(tit, linhas) { var c = el("div", "cartao"); c.appendChild(el("h3", null, tit)); var mx = Math.max.apply(null, linhas.map(function (x) { return x[1]; }));
  linhas.forEach(function (x) { var r = el("div", "linha-b"); r.appendChild(el("span", null, x[0])); var tr = el("div", "t"), i = el("i"); i.style.width = Math.round(x[1] / mx * 100) + "%"; tr.appendChild(i); r.appendChild(tr); r.appendChild(el("span", null, num(x[1]))); c.appendChild(r); });
  return c; }
function tabela(m, cab, linhas) { var c = el("div", "cartao rolagem"), tb = el("table"), tr = el("tr");
  cab.forEach(function (h) { tr.appendChild(el("th", null, h)); }); tb.appendChild(tr);
  linhas.forEach(function (l) { var r = el("tr"); l.forEach(function (v) { var td = el("td"); if (v && v.selo) td.appendChild(el("span", "selo " + v.selo[0], v.selo[1])); else td.textContent = v; r.appendChild(td); }); tb.appendChild(r); });
  c.appendChild(tb); m.appendChild(c); }
function desenharAbas() { var n = $("abas"); n.textContent = "";
  ABAS.forEach(function (a) { var b = el("button", null, t("a_" + a)); b.type = "button"; b.setAttribute("role", "tab"); b.setAttribute("aria-selected", String(a === aba)); b.onclick = function () { ir(a); }; n.appendChild(b); }); }
function ir(a) { aba = a; desenharAbas(); var m = $("tela"); m.textContent = ""; TELAS[a](m); window.scrollTo(0, 0); }
function textos() {
  document.documentElement.lang = lang === "en" ? "en" : "pt-BR";
  [["e-sub", "e_sub"], ["e-l-email", "e_email"], ["e-l-senha", "e_senha"], ["e-entrar", "e_entrar"], ["e-nota", "e_nota"], ["c-x", "c_x"], ["c-ou", "c_ou"],
   ["c-l-cod", "c_cod"], ["c-ok", "c_ok"], ["m-l-cod", "m_cod"], ["m-ok", "m_ok"], ["m-voltar", "m_voltar"], ["b-sair", "sair"]].forEach(function (p) { $(p[0]).textContent = t(p[1]); });
  $("h-prod").textContent = "› " + t("prod"); $("e-idioma").textContent = lang === "en" ? "PT" : "EN";
  $("b-pt").setAttribute("aria-pressed", String(lang === "pt")); $("b-en").setAttribute("aria-pressed", String(lang === "en"));
  if (!$("app").hidden) ir(aba);
}
function abrirApp() {
  $("entrada").hidden = true; $("app").hidden = false; $("tela").textContent = t("carregando");
  carregarDados().then(function () { ir("geral"); });
}
function trocarIdioma(l) { lang = l; try { localStorage.setItem("central-lexsuiteone.idioma", l); } catch (e) {} textos(); }
$("b-pt").onclick = function () { trocarIdioma("pt"); }; $("b-en").onclick = function () { trocarIdioma("en"); };
$("e-idioma").onclick = function () { trocarIdioma(lang === "en" ? "pt" : "en"); };
$("b-sair").onclick = function () { sair(); };
$("b-tema").onclick = function () { var r = document.documentElement; r.dataset.tema = r.dataset.tema === "escuro" ? "claro" : "escuro"; try { localStorage.setItem("central-lexsuiteone.tema", r.dataset.tema); } catch (e) {} };
(function () {
  var tm = null; try { tm = localStorage.getItem("central-lexsuiteone.tema"); lang = localStorage.getItem("central-lexsuiteone.idioma") || lang; } catch (e) {}
  document.documentElement.dataset.tema = tm || (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "escuro" : "claro");
  textos();
  if (sessao && sessao.aal2) { renovarSePreciso().then(function () { return rpc("eh_equipe"); }).then(function (eq) { if (eq === true) abrirApp(); else sair(); }).catch(function () { sair(); }); }
  else { guardarSessao(null); mostrarPasso("p-senha"); }
  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(function () {});
})();
