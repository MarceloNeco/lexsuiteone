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
  await b.close();
  console.log(falhas.length ? 'FALHOU:\n - ' + falhas.join('\n - ') : `OK (${n} verificações)`);
  process.exit(falhas.length ? 1 : 0);
})();
