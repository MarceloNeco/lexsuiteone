/* Teste permanente de uso da tela (regra do dono, 09/Nov): a cada versão, a tela é aberta em 4 larguras e falha se
   sobrar faixa vazia nas laterais, se algo sair da tela ou se o texto de um cartão cortar. Também grava os prints
   para o dono aprovar antes de publicar. Dados fictícios.
   Uso: (cd robo/testes/tela && PORTA=8781 python servidor_ficticio.py pronto &) ; node larguras.js 8781 pasta-dos-prints */
const { chromium, devices } = require('playwright');
const [porta, OUT] = [process.argv[2] || '8781', process.argv[3] || '.'];
(async () => {
  const b = await chromium.launch(); const falhas = []; let n = 0;
  // 0.7.31: a janela "Novidades da versão" já vista (senão ela abre por cima e o roteiro não clica em nada)
  const VERSAO = (require('fs').readFileSync(require('path').join(__dirname, '..', '..', 'lexsuite', '__init__.py'), 'utf8').match(/VERSAO = "([^"]+)"/) || [])[1] || '';
  const novoContexto = b.newContext.bind(b);
  b.newContext = async (o) => { const c = await novoContexto(o); await c.addInitScript((v) => { try { localStorage.setItem('lexsuite:novidades-vistas', v); } catch (e) {} }, VERSAO); return c; };
  const ok = (c, m) => { n++; if (!c) falhas.push(m); else console.log('  ✓ ' + m); };
  const tamanhos = [['celular', null], ['tablet', [768, 1024]], ['notebook', [1366, 768]], ['monitor', [1920, 1080]], ['monitor-grande', [2560, 1440]]];  // 0.7.29: + 768 px
  for (const [nome, vp] of tamanhos) {
    const ctx = vp ? await b.newContext({ viewport: { width: vp[0], height: vp[1] } }) : await b.newContext(devices['iPhone 14']);
    const p = await ctx.newPage(); const erros = []; p.on('pageerror', e => erros.push(e.message));
    await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1500);
    for (const aba of ['painel', 'lista']) {
      await p.click('#v-' + aba); await p.waitForTimeout(700);
      const r = await p.evaluate((aba) => {
        const W = document.documentElement.clientWidth, alvo = document.getElementById(aba === 'painel' ? 'graficos' : 'lista').getBoundingClientRect();
        const cortados = [...document.querySelectorAll('#lista .item .nome, #lista .item .meta, #lista .item .valor')].filter(e => e.scrollWidth > e.clientWidth + 1).length;
        return { lateral: Math.max(alvo.left, W - alvo.right) / W, vazaLado: document.documentElement.scrollWidth > W + 1, cortados };
      }, aba);
      ok(!r.vazaLado, `${nome}/${aba}: nada sai da tela para o lado`);
      ok(r.lateral < 0.06, `${nome}/${aba}: usa a largura toda (sobra lateral ${(r.lateral * 100).toFixed(1)}%)`);
      ok(r.cortados === 0, `${nome}/${aba}: texto dos cartões sem corte (${r.cortados})`);
      await p.screenshot({ path: `${OUT}/${nome}-${aba}.png`, fullPage: false });
    }
    // 0.7.30 (dono): os gráficos de baixo também em pizza; legenda visível e nada sai da tela
    await p.click('#v-painel'); await p.waitForTimeout(500);
    const bp = await p.$('.graf-tipo button:nth-of-type(2)'); if (bp) { await bp.click(); await p.waitForTimeout(700); }
    const z = await p.evaluate(() => {
      const W = document.documentElement.clientWidth, cards = [...document.querySelectorAll('.graf-pizza')];
      const fora = cards.filter(c => { const r = c.getBoundingClientRect(); return [...c.querySelectorAll('.legenda, .anel')].some(x => { const q = x.getBoundingClientRect(); return q.right > r.right + 1 || q.left < r.left - 1; }); }).length;
      const semLeg = cards.filter(c => !c.querySelector('.legenda li') && !c.querySelector('.nota-g')).length;
      return { n: cards.length, fora, semLeg, vaza: document.documentElement.scrollWidth > W + 1 };
    });
    ok(z.n >= 4, `${nome}/pizza: gráficos em pizza (${z.n})`);
    ok(!z.vaza && !z.fora, `${nome}/pizza: legenda e anel dentro do cartão, nada sai da tela`);
    ok(!z.semLeg, `${nome}/pizza: legenda visível em todos`);
    await p.screenshot({ path: `${OUT}/${nome}-painel-pizza.png`, fullPage: false });
    await p.evaluate(() => localStorage.removeItem('lexsuite:graf-tipo'));
    ok(!erros.length, `${nome}: sem erro na página ${erros.slice(0, 2).join(' | ')}`);
    await ctx.close();
  }
  // revisão da 0.7.30 (Operação): celular com "Mais filtros" aberto (o estado fica salvo) não pode ganhar rolagem lateral
  for (const lang of ['pt', 'en']) for (const w of [360, 390, 480, 560, 640]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 760 }, isMobile: true, hasTouch: true });
    await ctx.addInitScript((l) => { try { localStorage.setItem('lexsuite:mais-filtros', '1'); localStorage.setItem('lexsuite:idioma', l); } catch (e) {} }, lang);
    const p = await ctx.newPage(); await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300);
    for (const aba of ['lista', 'painel']) {
      await p.click('#v-' + aba); await p.waitForTimeout(500);
      const r = await p.evaluate(() => ({ aberto: !document.getElementById('filtros-avancados').hidden, sw: document.documentElement.scrollWidth, W: document.documentElement.clientWidth }));
      ok(r.aberto && r.sw <= r.W + 1, `${w}px ${lang}/${aba} com "Mais filtros" aberto: nada sai da tela (${r.sw} de ${r.W})`);
    }
    await ctx.close();
  }
  // revisão da 0.7.30 (Operação): no modo escuro, todo item do menu ☰ legível (contraste de pelo menos 4,5:1)
  for (const [nome, vp] of [['notebook', { viewport: { width: 1366, height: 768 } }], ['celular', devices['iPhone 14']]]) {
    const ctx = await b.newContext(Object.assign({ colorScheme: 'dark' }, vp));  // "Igual ao sistema" com o Windows no escuro
    const p = await ctx.newPage(); await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300);
    await p.click('.dgo-aone-x').catch(() => {}); await p.click('#b-menu'); await p.waitForTimeout(500);
    const ruins = await p.evaluate(() => {
      const rgb = s => (s.match(/[\d.]+/g) || []).map(Number);
      const lum = c => { const f = x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
      const fundo = e => { for (; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c.length >= 3 && (c.length < 4 || c[3] > 0.5)) return c; } return [0, 0, 0]; };
      return [...document.querySelectorAll('#gaveta .gv-item, #gaveta .grupo-menu, #gaveta .gv-topo b')].map(e => { const a = lum(rgb(getComputedStyle(e).color)), z = lum(fundo(e)); return [e.textContent.trim().slice(0, 20), (Math.max(a, z) + 0.05) / (Math.min(a, z) + 0.05)]; }).filter(x => x[1] < 4.5).map(x => x[0] + ' ' + x[1].toFixed(2));
    });
    ok(ruins.length === 0, `${nome}/escuro: menu ☰ legível ${ruins.slice(0, 4).join(' | ')}`);
    await p.screenshot({ path: `${OUT}/${nome}-menu-escuro.png` });
    await ctx.close();
  }
  // revisão da 0.7.30: no claro e no escuro, nenhum texto da Lista, do Painel, da Configuração e do Perfil abaixo do contraste mínimo
  // (4,5:1; 3:1 em letra grande), medido contra o fundo de verdade de cada texto
  const medir = () => {
    const rgb = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [v[0], v[1], v[2], v.length > 3 ? v[3] : 1]; };
    const lum = c => { const f = x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
    const fundo = el => { const pilha = []; for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.backgroundImage !== 'none' && !cs.backgroundImage.startsWith('url')) return null; const c = rgb(cs.backgroundColor); if (c && c[3] > 0) { pilha.push(c); if (c[3] >= 1) break; } } let base = [255, 255, 255]; if (getComputedStyle(document.documentElement).colorScheme === 'dark' && !pilha.length) base = [0, 0, 0]; for (let i = pilha.length - 1; i >= 0; i--) { const c = pilha[i]; base = [0, 1, 2].map(k => c[k] * c[3] + base[k] * (1 - c[3])); } return base; };
    const out = [];
    for (const el of document.querySelectorAll('body *')) {
      if (!el.childNodes.length || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
      const r = el.getBoundingClientRect(); if (!r.width || !r.height || r.bottom < 0 || r.top > innerHeight) continue;
      const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity === 0) continue;
      let tc = rgb(cs.color), bg = fundo(el); if (!tc || !bg) continue;
      const t = [0, 1, 2].map(k => tc[k] * tc[3] + bg[k] * (1 - tc[3]));
      const L1 = lum(t), L2 = lum(bg), cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      const grande = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.6 && +cs.fontWeight >= 700);
      if (cr < (grande ? 3 : 4.5)) out.push(cr.toFixed(2) + ' ' + (el.id ? '#' + el.id : el.tagName.toLowerCase()) + '.' + String(el.className).slice(0, 30) + ' «' + el.textContent.trim().slice(0, 25) + '»');
    }
    return [...new Set(out)];
  };
  for (const tema of ['claro', 'escuro']) {
    const ctx = await b.newContext({ viewport: { width: 1366, height: 900 } });
    await ctx.addInitScript((tm) => { try { localStorage.setItem('lexsuite:tema', tm); localStorage.setItem('lexsuite:mais-filtros', '1'); } catch (e) {} }, tema);
    const p = await ctx.newPage(); await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1500); await p.click('.dgo-aone-x').catch(() => {});
    const ruins = new Set();
    for (const acao of [() => p.click('#v-lista'), () => p.click('#v-painel'), () => p.evaluate(() => scrollTo(0, 900)), () => p.click('#b-config'),
      async () => { await p.keyboard.press('Escape'); await p.waitForTimeout(300); await p.click('#b-perfil'); }]) {
      await acao(); await p.waitForTimeout(600); (await p.evaluate(medir)).forEach(x => ruins.add(x));
    }
    ok(ruins.size === 0, `${tema}: texto com contraste suficiente ${[...ruins].slice(0, 4).join(' | ')}`);
    await ctx.close();
  }
  // teste do dono (0.7.30; 0.7.33: o menu abre pelo primeiro item, hoje Destaques e exclusões): Configurações pelo menu ☰ abre em janela, rola com a roda do mouse, e o (?) abre na frente
  { const ctx = await b.newContext({ viewport: { width: 1366, height: 700 } }); const p = await ctx.newPage();
    await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300); await p.click('.dgo-aone-x').catch(() => {});
    await p.click('#b-menu'); await p.waitForTimeout(400); await p.locator('.gv-item', { hasText: /^Destaques e exclusões/ }).first().click(); await p.waitForTimeout(700);
    await p.mouse.move(683, 450); await p.mouse.wheel(0, 600); await p.waitForTimeout(400);
    const y = await p.evaluate(() => document.getElementById('config').scrollTop); const pag = await p.evaluate(() => document.getElementById('config').classList.contains('pagina'));
    ok(!pag && y > 100, `Configuração pelo menu abre em janela e rola com a roda do mouse (${y})`);
    await p.click('#c-l-codigo').catch(() => {}); const aj = p.locator('#config .ajuda').first(); await aj.scrollIntoViewIfNeeded(); await aj.click(); await p.waitForTimeout(300);
    const z = await p.evaluate(() => { const q = document.querySelector('.balao'); if (!q) return 'sem balão'; const r = q.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return q.contains(e) ? 'na frente' : 'atrás'; });
    ok(z === 'na frente', `o (?) da Configuração abre na frente da janela (${z})`); await ctx.close(); }
  // 0.7.39 (revisão da Operação): motivo de 200 caracteres nas empresas excluídas não alarga a janela (360 e 1366 px); ▸ e ✎
  for (const w of [360, 1366]) { const ctx = await b.newContext({ viewport: { width: w, height: 800 } }); const p = await ctx.newPage();
    await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300); await p.click('.dgo-aone-x').catch(() => {});
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); });
    await p.click('#b-config'); await p.waitForTimeout(500); await p.evaluate(() => { document.querySelector('.rg-exc-det').open = true; });
    await p.locator('#c-regras input[placeholder^="CNPJ, CPF"]').fill('Empresa Ficticia Motivo Longo Ltda'); await p.locator('#c-regras input[placeholder^="Motivo"]').fill('motivo '.repeat(40).slice(0, 200));
    await p.locator('#c-regras button', { hasText: 'Acrescentar' }).click(); await p.waitForTimeout(600);
    const r = await p.evaluate(() => { const c = document.getElementById('config'); const ln = [...document.querySelectorAll('.rg-exc-linha')].find(l => /Motivo Longo/.test(l.textContent)); return { larg: Math.round(c.getBoundingClientRect().width), sw: c.scrollWidth, cw: c.clientWidth, mais: ln && !ln.querySelector('.rg-exc-mais').hidden, lapis: !!(ln && ln.querySelector('.rg-exc-lapis')), rem: ln && ln.querySelector('.fs-apagar').textContent }; });
    ok(r.sw <= r.cw + 1 && r.larg <= w, `${w}px: motivo longo não alarga Configurações (${r.larg} px, ${r.sw}/${r.cw})`);
    ok(r.mais && r.lapis && r.rem === 'Remover', `${w}px: motivo cortado tem ▸, ✎ e "Remover" (${JSON.stringify(r)})`);
    await ctx.close(); }
  // 0.7.32: 320 px em inglês sem rolagem lateral; gráfico do Painel desliga pela legenda (apagado) sem mexer na Lista; faixa de leitura baixa
  { const ctx = await b.newContext({ viewport: { width: 320, height: 700 }, isMobile: true, hasTouch: true });
    await ctx.addInitScript(() => { try { localStorage.setItem('lexsuite:idioma', 'en'); } catch (e) {} });
    const p = await ctx.newPage(); await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300);
    for (const aba of ['lista', 'painel']) { await p.click('#v-' + aba); await p.waitForTimeout(400); const r = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]); ok(r[0] <= r[1] + 1, `320px en/${aba}: nada sai da tela (${r[0]} de ${r[1]})`); }
    await ctx.close(); }
  { const ctx = await b.newContext({ viewport: { width: 1366, height: 900 } }); const p = await ctx.newPage();
    await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300); await p.click('.dgo-aone-x').catch(() => {});
    const h = await p.evaluate(() => Math.round(document.getElementById('bloco-leitura').getBoundingClientRect().height)); ok(h <= 72, `faixa de leitura baixa no notebook (${h} px; 0.7.39: até 72)`);
    await p.click('#v-painel'); await p.waitForTimeout(500);
    const card = p.locator('.grade-graf > *', { hasText: /Situação no escritório|Status at the firm/ }).first();
    await card.locator('button.barra-l').first().click(); await p.waitForTimeout(400);
    const r = await card.evaluate(c => ({ apagadas: c.querySelectorAll('.barra-l.desligada').length, todas: c.querySelectorAll('.barra-l').length, mostrar: !!c.querySelector('.graf-acoes') }));
    ok(r.apagadas === 1 && r.todas >= 2 && r.mostrar, `Painel: item desligado fica apagado no gráfico (${r.apagadas} de ${r.todas})`);
    await p.click('#v-lista'); await p.waitForTimeout(400);
    const fl = await p.evaluate(() => document.getElementById('f-sit').textContent);
    ok(!/\(\d+\)/.test(fl.split('✕')[0]) || /Todas|All/.test(fl), `a Lista não herdou o filtro do Painel (${fl.slice(0, 30)})`);
    await ctx.close(); }
  // revisão da 0.7.32 (bloqueio 1): com mais de 8 categorias, desligar uma tira só ela do total (o resto, inclusive o que não aparece, continua)
  { const ctx = await b.newContext({ viewport: { width: 1366, height: 900 } });
    await ctx.route('**/dados*', async r => { const resp = await r.fetch(); const j = await resp.json();
      const ufs = ['SP', 'RJ', 'MG', 'PR', 'SC', 'RS', 'BA', 'PE', 'CE', 'GO', 'DF', 'ES'];
      (j.itens || []).forEach((i, k) => { i.empresa = Object.assign({}, i.empresa || {}, { uf: k % 5 === 4 ? '' : ufs[k % ufs.length] }); }); await r.fulfill({ response: resp, json: j }); });  // segunda revisão da 0.7.32: 1 em cada 5 sem estado (sem CNPJ)
    const p = await ctx.newPage(); await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300); await p.click('.dgo-aone-x').catch(() => {});
    await p.click('#v-painel'); await p.waitForTimeout(500);
    const kpi = () => p.evaluate(() => Number((document.querySelector('.kpi') || {}).innerText.replace(/\D+/g, ' ').trim().split(' ')[0]));
    const antes = await kpi();
    const card = p.locator('.grade-graf > *', { hasText: /Estado da empresa|Company state/ }).first();
    const um = card.locator('button.barra-l:not([data-gk$="__nao__"])').first();
    const n1 = Number((await um.locator('.n').innerText()).replace(/\D/g, ''));
    await um.click(); await p.waitForTimeout(400);
    const depois = await kpi();
    ok(depois === antes - n1, `Painel com 12 estados: desligar um tira só ele (${antes} → ${depois}, esperado ${antes - n1})`);
    const sem = card.locator('button.barra-l[data-gk$="__nao__"]').first();
    ok(await sem.count() === 1, 'Painel: a linha "Sem estado" (sem CNPJ) se liga e desliga como as outras');
    if (await sem.count()) { const ns = Number((await sem.locator('.n').innerText()).replace(/\D/g, '')); await sem.click(); await p.waitForTimeout(400); const d2 = await kpi(); ok(d2 === antes - n1 - ns, `Painel: desligar "Sem estado" também tira só ela (${depois} → ${d2}, esperado ${antes - n1 - ns})`); }
    await ctx.close(); }
  await b.close();
  console.log(falhas.length ? 'FALHOU:\n - ' + falhas.join('\n - ') : `OK (${n} verificações)`);
  process.exit(falhas.length ? 1 : 0);
})();
