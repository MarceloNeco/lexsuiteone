const { chromium } = require('playwright');
// 0.7.40 (revisão do dono): uso: PORTA=8781 python3 -B guarda_rede.py servidor_ficticio.py pronto & ; node ver_na_lista.js
const porta = process.env.PORTA || '8781';
// Para cada cartão do Painel com "Ver na lista": o total da Lista depois do clique tem de ser igual ao total do cartão.
(async () => {
  const b = await chromium.launch(); const erros = []; const res = [];
  for (const tipo of ['pizza', 'barras']) {
    const p = await b.newPage({ viewport: { width: 1366, height: 900 } }); p.on('pageerror', e => erros.push(String(e)));
    await p.addInitScript((tp) => { try { localStorage.setItem('lexsuite:graf-tipo', tp); localStorage.setItem('lexsuite:emp-top', '5'); } catch (e) {} }, tipo);
    await p.goto('http://127.0.0.1:' + porta + '/'); await p.waitForTimeout(1500); await p.click('.dgo-aone-x').catch(() => {});
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); });
    const n = await p.evaluate(() => { document.getElementById('v-painel').click(); return document.querySelectorAll('.grade-graf > .graf').length; });
    for (let i = 0; i < n; i++) {
      await p.evaluate(() => document.getElementById('v-painel').click()); await p.waitForTimeout(400);
      const info = await p.evaluate((i) => {
        const c = document.querySelectorAll('.grade-graf > .graf')[i], tit = c.querySelector('h3').textContent;
        const vl = [...c.querySelectorAll('.graf-acoes button')].find(x => /Ver na lista/.test(x.textContent));
        let tot = 0;
        const anel = c.querySelector('.anel-total');
        if (anel) tot = Number(anel.textContent.replace(/\D/g, ''));
        else tot = [...c.querySelectorAll('.barra-l:not(.desligada) .n')].reduce((a, x) => a + Number((x.firstChild ? x.firstChild.textContent : x.textContent).replace(/\D/g, '')), 0);
        if (/Empresas/.test(tit) && !anel) tot = [...c.querySelectorAll('.barra-l .n')].slice(0, 5).reduce((a, x) => a + Number((x.firstChild ? x.firstChild.textContent : x.textContent).replace(/\D/g, '')), 0);
        if (/Empresas/.test(tit) && anel) tot = [...c.querySelectorAll('li:not(.desligada) .leg-item')].filter(x => !/^Outros/.test(x.textContent)).reduce((a, x) => a + Number(x.querySelector('.leg-n').textContent.split(' ')[0].replace(/\D/g, '')), 0);
        if (vl) vl.click();
        return { tit, tot, tem: !!vl };
      }, i);
      if (!info.tem) { res.push(`${tipo} | ${info.tit}: sem "Ver na lista"`); continue; }
      await p.waitForTimeout(500);
      const lista = await p.evaluate(() => { const m = document.getElementById('mais'); if (!m.hidden) return Number(document.getElementById('mais-txt').textContent.split(' de ')[1].replace(/\D/g, '')); return document.querySelectorAll('#lista article.item').length; });
      res.push(`${tipo} | ${info.tit}: cartão ${info.tot}, Lista ${lista} ${info.tot === lista ? 'OK' : 'DIFERENTE'}`);
      await p.evaluate(() => { const b = document.getElementById('b-limpar-filtros'); if (b && !b.disabled) b.click(); });
    }
    await p.close();
  }
  console.log(res.join('\n')); console.log('erros', erros); await b.close();
  const ruins = res.filter(r => !/ OK$|sem "Ver na lista"/.test(r)).length + erros.length;
  console.log(ruins ? 'FALHOU' : `OK (${res.length} cartões)`); process.exit(ruins ? 1 : 0);
})();
