const { chromium } = require('playwright');
// 0.7.43 (dono: "tem que ter um regression"): o que o escritório faz todo dia, conferido na tela de verdade, com dados
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

  // 5. CNJ fora do ar (0.7.44): a faixa vermelha diz até que dia já foi lido e a última conferência; quando o CNJ volta, aviso verde
  {
    let cnj = { situacao: 'fora', testado: '2026-11-13T15:10', tribunal: 'TRT9', dia: '2026-11-12', lendo: false };
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'painel'); } catch (e) {} });
    await p.route('**/dados*', async r => { const resp = await r.fetch(); const j = await resp.json(); j.ultima_tentativa = { causa: 'governo_fora', tribunal: 'TRT9', quando_local: '2026-11-13T14:54:00-03:00', ok_ate: '2026-11-13' }; r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.route('**/estado', async r => { const resp = await r.fetch(); const j = await resp.json(); j.cnj = cnj; r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.reload(); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 });
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); document.getElementById('v-painel').click(); });
    await espera(11500);  // o batimento da tela é de 10 em 10 s
    const fx = await p.evaluate(() => { const f = document.querySelector('.faixa-falha'); return f ? f.innerText : ''; });
    confere(/Nada se perdeu: o TRT9 já foi lido até 13\/NOV/i.test(fx), 'CNJ fora: a faixa vermelha diz até que dia já foi lido');
    confere(/15 em 15 minutos.*15:10, ainda fora/.test(fx), 'CNJ fora: a faixa mostra a última conferência (15:10)');
    cnj = { situacao: 'voltou', testado: '2026-11-13T15:25', tribunal: 'TRT9', dia: '2026-11-12', lendo: false };
    await espera(11000);
    const av = await p.evaluate(() => [...document.querySelectorAll('.aviso-rapido')].map(x => x.textContent).join(' | '));
    confere(/O CNJ voltou a responder \(15:25\)/.test(av), 'CNJ volta: aparece o aviso verde ("' + av.slice(0, 80) + '")');
    confere(p._erros.length === 0, 'CNJ: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 6. Área logada v2 (0.7.46): passos, faixa pendente, resposta com 2 lotes, relatório, filtro, selo, (?) fixo e interruptor
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); localStorage.removeItem('lexsuite:filtro-atual'); } catch (e) {} });
    await p.evaluate(() => document.getElementById('v-lista').click()); await espera(400);
    await p.evaluate(() => [...document.querySelectorAll('#lista article.item input[type=checkbox]')].slice(0, 2).forEach(c => c.click())); await espera(300);
    const bal = await p.evaluate(() => { document.querySelector('#lote .ajuda').click(); const q = document.querySelector('.balao'); const r = q.getBoundingClientRect(); return { pos: getComputedStyle(q).position, dentro: r.top >= 0 && r.bottom <= innerHeight }; });
    confere(bal.pos === 'fixed' && bal.dentro, 'Área logada: o (?) da barra de seleção abre fixo e dentro da tela');
    await p.evaluate(() => document.body.click());
    await p.evaluate(() => [...document.querySelectorAll('#lote button')].find(x => /área logada|logged-in area/.test(x.textContent)).click()); await espera(800);
    const p1 = await p.evaluate(() => document.querySelector('#janela .al-resumo').textContent);
    confere(/2 processos, em 1 lote/.test(p1), 'Área logada: passo 1 conta os processos e os lotes ("' + p1.slice(0, 60) + '")');
    await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].pop().click()); await espera(900);
    const p2 = await p.evaluate(() => ({ caixa: (document.querySelector('#janela .al-pedido') || {}).value || '', dialogos: document.querySelectorAll('dialog[open]').length }));
    confere(p2.caixa.includes('RESPOSTA PARA O RADAR v1 · lote 1 de 1') && p2.dialogos === 1, 'Área logada: passo 2 mostra o pedido na caixa, numa janela só');
    const ids = [...p2.caixa.matchAll(/\| (\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}) \| TRT/g)].map(m => m[1]);
    await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].pop().click()); await espera(400);
    confere(await p.evaluate(() => !document.getElementById('faixa-area').hidden && !document.getElementById('janela').open), 'Área logada: "Fechar e voltar" fecha a janela e deixa a faixa do pedido pendente');
    await p.reload(); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 });
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); document.getElementById('v-lista').click(); }); await espera(400);
    confere(await p.evaluate(() => !document.getElementById('faixa-area').hidden), 'Área logada: o pedido pendente continua depois de recarregar');
    await p.evaluate(() => document.querySelector('#faixa-area button').click()); await espera(300);
    await p.fill('#janela .al-resposta', 'Oi!\nNão deu para entrar.'); await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].pop().click()); await espera(700);
    confere(/Não achei a tabela|did not find/.test(await p.evaluate(() => document.querySelector('#janela .al-msg').innerText)), 'Área logada: texto sem bloco avisa "Não achei a tabela" e mostra o começo');
    const cab = '| processo | dado | valor | resultado | fonte | data | observação |\n|---|---|---|---|---|---|---|\n';
    const resp = 'Pronto!\nRESPOSTA PARA O RADAR v1 · lote 1 de 1\n' + cab + '| ' + ids[0] + ' | data_ajuizamento | 2026-11-01 | encontrado | PJe dados do processo | 2026-11-14 | |\n| ' + ids[1] + ' | email | | tentar_depois | | 2026-11-14 | petição em PDF |\n| ' + ids[1] + ' | telefone | 123.456.789-09 | encontrado | PJe petição inicial | 2026-11-14 | |\nFim.';
    await p.fill('#janela .al-resposta', resp); await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].pop().click()); await espera(1300);
    const p4 = await p.evaluate(() => { const c = [...document.querySelectorAll('#janela .al-card b')].map(x => x.textContent); return { cards: c, tabela: !!document.querySelector('#janela .al-tabela'), passo: document.querySelector('#janela .al-passos .on').textContent }; });
    confere(p4.passo === '4' && p4.cards.join(',') === '2,1,0,1,1' && p4.tabela, 'Área logada: passo 4 com totais (2 pedidos, 1 novo, 1 tentar depois, 1 recusada) e o que mudou (' + p4.cards.join(',') + ')');
    await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].pop().click()); await espera(1500);
    const fl = await p.evaluate(() => ({ filtro: !document.getElementById('f-area').hidden, selo: document.querySelectorAll('.selo-area').length, faixa: document.getElementById('faixa-area').hidden }));
    confere(fl.filtro && fl.selo >= 1 && fl.faixa, 'Área logada: depois da resposta, filtro e selo aparecem e a faixa some');
    await p.evaluate(() => { const o = window.SolverRecursos.ligado; window.SolverRecursos.ligado = (id, pd) => id === 'area-logada' ? false : o(id, pd); document.getElementById('v-arquivo').click(); });
    await espera(300); await p.evaluate(() => document.getElementById('v-lista').click()); await espera(300);
    await p.evaluate(() => [...document.querySelectorAll('#lista article.item input[type=checkbox]')].slice(0, 1).forEach(c => c.click())); await espera(200);
    const vis = await p.evaluate(() => [...document.querySelectorAll('[data-recurso="area-logada"]')].filter(x => x.offsetParent !== null).length);
    confere(vis === 0, 'Área logada: com o recurso desligado na licença, barra, cartão, filtro e faixa somem (' + vis + ' visíveis)');
    confere(p._erros.length === 0, 'Área logada: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 7. CNJ fora e antivírus (0.7.47): "é do CNJ ou é daqui" na faixa e no histórico, a linha da SolverONE, a opção de
  //    e-mail e o antivírus em Sobre este computador (dados fictícios injetados nas respostas do programa)
  {
    const AV = { identificado: true, lido_em: '2026-11-14', antivirus: [{ nome: 'Windows Defender', ligado: false }, { nome: 'Bitdefender Antivirus', ligado: true }],
      firewall: [{ nome: 'Bitdefender Firewall', ligado: true }], principal: 'Bitdefender Antivirus',
      link: 'https://judicial.solverone.com.br/antivirus.html#pt-bitdefender', link_en: 'https://judicial.solverone.com.br/antivirus.html#en-bitdefender' };
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'painel'); } catch (e) {} });
    await p.route('**/dados*', async r => { const resp = await r.fetch(); const j = await resp.json();
      j.ultima_tentativa = { causa: 'governo_fora', tribunal: 'TRT9', quando_local: '2026-11-13T14:54:00-03:00', origem_falha: 'cnj_aplicacao',
        origem_pt: 'O servidor do CNJ respondeu erro (aplicação). Sua internet está normal. Não é problema deste computador.', origem_en: 'x' };
      if (j.app) j.app.computador = AV; r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.route('**/estado', async r => { const resp = await r.fetch(); const j = await resp.json();
      j.cnj = { situacao: 'fora', testado: '2026-11-13T15:10', tribunal: 'TRT9', dia: '2026-11-12', lendo: false };
      j.cnj_solverone = { fora: 23, total: 24, desde: '13:30', pt: 'A SolverONE também vê o CNJ fora desde 13h30 (23 de 24 tribunais).', en: 'y' };
      j.sinais = [{ sinal: 'tarefa_falhou', chave: 'tarefa_nunca', pt: 'A leitura automática das 20:00 não rodou, embora a tarefa exista. O Bitdefender Antivirus pode estar impedindo.', en: 'z', link: AV.link, link_en: AV.link_en }];
      r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.route('**/historico', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify({ tentativas: [{ quando_local: '2026-11-13T14:54:00-03:00', origem: 'agendamento', tribunal: 'TRT9',
      dias_pedidos: '2026-11-13', http: '500', causa: 'governo_fora', fez: 'não leu este tribunal; seguiu com os outros', duracao: 3.2, origem_falha: 'cnj_aplicacao',
      origem_pt: 'O servidor do CNJ respondeu erro (aplicação). Sua internet está normal. Não é problema deste computador.',
      tecnico: 'Diagnóstico: O servidor do CNJ respondeu erro (aplicação).\nCabeçalhos: server: CloudFront; x-amz-cf-pop: GRU3-P1' }] }) }));
    await p.reload(); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 });
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); document.getElementById('v-painel').click(); });
    await espera(11500);  // o batimento traz o estado (CNJ e o que a SolverONE vê)
    const fx = await p.evaluate(() => { const f = document.querySelector('.faixa-falha'); return f ? f.innerText : ''; });
    confere(/O servidor do CNJ respondeu erro \(aplicação\)\. Sua internet está normal/.test(fx), 'CNJ fora: a faixa do Painel diz que é do CNJ, não deste computador');
    confere(/A SolverONE também vê o CNJ fora desde 13h30 \(23 de 24 tribunais\)/.test(fx), 'CNJ fora: a faixa mostra a linha da SolverONE');
    const est = await p.evaluate(() => { const s_ = document.querySelector('.sinal-pc'); return s_ ? { t: s_.innerText, href: (s_.querySelector('a') || {}).href || '' } : null; });
    confere(est && /Bitdefender Antivirus pode estar impedindo/.test(est.t) && /#pt-bitdefender$/.test(est.href), 'Antivírus: o aviso do programa nomeia o antivírus e leva aos passos dele');
    await abrirConfig(p); await espera(600);
    const sobre = await p.evaluate(() => { const i = document.getElementById('c-info'); const a = i.querySelector('a.link-antivirus'); return { t: i.innerText, href: a ? a.href : '', a: a ? a.textContent : '' }; });
    confere(/Bitdefender Antivirus \(ligado\)/.test(sobre.t) && /Windows Defender \(desligado\)/.test(sobre.t) && /Bitdefender Firewall/.test(sobre.t), 'Sobre este computador: antivírus e firewall, ligados ou não');
    confere(/#pt-bitdefender$/.test(sobre.href) && /Como liberar o RADAR no Bitdefender Antivirus/.test(sobre.a), 'Sobre este computador: "Como liberar o RADAR no Bitdefender Antivirus" abre a seção dele');
    confere(/Recursos da licença[\s\S]*Trazer dados da área logada: ligado/.test(sobre.t), 'Sobre este computador: recursos da licença');
    const cnjOpc = await p.evaluate(() => ({ marcado: document.getElementById('c-avisar-cnj').checked, rot: document.getElementById('c-l-avisar-cnj').textContent, x: document.getElementById('c-avisar-cnj-x').textContent }));
    confere(!cnjOpc.marcado && /mais de 4 horas em dia útil/.test(cnjOpc.rot) && /um e-mail na queda e um na volta/.test(cnjOpc.x), 'Aviso por e-mail do CNJ: desligado por padrão, com a explicação');
    await p.evaluate(() => { document.getElementById('c-avisar-cnj').click(); document.getElementById('c-salvar').click(); }); await espera(1500);
    await abrirConfig(p); await espera(600);
    confere(await p.evaluate(() => document.getElementById('c-avisar-cnj').checked), 'Aviso por e-mail do CNJ: fica marcado depois de salvar e reabrir');
    await p.evaluate(() => { document.getElementById('c-avisar-cnj').click(); document.getElementById('c-salvar').click(); }); await espera(1200);  // volta ao padrão
    await p.evaluate(() => document.getElementById('c-historico').click()); await espera(900);
    const h = await p.evaluate(() => { const r = document.querySelector('.historico tbody tr'); return r ? { o: (r.querySelector('.origem-hist') || {}).textContent || '', tec: !!r.querySelector('details.tec-hist code') } : null; });
    confere(h && /Não é problema deste computador/.test(h.o) && h.tec, 'Histórico de leituras: a frase do diagnóstico e os detalhes técnicos');
    confere(p._erros.length === 0, 'CNJ e antivírus: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(res.join('\n'));
  console.log(falhas ? `\n${falhas} FALHA(S)` : '\nTUDO OK');
  process.exit(falhas ? 1 : 0);
})().catch(e => { console.log(res.join('\n')); console.log('ERRO NO ROTEIRO:', e.message); process.exit(1); });
