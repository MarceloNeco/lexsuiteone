/* Roteiro de tela do aviso de planilha em uso, da lupa offline e do /dados com Infinity e NaN (revisão da 0.7.27). Dados FICTÍCIOS.
   Não rode direto: use aviso_e_lupa.sh, que sobe os servidores e passa as portas. Se um texto de planilha_em_uso, planilha_em_uso_sem_excel
   ou da lupa mudar em radar_modelo.html, atualize as expressões PT_LEIT/EN_LEIT/PT_SEM/EN_SEM abaixo. */
const { chromium } = require('playwright');
const [pOk, pUso, pSem, pMarca, pMarcaSem, OUT, arquivo, pInf, pLegit, pFic] = process.argv.slice(2);
const falhas = []; let nv = 0; const ok = (c, m) => { nv++; if (!c) { falhas.push(m); console.log('  X ' + m); } else console.log('  ok ' + m); };
const externos = [];
(async () => {
  const b = await chromium.launch({ args: ['--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1'] });
  const VERSAO = (require('fs').readFileSync(require('path').join(__dirname, '..', '..', 'lexsuite', '__init__.py'), 'utf8').match(/VERSAO = "([^"]+)"/) || [])[1] || '';
  const novoContexto = b.newContext.bind(b);  // 0.7.31: "Novidades da versão" já vista
  b.newContext = async (o) => { const c = await novoContexto(o); await c.addInitScript((v) => { try { localStorage.setItem('lexsuite:novidades-vistas', v); } catch (e) {} }, VERSAO); return c; };
  const novoCtx = async (vp, mobile, idioma, so127 = true) => {
    const ctx = await b.newContext({ viewport: vp, isMobile: mobile, hasTouch: mobile, serviceWorkers: 'block' });
    ctx.on('request', r => { const u = new URL(r.url()); if (!(u.hostname === '127.0.0.1' || u.protocol === 'file:' || u.protocol === 'data:' || u.protocol === 'blob:' || u.protocol === 'about:')) externos.push(r.url()); });
    await ctx.addInitScript((idioma) => { try { if (!sessionStorage.getItem('__ini')) { localStorage.setItem('dgo:radar-judicial:pref:aone:ligado', 'false'); localStorage.setItem('lexsuite:idioma', idioma); sessionStorage.setItem('__ini', '1'); } } catch (e) {} }, idioma);
    return ctx;
  };
  for (const [nome, vp, mobile] of [['cel360', { width: 360, height: 740 }, true], ['nb1366', { width: 1366, height: 768 }, false]]) {
    for (const idioma of ['pt', 'en']) {
      console.log(`== ${nome} ${idioma}`);
      const novo = async (url) => {
        const ctx = await novoCtx(vp, mobile, idioma);
        const p = await ctx.newPage(); p.erros = []; p.on('pageerror', e => p.erros.push(e.message));
        await p.goto(url); await p.waitForTimeout(1500);
        if (await p.locator('#config').isVisible().catch(() => false)) { await p.click('#c-fechar'); await p.waitForTimeout(400); }
        return [ctx, p];
      };
      const abrir = async (p) => {
        await p.click('#b-menu'); await p.waitForTimeout(500);
        await p.locator('.gv-item', { hasText: idioma === 'pt' ? 'Abrir a planilha' : 'Open the spreadsheet' }).first().click(); await p.waitForTimeout(700);
        if (await p.locator('#janela[open]').count()) { await p.locator('#janela[open] button', { hasText: idioma === 'pt' ? 'Entendi, abrir' : 'Got it, open' }).click(); await p.waitForTimeout(900); }
      };
      const lerMsg = (p) => p.evaluate(() => { const es = [...document.querySelectorAll('#estado span.erro, #estado span.ok')]; const e = es[0]; if (!e) return null; const r = e.getBoundingClientRect();
        return { n: es.length, nErro: document.querySelectorAll('#estado span.erro').length, nId: document.querySelectorAll('#aviso-em-uso').length, id: e.id, cls: e.className, txt: e.textContent, vis: r.width > 0 && r.height > 0 && r.left >= 0 && r.right <= document.documentElement.clientWidth + 1, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }; });
      const PT_LEIT = /Pedi ao Excel para abrir só para leitura; feche a outra para o \S+ voltar a atualizá-la\./, EN_LEIT = /I asked Excel to open it read-only; close the other one so \S+ can update it again\./;
      const PT_SEM = /Abri a planilha do jeito normal; não salve nela e feche a outra para o \S+ voltar a atualizá-la\./, EN_SEM = /I opened it the normal way; do not save in it and close the other one so \S+ can update it again\./;
      // B3: 4 combinações (com Excel / sem Excel) x (marca RADAR / ZETA)
      for (const [rot, porta, curto, semExcel] of [['com Excel, RADAR', pUso, 'RADAR', false], ['sem Excel, RADAR', pSem, 'RADAR', true], ['com Excel, ZETA', pMarca, 'ZETA', false], ['sem Excel, ZETA', pMarcaSem, 'ZETA', true]]) {
        const [ctx2, p2] = await novo('http://127.0.0.1:' + porta + '/');
        const resp = []; p2.on('response', async r => { if (new URL(r.url()).pathname === '/abrir') { try { resp.push(await r.text()); } catch (e) {} } });
        await abrir(p2);
        const m1 = await lerMsg(p2);
        console.log(`  [${rot}] /abrir ->`, resp.join(' '), '\n    mensagem:', JSON.stringify(m1 && m1.txt));
        const j = resp.length ? JSON.parse(resp[0]) : {};
        ok(j.ok === true && j.em_uso === true, `${rot}: /abrir = ok + em_uso`);
        ok(semExcel ? !('so_leitura' in j) : j.so_leitura === true, `${rot}: so_leitura ${semExcel ? 'ausente' : 'true'}`);
        ok(m1 && m1.cls === 'erro' && m1.id === 'aviso-em-uso', `${rot}: aviso vermelho com id aviso-em-uso`);
        ok(m1 && (semExcel ? (idioma === 'pt' ? PT_SEM : EN_SEM) : (idioma === 'pt' ? PT_LEIT : EN_LEIT)).test(m1.txt), `${rot}: texto certo (${idioma})`);
        ok(m1 && (semExcel ? !/Pedi ao Excel|asked Excel/.test(m1.txt) : !/Abri a planilha do jeito normal|opened it the normal way/.test(m1.txt)), `${rot}: o outro texto NÃO aparece`);
        ok(m1 && !/\{[a-z]+\}/.test(m1.txt), `${rot}: nenhum "{c}" literal`);
        ok(m1 && m1.txt.includes(curto + (idioma === 'pt' ? ' voltar' : ' can')), `${rot}: nome curto da marca = "${curto}"`);
        if (curto === 'ZETA') ok(m1 && !/RADAR/.test(m1.txt), `${rot}: "RADAR" fixo não aparece`);
        ok(m1 && m1.vis && m1.sw <= m1.cw + 1, `${rot}: dentro da tela, sem transbordo (scrollWidth ${m1 && m1.sw} <= ${m1 && m1.cw})`);
        await p2.screenshot({ path: `${OUT}/${nome}-${idioma}-uso-${porta}.png` });
        if (curto === 'RADAR') {
          await p2.waitForTimeout(10500);
          const m2 = await lerMsg(p2);
          ok(m2 && m2.cls === 'erro' && m2.txt === m1.txt, `${rot}: o aviso vermelho continua depois de 10,5 s`);
        }
        // 2º e 3º clique: não empilham
        await abrir(p2); await p2.waitForTimeout(300); await abrir(p2); await p2.waitForTimeout(300);
        const m3 = await lerMsg(p2);
        ok(m3 && m3.nErro === 1 && m3.nId === 1, `${rot}: depois de 3 cliques há 1 aviso vermelho só (span.erro=${m3 && m3.nErro}, #aviso-em-uso=${m3 && m3.nId})`);
        ok(!p2.erros.length, `${rot}: sem erro de JS ${JSON.stringify(p2.erros.slice(0, 2))}`);
        await ctx2.close();
      }
      // verde normal some em ~8 s (e não acumula)
      {
        const [ctx3, p3] = await novo('http://127.0.0.1:' + pOk + '/');
        await abrir(p3); await p3.waitForTimeout(500); const v1 = await lerMsg(p3); console.log('  [verde] mensagem:', JSON.stringify(v1 && v1.txt));
        ok(v1 && v1.cls === 'ok' && v1.id === '', 'verde: aviso normal (classe ok, sem id aviso-em-uso)');
        await p3.waitForTimeout(8300); const v2 = await lerMsg(p3); ok(!v2 || v2.txt !== v1.txt, 'verde: some em ~8 s (restou: ' + JSON.stringify(v2 && v2.txt) + ')');
        ok(!p3.erros.length, 'verde: sem erro de JS'); await ctx3.close();
      }
      // M1 no app: a lupa vazia só orienta (0.7.36, dono); cada grupo aparece ao digitar e Enter abre o que deve
      {
        const [ctx4, p4] = await novo('http://127.0.0.1:' + pOk + '/');
        const lista = async () => p4.evaluate(() => [...document.querySelectorAll('#bg-res button')].map(x => x.firstChild.textContent.trim() + '|' + ((x.querySelector('small') || {}).textContent || '')));
        await p4.click('#b-busca'); await p4.waitForTimeout(300); const L = await lista();
        console.log('  [app] lupa vazia:', L.length, 'itens');
        ok(L.length === 0 && await p4.locator('#bg-res .bg-nada').isVisible(), 'app: lupa vazia mostra só a dica');
        const exp = idioma === 'pt' ? ['Painel', 'Lista', 'Arquivo', 'Histórico', 'planilha', 'Configurações', 'Perfil', 'área logada', 'Termos', 'Manual', 'Sair'] : ['Dashboard', 'List', 'Archive', 'History', 'spreadsheet', 'Settings', 'Profile', 'logged-in area', 'Terms', 'Manual', 'Exit'];
        for (const e of exp) { await p4.fill('#bg-q', e); await p4.waitForTimeout(200); const Le = await lista(); ok(Le.some(x => x.toLowerCase().includes(e.toLowerCase())), `app: "${e}" acha algo com "${e}"`); }
        await p4.fill('#bg-q', 'abri'); await p4.waitForTimeout(200); const La = await lista();
        ok(!La.some(x => /fabric/i.test(x)), 'app: "abri" não acha "Fabricadora" (começo de palavra)');
        for (const [q, cond] of [[idioma === 'pt' ? 'Arquivo' : 'Archive', async () => (await p4.getAttribute('#v-arquivo', 'aria-selected')) === 'true'],
                                 [idioma === 'pt' ? 'Histórico' : 'History', async () => { const r = await p4.evaluate(() => document.getElementById('config').classList.contains('ver-hist')); await p4.evaluate(() => { const b = document.getElementById('c-fechar'); if (b) b.click(); }); await p4.waitForTimeout(300); return r; }],
                                 [idioma === 'pt' ? 'Painel' : 'Dashboard', async () => (await p4.getAttribute('#v-painel', 'aria-selected')) === 'true'],
                                 [idioma === 'pt' ? 'Lista' : 'List', async () => (await p4.getAttribute('#v-lista', 'aria-selected')) === 'true']]) {
          if (await p4.locator('#busca-global').isHidden()) { await p4.click('#b-busca'); await p4.waitForTimeout(250); }
          await p4.fill('#bg-q', q); await p4.waitForTimeout(300); await p4.keyboard.press('Enter'); await p4.waitForTimeout(900);
          ok(await cond(), `app: Enter em "${q}" abre a tela certa`);
        }
        if (await p4.locator('#busca-global').isHidden()) { await p4.click('#b-busca'); await p4.waitForTimeout(250); }
        await p4.fill('#bg-q', idioma === 'pt' ? 'Perfil' : 'Profile'); await p4.waitForTimeout(300); await p4.keyboard.press('Enter'); await p4.waitForTimeout(900);
        const perfilAberto = await p4.evaluate(() => { const j = document.querySelector('#janela[open], #perfil-jan[open], dialog[open]'); const pf = document.getElementById('perfil'); return !!j || (pf && !pf.hidden && pf.getBoundingClientRect().height > 0) || !!document.querySelector('#config:not([hidden])'); });
        ok(perfilAberto, 'app: Enter em "Perfil" abre o perfil');
        ok(!p4.erros.length, 'app: sem erro de JS ' + JSON.stringify(p4.erros.slice(0, 2))); await ctx4.close();
      }
      // M2: a tela carrega com Infinity/NaN no config; e com valores legítimos
      for (const [rot, porta, esperaDias] of [['config com Infinity/NaN', pInf, '1'], ['config legítimo (1000.5, 3, 5000000)', pLegit, '3']]) {
        const [ctx5, p5] = await novo('http://127.0.0.1:' + porta + '/');
        await p5.click('#v-lista'); await p5.waitForTimeout(700);
        const est = await p5.evaluate(() => ({ estado: (document.getElementById('estado') || {}).innerText, versao: (document.getElementById('versao-topo') || {}).textContent, abas: [...document.querySelectorAll('[role=tab]')].filter(x => x.getBoundingClientRect().width).length, corpo: document.body.innerText.length, periodo: (document.getElementById('periodo') || {}).value, linhas: document.querySelectorAll('#lista .item').length, sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        console.log(`  [${rot}]`, JSON.stringify(est).slice(0, 300));
        ok(!/Não consegui falar|Could not reach/.test(est.estado || '') && !/Não consegui falar|Could not reach/.test(await p5.evaluate(() => document.body.innerText)), `${rot}: sem "Não consegui falar com o programa"`);
        ok(est.abas >= 3 && est.linhas > 0 && est.corpo > 200, `${rot}: a tela carregou (abas ${est.abas}, linhas ${est.linhas})`);
        ok(est.periodo === esperaDias, `${rot}: período mostrado = ${esperaDias} (veio ${est.periodo})`);
        ok(est.sw <= est.cw + 1, `${rot}: sem transbordo`);
        // abre a Configuração e fecha
        await p5.click('#b-config').catch(() => {}); await p5.waitForTimeout(700);
        const cfgAberta = await p5.locator('#config').isVisible().catch(() => false);
        ok(cfgAberta, `${rot}: Configuração abre`);
        ok(!p5.erros.length, `${rot}: sem erro de JS ${JSON.stringify(p5.erros.slice(0, 2))}`);
        if (porta === pInf) await p5.screenshot({ path: `${OUT}/${nome}-${idioma}-infinity.png` });
        await ctx5.close();
      }
    }
  }
  // M1 offline (file://)
  for (const [nome, vp] of [['cel360', { width: 360, height: 740 }], ['nb1366', { width: 1366, height: 768 }]]) for (const idioma of ['pt', 'en']) {
    console.log(`== offline ${nome} ${idioma}`);
    const ctx = await novoCtx(vp, false, idioma);
    const p = await ctx.newPage(); const erros = []; p.on('pageerror', e => erros.push(e.message));
    await p.goto('file://' + arquivo); await p.waitForTimeout(1500);
    console.log('  lupa visível:', await p.locator('#b-busca').isVisible(), '| menu ☰:', await p.locator('#b-menu').isVisible(), '| engrenagem:', await p.locator('#b-config').isVisible(), '| abas:', await p.evaluate(() => [...document.querySelectorAll('[role=tab]')].filter(x => x.getBoundingClientRect().width).map(x => x.id)));
    const lista = async () => p.evaluate(() => [...document.querySelectorAll('#bg-res button')].map(x => x.firstChild.textContent.trim() + '|' + ((x.querySelector('small') || {}).textContent || '')));
    await p.click('#b-busca'); await p.waitForTimeout(300);
    const L0 = await lista(); console.log('  lista vazia:', JSON.stringify(L0));
    const nomesVer = idioma === 'pt' ? ['Painel', 'Lista'] : ['Dashboard', 'List'], proibidos = idioma === 'pt' ? ['Arquivo', 'Histórico'] : ['Archive', 'History'];
    ok(L0.length === 0, 'offline: a lupa vazia só orienta (0.7.36, dono)');
    ok(!L0.some(x => proibidos.some(pr => x.startsWith(pr))), 'offline: nem Arquivo nem Histórico na lupa vazia');
    for (const q of (idioma === 'pt' ? ['Arquivo', 'Histórico', 'historico', 'arq', 'planilha', 'pasta', 'Configuração', 'Perfil', 'Colar', 'Termos', 'aba', 'cópia', 'Sair', 'Ver', 'Pa', 'Li'] : ['Archive', 'History', 'hist', 'arc', 'spreadsheet', 'folder', 'Settings', 'Profile', 'Paste', 'Terms', 'tab', 'copy', 'Quit', 'View', 'Da', 'Li'])) {
      await p.fill('#bg-q', q); await p.waitForTimeout(250); const L = await lista();
      console.log(`  "${q}" ->`, JSON.stringify(L).slice(0, 200));
      ok(!L.some(x => !nomesVer.some(n => x.startsWith(n + '|')) && !/^Nada encontrado|^Nothing found/.test(x) && !x.includes('·')), `offline: "${q}" não oferece nada fora de Painel/Lista (ações da lista à parte)`);
    }
    for (const n of nomesVer) {
      await p.fill('#bg-q', n); await p.waitForTimeout(250); const L = await lista();
      if (!L.length) { ok(false, `offline: "${n}" sem resultado`); continue; }
      await p.keyboard.press('Enter'); await p.waitForTimeout(700);
      const est = await p.evaluate(() => ({ busca: document.getElementById('busca-global').hidden, txt: document.body.innerText.length, graficos: document.getElementById('graficos').getBoundingClientRect().height, lista: document.getElementById('lista').getBoundingClientRect().height, sel: [...document.querySelectorAll('[role=tab][aria-selected=true]')].map(x => x.id), sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
      console.log(`  Enter em "${n}" ->`, JSON.stringify(est), 'erros JS:', erros.length);
      const quer = n === nomesVer[0] ? 'v-painel' : 'v-lista';
      ok(est.busca && est.txt > 40 && est.sw <= est.cw + 1 && est.sel.includes(quer) && (quer === 'v-painel' ? est.graficos > 50 : est.lista > 50), `offline: Enter em "${n}" abre ${quer} (aba selecionada ${est.sel}, sem transbordo)`);
      await p.screenshot({ path: `${OUT}/off-${nome}-${idioma}-${n}.png` });
      await p.click('#b-busca'); await p.waitForTimeout(200);
    }
    ok(!erros.length, 'offline: sem erro de JS ' + JSON.stringify(erros.slice(0, 3)));
    await ctx.close();
  }
  // INC: "Ler o Diário agora" no servidor fictício não lê o Diário
  {
    const ctx = await novoCtx({ width: 1366, height: 768 }, false, 'pt'); const p = await ctx.newPage(); const erros = []; p.on('pageerror', e => erros.push(e.message));
    const resp = []; p.on('response', async r => { const pt = new URL(r.url()).pathname; if (pt === '/rodar') { try { resp.push(await r.text()); } catch (e) {} } });
    await p.goto('http://127.0.0.1:' + pFic + '/'); await p.waitForTimeout(1500);
    await p.click('#b-rodar'); await p.waitForTimeout(3500);
    const txt = await p.evaluate(() => document.getElementById('estado').innerText + ' || ' + document.body.innerText.match(/Servidor de teste[^\n]*/));
    console.log('  [INC] /rodar ->', resp.join(' '), '| estado:', JSON.stringify(txt).slice(0, 300));
    ok(/Servidor de teste: leitura desligada \(dados fictícios\)/.test(txt), 'INC: a mensagem "Servidor de teste: leitura desligada (dados fictícios)" aparece');
    ok(!erros.length, 'INC: sem erro de JS ' + JSON.stringify(erros.slice(0, 2)));
    await ctx.close();
  }
  await b.close();
  ok(externos.length === 0, 'nenhum pedido fora de 127.0.0.1/file: ' + JSON.stringify(externos.slice(0, 5)));
  console.log(falhas.length ? `FALHOU (${falhas.length} de ${nv}):\n - ` + falhas.join('\n - ') : `TUDO OK (${nv} verificações)`);
  process.exitCode = falhas.length ? 1 : 0;
})();
