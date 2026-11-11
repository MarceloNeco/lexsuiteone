/* Teste permanente de uso da tela (regra do dono, 09/Nov): a cada versão, a tela é aberta em 4 larguras e falha se
   sobrar faixa vazia nas laterais, se algo sair da tela ou se o texto de um cartão cortar. Também grava os prints
   para o dono aprovar antes de publicar. Dados fictícios.
   Uso: (cd robo/testes/tela && PORTA=8781 python servidor_ficticio.py pronto &) ; node larguras.js 8781 pasta-dos-prints */
const { chromium, devices } = require('playwright');
const [porta, OUT] = [process.argv[2] || '8781', process.argv[3] || '.'];
(async () => {
  const b = await chromium.launch(); const falhas = []; let n = 0;
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
  // teste do dono (0.7.30): Configuração e Perfil abertos como página (pelo menu ☰) rolam com a roda do mouse e os dois dedos
  { const ctx = await b.newContext({ viewport: { width: 1366, height: 700 } }); const p = await ctx.newPage();
    await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1300); await p.click('.dgo-aone-x').catch(() => {});
    await p.click('#b-menu'); await p.waitForTimeout(400); await p.locator('.gv-item', { hasText: /^Configuração/ }).first().click(); await p.waitForTimeout(700);
    await p.evaluate(() => scrollTo(0, 0)); await p.mouse.move(683, 450); await p.mouse.wheel(0, 600); await p.waitForTimeout(400);
    const y = await p.evaluate(() => window.scrollY); ok(y > 100, `Configuração como página rola com a roda do mouse (${y})`); await ctx.close(); }
  await b.close();
  console.log(falhas.length ? 'FALHOU:\n - ' + falhas.join('\n - ') : `OK (${n} verificações)`);
  process.exit(falhas.length ? 1 : 0);
})();
