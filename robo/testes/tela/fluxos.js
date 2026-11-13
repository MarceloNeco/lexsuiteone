const { chromium } = require('playwright');
// 0.7.42 (dono: "tem que ter um regression"): o que o escritório faz todo dia, conferido na tela de verdade, com dados
// FICTÍCIOS e com a rede lenta de propósito (como numa máquina com dezenas de milhares de processos).
// Uso: PORTA=8781 python3 -B guarda_rede.py servidor_ficticio.py pronto &   e depois   node fluxos.js
// Termina com código 1 se qualquer conferência falhar. Cada falha diz o que a pessoa veria de errado.
const porta = process.env.PORTA || '8781';
const URL_ = 'http://127.0.0.1:' + porta + '/';
const res = []; let falhas = 0;
const confere = (ok, txt) => { res.push((ok ? 'OK    ' : 'FALHOU') + ' ' + txt); if (!ok) falhas++; };
const espera = ms => new Promise(r => setTimeout(r, ms));

async function abrirPagina(b, initScript) {
  const p = await b.newPage({ viewport: { width: 1366, height: 900 } });
  p._erros = []; p.on('pageerror', e => p._erros.push(String(e)));
  if (initScript) await p.addInitScript(initScript);
  await p.goto(URL_);
  await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 });
  await p.click('.dgo-aone-x').catch(() => {});
  await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); });
  return p;
}
const abrirConfig = p => p.evaluate(() => [...document.querySelectorAll('button,a')].find(x => /^(Configurações|Settings)$/.test(x.textContent.trim())).click());
const dias = p => p.evaluate(() => [...document.querySelectorAll('#c-dias button')].map(x => x.getAttribute('aria-pressed') === 'true' ? 1 : 0).join(''));
const totalLista = p => p.evaluate(() => { const m = document.getElementById('mais'); if (m && !m.hidden) return Number(document.getElementById('mais-txt').textContent.split(/ de | of /)[1].replace(/\D/g, '')); return document.querySelectorAll('#lista article.item').length; });

(async () => {
  const b = await chromium.launch();

  // 1. Configurações: salvar e reabrir na hora, com a lista ainda recarregando (bug de 13/Nov: voltava o de antes)
  {
    const p = await abrirPagina(b);
    await p.route('**/dados*', async r => { await espera(3000); r.continue(); });
    await p.route('**/config', async r => { if (r.request().method() === 'POST') await espera(1500); r.continue(); });
    await abrirConfig(p); await espera(600);
    const antes = await dias(p);
    await p.evaluate(() => { const bs = [...document.querySelectorAll('#c-dias button')]; bs[0].click(); bs[6].click(); });  // domingo e sábado
    const marcado = await dias(p);
    await p.evaluate(() => document.getElementById('c-salvar').click()); await espera(300);
    const st = await p.evaluate(() => ({ gira: document.getElementById('c-salvar').classList.contains('salvando'), off: document.getElementById('c-salvar').disabled, msg: document.getElementById('c-msg').textContent }));
    confere(st.gira && st.off && /Salvando|Saving/.test(st.msg), 'Configurações: enquanto salva, o botão Salvar gira e fica desligado ("' + st.msg + '")');
    await p.waitForFunction(() => document.getElementById('config').hidden, null, { timeout: 30000 });
    await abrirConfig(p); await espera(600);
    confere(await dias(p) === marcado, 'Configurações: reabrir logo depois de salvar mostra os dias salvos (' + marcado + ')');
    confere(await p.evaluate(() => document.getElementById('c-salvar').disabled), 'Configurações: reaberta sem mudança, o Salvar fica apagado');
    await p.evaluate(() => document.getElementById('c-cancelar').click()); await espera(4000);
    await abrirConfig(p); await espera(600);
    confere(await dias(p) === marcado, 'Configurações: depois de a lista recarregar, os dias salvos continuam');
    // volta como estava
    await p.unroute('**/dados*'); await p.unroute('**/config');
    if (antes !== marcado) { await p.evaluate(() => { const bs = [...document.querySelectorAll('#c-dias button')]; bs[0].click(); bs[6].click(); }); await p.evaluate(() => document.getElementById('c-salvar').click()); await p.waitForFunction(() => document.getElementById('config').hidden, null, { timeout: 30000 }); }
    const disco = await p.evaluate(() => fetch('/dados?dias=1', { headers: { 'X-LexSuite': '1' } }).then(r => r.json()).then(d => JSON.stringify(d.app.config.dias)));
    confere(disco !== undefined, 'Configurações: o programa devolve os dias gravados (' + disco + ')');
    // só o aviso muda: não manda pasta nem agendamento (cada um leva segundos no Windows)
    const posts = []; p.on('request', r => { if (r.method() === 'POST' && /\/config$/.test(r.url())) posts.push(JSON.parse(r.postData() || '{}')); });
    await abrirConfig(p); await espera(600);
    await p.evaluate(() => document.getElementById('c-avisar').click()); await espera(100);
    await p.evaluate(() => document.getElementById('c-salvar').click()); await p.waitForFunction(() => document.getElementById('config').hidden, null, { timeout: 30000 });
    const c1 = posts[posts.length - 1] || {};
    confere(!('pasta' in c1) && !('agendar' in c1) && !('dias' in c1) && 'avisar_ao_terminar' in c1, 'Configurações: mudar só o aviso não regrava a pasta nem o agendamento (' + Object.keys(c1).join(',') + ')');
    await abrirConfig(p); await espera(600);
    await p.evaluate(() => document.getElementById('c-avisar').click()); await p.evaluate(() => document.getElementById('c-salvar').click());
    await p.waitForFunction(() => document.getElementById('config').hidden, null, { timeout: 30000 });
    confere(p._erros.length === 0, 'Configurações: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 2. Busca da Lista: digitar não trava, 1 letra não filtra, sem acento acha com acento, apagar volta tudo
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); } catch (e) {} });
    await p.evaluate(() => document.getElementById('v-lista').click()); await espera(400);
    const tot = await totalLista(p);
    await p.click('#f-busca'); await p.keyboard.type('f', { delay: 40 }); await espera(600);
    confere(await totalLista(p) === tot, 'Busca: uma letra só não filtra (' + tot + ' processos)');
    await p.keyboard.type('icticia 23 ltda', { delay: 40 }); await espera(700);
    const n = await totalLista(p), nomes = await p.evaluate(() => [...document.querySelectorAll('#lista article.item')].map(x => x.textContent));
    confere(n >= 1 && n < tot && nomes.every(x => /Fict[ií]cia 23/i.test(x)), 'Busca: "ficticia 23 ltda" (sem acento) acha a "Empresa Fictícia 23 Ltda" (' + n + ')');
    confere(await p.evaluate(() => document.activeElement && document.activeElement.id === 'f-busca'), 'Busca: o cursor continua na caixa de busca');
    await p.fill('#f-busca', ''); await p.dispatchEvent('#f-busca', 'input'); await espera(400);
    confere(await totalLista(p) === tot, 'Busca: apagar o texto volta a lista inteira');
    confere(p._erros.length === 0, 'Busca: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 3. Período: duas trocas seguidas com a rede lenta; vale a última (a carga antiga não pode voltar)
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:ultimo-mes', '0'); } catch (e) {} });
    const ops = await p.evaluate(() => [...document.getElementById('periodo').options].map(o => o.value));
    const a = ops[0], z = ops[ops.length - 1];
    await p.route('**/dados*', async r => { const m = /dias=(\d+)/.exec(r.request().url()); await espera(m && m[1] === a ? 3000 : 400); r.continue(); });
    const troca = v => p.evaluate(v => { const s = document.getElementById('periodo'); s.value = v; s.dispatchEvent(new Event('change')); }, v);
    await troca(a); await espera(100); await troca(z); await espera(4500);
    const fim = await p.evaluate(() => ({ sel: document.getElementById('periodo').value, ocup: document.body.classList.contains('ocupado') }));
    confere(fim.sel === z && !fim.ocup, 'Período: trocar duas vezes seguidas fica no último escolhido (' + z + ' dias)');
    confere(p._erros.length === 0, 'Período: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 4. Painel e Lista: trocar de aba, riscar um item de um cartão e Limpar filtros
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:graf-tipo', 'pizza'); } catch (e) {} });
    await p.evaluate(() => document.getElementById('v-lista').click()); await espera(300);
    const tot = await totalLista(p);
    await p.evaluate(() => document.getElementById('v-painel').click()); await espera(500);
    const temCartoes = await p.evaluate(() => document.querySelectorAll('.grade-graf > .graf').length);
    confere(temCartoes > 3, 'Painel: abre com os cartões (' + temCartoes + ')');
    const riscou = await p.evaluate(() => { const c = [...document.querySelectorAll('.grade-graf > .graf')].find(x => x.querySelectorAll('.leg-item').length >= 2); if (!c) return false; window.__cartao = c.querySelector('h3').textContent; c.querySelectorAll('.leg-item')[0].click(); return true; });
    await espera(500);
    const riscos = () => p.evaluate(() => { const c = [...document.querySelectorAll('.grade-graf > .graf')].find(x => x.querySelector('h3').textContent === window.__cartao); return c ? c.querySelectorAll('.desligada').length : -1; });
    confere(riscou && await riscos(p) > 0, 'Painel: clicar num item da legenda risca esse item');
    await p.evaluate(() => document.getElementById('b-limpar-filtros').click()); await espera(600);
    confere(await riscos(p) === 0, 'Limpar filtros (no Painel): desfaz os riscos dos cartões');
    await p.evaluate(() => document.getElementById('v-lista').click()); await espera(400);
    confere(await totalLista(p) === tot, 'Lista: continua com todos os processos (' + tot + ')');
    confere(p._erros.length === 0, 'Painel e Lista: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(res.join('\n'));
  console.log(falhas ? `\n${falhas} FALHA(S)` : '\nTUDO OK');
  process.exit(falhas ? 1 : 0);
})().catch(e => { console.log(res.join('\n')); console.log('ERRO NO ROTEIRO:', e.message); process.exit(1); });
