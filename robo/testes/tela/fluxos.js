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
    const msgSem = await p.evaluate(() => document.querySelector('#janela .al-msg').innerText);
    confere(/Não encontrei a resposta da ferramenta neste texto/.test(msgSem) && /Oi!/.test(msgSem) && !/RESPOSTA PARA O RADAR|v1/.test(msgSem), 'Área logada: texto sem a tabela avisa sem jargão ("Não encontrei a resposta da ferramenta") e mostra o começo');
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

  // 8. Quem pula versões (0.7.45 → 0.7.47) vê as Novidades das duas (revisão da publicação conjunta, 14/Nov)
  {
    const p = await b.newPage({ viewport: { width: 1366, height: 900 } }); p._erros = []; p.on('pageerror', e => p._erros.push(String(e)));
    await p.addInitScript(() => { try { localStorage.setItem('lexsuite:novidades-vistas', '0.7.45'); localStorage.setItem('lexsuite:visao', 'lista'); } catch (e) {} });
    await p.goto(URL_); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 }); await espera(800);
    const nv = await p.evaluate(() => { const d = document.getElementById('janela'); return d && d.open ? d.innerText : ''; });
    confere(/Novidades da versão 0\.7\.47/.test(nv) && /Novidades da versão 0\.7\.46/.test(nv) && !/Novidades da versão 0\.7\.45/.test(nv),
      'Novidades: da 0.7.45 para a 0.7.47 mostra a 0.7.47 e a 0.7.46 (e não a 0.7.45, já vista)');
    confere(p._erros.length === 0, 'Novidades: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 9. Leitura pela consulta pública quando o caderno cai (0.7.48): cenas 2, 3 e 4 na faixa, "Ver os N processos", opção
  //    em Configurações e as linhas novas do Histórico (dados fictícios injetados nas respostas do programa)
  {
    const RODADA = '2026-11-14T20:00';
    const SIT3 = { pt: 'Diário de hoje lido pela consulta pública: 2 processos novos.', en: 'x', quando: '2026-11-14T20:09', lidas: 9, novas: 2, com_cnpj: 2,
      consulta: { novos: 2, tribunais: ['TRT2'], dias: ['2026-11-13'], pedidos: 118, minutos: 19, parcial: false }, rodada: RODADA };
    let estado = { rodando: true, progresso: 30, mensagens: [], consulta: { tribunal: 'TRT2', dia: '13/NOV', vara: 7, varas: 180, lidas: 0, total: 0, fim: false } };
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); } catch (e) {} });
    await p.route('**/dados*', async r => { const resp = await r.fetch(); const j = await resp.json();
      (j.itens || []).slice(0, 2).forEach(i => { i.rodada = RODADA; i.fonte_leitura = 'consulta'; });
      if (j.app) j.app.estado = estado; r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.route('**/estado', async r => { const resp = await r.fetch(); const j = await resp.json(); Object.assign(j, estado); r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.route('**/historico', r => r.fulfill({ contentType: 'application/json', body: JSON.stringify({ tentativas: [
      { tipo: 'conferencia', quando_local: '2026-11-14T20:31:00-03:00', a_mais: 0, tribunais: ['TRT2', 'TRT15'] },
      { tipo: 'consulta', quando_local: '2026-11-14T20:09:00-03:00', novos: 37, tribunais: ['TRT2'], pedidos: 1112, minutos: 19, parcial: false }] }) }));
    await p.reload(); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 }); await espera(1500);
    const c2 = await p.evaluate(() => { const c = document.querySelector('#estado .cena.info'); return c ? c.innerText : ''; });
    confere(/Lendo pela consulta pública do CNJ \(vara por vara\)/.test(c2) && /TRT2 13\/NOV: vara 7 de 180/.test(c2) && /continuar usando o programa/.test(c2), 'Consulta pública, cena 2: "Lendo pela consulta pública (vara por vara)…" com o andamento');
    confere(await p.evaluate(() => !!document.querySelector('#estado button.perigo')), 'Consulta pública, cena 2: o Interromper continua à vista');
    confere(await p.evaluate(() => { const b_ = document.querySelector('#lista article.item'); return !!b_; }), 'Consulta pública, cena 2: a Lista continua livre durante a consulta');
    estado = { rodando: false, situacao: SIT3 };
    await espera(3500);
    const c3 = await p.evaluate(() => { const c = document.querySelector('#estado .cena.ok'); return c ? c.innerText : ''; });
    confere(/Diário de hoje lido pela consulta pública: 2 processos novos/.test(c3) && /confere pelo caderno/.test(c3), 'Consulta pública, cena 3: quantos processos novos e que o caderno confere depois');
    const antes3 = await totalLista(p);
    await p.evaluate(() => [...document.querySelectorAll('#estado .cena.ok button.lk')].find(x => /Ver os 2 processos/.test(x.textContent)).click()); await espera(1200);
    const depois3 = await totalLista(p);
    const chip = await p.evaluate(() => { const c = document.getElementById('chip-rodada'); return c && !c.hidden ? c.textContent : ''; });
    confere(antes3 > 2 && depois3 === 2 && /Novos desta leitura/.test(chip), 'Consulta pública, cena 3: "Ver os 2 processos" mostra só os novos desta leitura (' + antes3 + ' → ' + depois3 + ')');
    confere(await p.evaluate(() => [...document.querySelectorAll('#lista .selo-area')].filter(x => /consulta pública · caderno pendente/.test(x.textContent)).length) === 2, 'Consulta pública: os processos lidos pela consulta trazem o selo "consulta pública · caderno pendente"');
    await p.evaluate(() => document.getElementById('chip-rodada').click()); await espera(900);
    confere(await totalLista(p) === antes3, 'Consulta pública: tirar o filtro "Novos desta leitura" volta a lista inteira');
    estado = { rodando: false, situacao: Object.assign({}, SIT3, { consulta: null, conferencia: { hora: '20h31', a_mais: 3, tribunais: ['TRT2'] } }) };
    await p.reload(); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 }); await espera(1200);
    const c4 = await p.evaluate(() => { const c = document.querySelector('#estado .cena.ok'); return c ? c.innerText : ''; });
    confere(/Caderno do CNJ voltou \(20h31\)\. Conferência feita: 3 processos a mais, já incluídos/.test(c4), 'Consulta pública, cena 4: "Caderno do CNJ voltou (20h31). Conferência feita: 3 processos a mais"');
    await abrirConfig(p); await espera(600);
    const op = await p.evaluate(() => ({ m: document.getElementById('c-consulta').checked, r: document.getElementById('c-l-consulta').textContent, x: document.getElementById('c-consulta-x').textContent }));
    const opAj = await p.evaluate(() => !!document.querySelector('#c-l-consulta .ajuda'));
    confere(op.m && /Usar a consulta pública do CNJ quando o caderno falhar/.test(op.r) && opAj && !op.x, 'Configurações: consulta pública ligada por padrão, com a explicação no (?) (0.7.50)');
    await p.evaluate(() => { document.getElementById('c-consulta').click(); document.getElementById('c-salvar').click(); }); await espera(1500);
    await abrirConfig(p); await espera(600);
    confere(await p.evaluate(() => !document.getElementById('c-consulta').checked), 'Configurações: desligar a consulta pública fica gravado');
    await p.evaluate(() => { document.getElementById('c-consulta').click(); document.getElementById('c-salvar').click(); }); await espera(1200);
    await abrirConfig(p); await espera(500);
    await p.evaluate(() => document.getElementById('c-historico').click()); await espera(900);
    const hs = await p.evaluate(() => [...document.querySelectorAll('.historico tbody tr')].map(r => r.innerText).join('\n'));
    confere(/Leitura pela consulta pública \(caderno do CNJ fora\): 37 processos novos \(TRT2\), 1\.112 pedidos em 19 min\. Conferência pelo caderno pendente/.test(hs), 'Histórico: linha "Leitura pela consulta pública"');
    confere(/Conferência pelo caderno: TRT2, TRT15: nada faltou/.test(hs), 'Histórico: linha da conferência pelo caderno');
    confere(p._erros.length === 0, 'Consulta pública: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 10. 0.7.48: janelas que se movem e mudam de tamanho (voltam ao padrão ao reabrir), ajustes da área logada (teste do dono
  //     na 0.7.47), limpeza do banco em Armazenamento e filtro de cidade (com uma cidade fictícia de outro estado)
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); localStorage.removeItem('lexsuite:filtro-atual'); localStorage.removeItem('lexsuite:area-logada'); } catch (e) {} });
    await p.route('**/dados*', async r => { const resp = await r.fetch(); const j = await resp.json();
      (j.itens || []).slice(0, 3).forEach(i => { i.empresa = Object.assign({}, i.empresa || {}, { municipio: 'NITEROI', uf: 'RJ' }); });
      (j.itens || []).slice(3, 4).forEach(i => { i.empresa = Object.assign({}, i.empresa || {}, { municipio: '', uf: '' }); });
      (j.itens || []).slice(4, 12).forEach((i, k) => { i.empresa = Object.assign({}, i.empresa || {}, { municipio: 'CIDADE FICTICIA ' + (k + 1), uf: 'MG' }); });
      r.fulfill({ response: resp, body: JSON.stringify(j) }); });
    await p.reload(); await p.waitForFunction(() => document.getElementById('carregando').hidden, null, { timeout: 30000 }); await espera(900);
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d && d.open) d.close(); document.getElementById('v-lista').click(); }); await espera(400);
    // janelas: arrastar pelo título e voltar ao centro ao reabrir
    await p.evaluate(() => [...document.querySelectorAll('#lista article.item input[type=checkbox]')].slice(0, 2).forEach(c => c.click())); await espera(300);
    await p.evaluate(() => [...document.querySelectorAll('#lote button')].find(x => /área logada|logged-in area/.test(x.textContent)).click()); await espera(900);
    const caixa0 = await p.evaluate(() => { const r = document.getElementById('janela').getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width }; });
    const tit = await p.evaluate(() => { const h = document.querySelector('#janela h3'); const r = h.getBoundingClientRect(); return { x: r.left + 20, y: r.top + r.height / 2 }; });
    await p.mouse.move(tit.x, tit.y); await p.mouse.down(); await p.mouse.move(tit.x - 150, tit.y + 60, { steps: 6 }); await p.mouse.up(); await espera(200);
    const caixa1 = await p.evaluate(() => { const j = document.getElementById('janela'); const r = j.getBoundingClientRect(); return { x: r.left, y: r.top, movida: j.classList.contains('movida'), resize: getComputedStyle(j).resize }; });
    confere(caixa1.movida && Math.abs((caixa0.x - caixa1.x) - 150) < 8 && Math.abs((caixa1.y - caixa0.y) - 60) < 8 && caixa1.resize === 'both', 'Janelas: a janela se move pelo título e muda de tamanho pelo canto');
    // área logada, passo 1: sócio marcado, (?) dentro da janela, Quantos não passa do limite
    const p1 = await p.evaluate(() => { const j = document.getElementById('janela'); const lb = [...j.querySelectorAll('label')].find(l => /Sócio ou administrador/.test(l.textContent)); return { socio: lb ? lb.querySelector('input').checked : null }; });
    confere(p1.socio === true, 'Área logada: "Sócio ou administrador" vem marcado');
    const bal = await p.evaluate(() => { const j = document.getElementById('janela'); const a = j.querySelector('.ajuda'); a.click(); const q = document.querySelector('.balao'); return q ? !!q.closest('dialog') : false; });
    confere(bal, 'Área logada: o (?) dentro da janela abre por cima dela (dentro da janela, não atrás)');
    await p.evaluate(() => document.querySelector('#janela h3').click());
    const lim = await p.evaluate(() => { const j = document.getElementById('janela'); const i = [...j.querySelectorAll('input[type=number]')][0]; if (!i) return null; i.value = '41'; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); const av = j.querySelector('.al-limite-aviso'); return { v: i.value, max: i.max, av: av ? av.textContent : '' }; });
    confere(lim && Number(lim.v) <= 25 && /Até 25 por pedido \(Configurações → Área logada\)/.test(lim.av), 'Área logada: "Quantos" não passa do limite e diz "até 25 por pedido" (' + (lim && lim.v) + ')');
    await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].pop().click());
    await p.waitForFunction(() => !!document.querySelector('#janela .al-pedido'), null, { timeout: 15000 }); await espera(300);
    const p2 = await p.evaluate(() => { const j = document.getElementById('janela'); return { ic: !!j.querySelector('.al-copiar-ic'), deNovo: /Copiar de novo/.test(j.innerText), cpf: /O que nunca entra/.test(j.innerText), botoes: [...j.querySelectorAll('.botoes button')].map(x => x.textContent), md: !!j.querySelector('.al-md .ajuda, .ajuda[data-md], .al-salvar .ajuda') || /\.md/.test(j.innerText) }; });
    confere(p2.ic && !p2.deNovo, 'Área logada, passo 2: ícone de copiar no canto da caixa, sem "Copiar de novo"');
    confere(!p2.cpf, 'Área logada, passo 2: a frase "O que nunca entra… CPF" não se repete no passo');
    confere(p2.botoes.some(x => /Colar a resposta agora/.test(x)) && p2.botoes.some(x => /Fechar \(trago a resposta depois\)/.test(x)), 'Área logada, passo 2: "Colar a resposta agora" e "Fechar (trago a resposta depois)"');
    const circ = await p.evaluate(() => [...document.querySelectorAll('#janela .al-passos .al-p')].map(x => x.tagName + ':' + x.textContent).join(' '));
    confere(/BUTTON:1Escolher/.test(circ) && /BUTTON:3Resposta/.test(circ) && /DIV:2Pedido/.test(circ), 'Área logada: os círculos têm nome e são clicáveis para voltar (' + circ + ')');
    await p.evaluate(() => [...document.querySelectorAll('#janela .al-passos button')].find(x => /3/.test(x.textContent)).click()); await espera(600);
    await p.evaluate(() => [...document.querySelectorAll('#janela .al-abas button')].find(x => /Arrastar ou escolher arquivo/.test(x.textContent)).click()); await espera(200);
    const p3 = await p.evaluate(() => { const j = document.getElementById('janela'); return { solta: /Arraste o arquivo aqui ou clique para escolher/.test(j.innerText), circ: [...j.querySelectorAll('.al-passos .al-p')].map(x => x.tagName + ':' + x.textContent).join(' ') }; });
    confere(p3.solta, 'Área logada, passo 3: área "Arraste o arquivo aqui ou clique para escolher"');
    confere(/BUTTON:2Pedido/.test(p3.circ), 'Área logada, passo 3: com o pedido pendente, o círculo 2 revê o pedido');
    await p.evaluate(() => [...document.querySelectorAll('#janela .al-passos button')].find(x => /2/.test(x.textContent)).click());
    await p.waitForFunction(() => !!document.querySelector('#janela .al-pedido'), null, { timeout: 15000 }).catch(() => {});
    confere(await p.evaluate(() => /RESPOSTA PARA O RADAR v1/.test((document.querySelector('#janela .al-pedido') || {}).value || '')), 'Área logada: o círculo 2 mostra de novo o pedido pendente');
    await p.evaluate(() => document.getElementById('janela').close()); await espera(300);
    await p.evaluate(() => [...document.querySelectorAll('#lote button')].find(x => /área logada|logged-in area/.test(x.textContent)).click()); await espera(900);
    const caixa2 = await p.evaluate(() => { const j = document.getElementById('janela'); const r = j.getBoundingClientRect(); return { x: r.left, y: r.top, movida: j.classList.contains('movida') }; });
    confere(!caixa2.movida && Math.abs(caixa2.x - caixa0.x) < 3, 'Janelas: ao fechar e abrir de novo, a janela volta ao centro e ao tamanho padrão');
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d.open) d.close(); });
    await p.evaluate(() => { const c_ = [...document.querySelectorAll('#faixa-area button')].find(x => /Cancelar|Cancel/.test(x.textContent)); if (c_) c_.click(); }); await espera(400);
    await p.evaluate(() => { const d = document.getElementById('janela'); if (d.open) { const bs = [...d.querySelectorAll('.botoes button')]; bs[bs.length - 1].click(); } }); await espera(500);
    // cidade: depois do Estado, contagens, busca sem acento, "Sem cidade", troca de estado tira a cidade de fora
    await p.evaluate(() => { const fa = document.getElementById('filtros-avancados'); if (fa.hidden) document.getElementById('b-mais-filtros').click(); }); await espera(300);
    const ordemF = await p.evaluate(() => { const ids = [...document.querySelectorAll('#filtros-avancados [id^="f-"]')].map(x => x.id); return ids.indexOf('f-cidade') - ids.indexOf('f-uf'); });
    confere(ordemF === 1, 'Cidade: o filtro vem logo depois do Estado');
    const total0 = await totalLista(p);
    await p.evaluate(() => document.querySelector('#f-cidade > button').click()); await espera(300);
    const opc = await p.evaluate(() => [...document.querySelectorAll('#f-cidade .multi-lista label')].map(l => l.textContent));
    confere(opc.length >= 9 && /^(Sao Paulo|Barueri)\/SP\d+$/.test(opc[0]) && opc.some(x => /^Niteroi\/RJ3$/.test(x)) && opc.some(x => /^Sem cidade\d+$/.test(x)) && opc.some(x => /^Cidade Ficticia 1\/MG1$/.test(x)), 'Cidade: as opções com quantos processos, as de mais processos primeiro, e "Sem cidade" (' + opc.join(' | ') + ')');
    const busca = await p.evaluate(() => { const i = document.querySelector('#f-cidade .multi-painel input[type=search], #f-cidade .multi-painel input[type=text]'); if (!i) return null; i.value = 'NITERÓI'; i.dispatchEvent(new Event('input', { bubbles: true })); return [...document.querySelectorAll('#f-cidade .multi-lista label')].map(l => l.textContent); });
    confere(busca && busca.length === 1 && /Niteroi/.test(busca[0]), 'Cidade: a busca não liga para acento nem maiúscula ("NITERÓI" acha Niteroi/RJ)');
    await p.evaluate(() => document.querySelector('#f-cidade .multi-lista input[type=checkbox]').click()); await espera(700);
    confere(await totalLista(p) === 3, 'Cidade: escolher Niteroi/RJ mostra só os 3 processos de lá');
    await p.evaluate(() => { const f = document.getElementById('f-uf'); if (!f.querySelector('.multi-painel') || f.querySelector('.multi-painel').hidden) f.querySelector('button').click(); }); await espera(300);
    const ufs = await p.evaluate(() => [...document.querySelectorAll('#f-uf .multi-lista label')].map(l => l.textContent));
    await p.evaluate(() => { const lb = [...document.querySelectorAll('#f-uf .multi-lista label')].find(l => /^SP/.test(l.textContent)); if (lb) lb.querySelector('input').click(); }); await espera(800);
    const depoisUf = await p.evaluate(() => ({ cid: (document.querySelector('#f-cidade > button') || {}).textContent || '', aviso: (document.getElementById('aviso') || document.body).innerText }));
    confere(/Cidades/.test(depoisUf.cid) && /cidade/i.test(depoisUf.aviso), 'Cidade: trocar o estado para SP tira a cidade do RJ, com aviso (' + ufs.join(',') + ')');
    await p.evaluate(() => document.getElementById('b-limpar-filtros').click()); await espera(600);
    confere(await totalLista(p) === total0, 'Cidade: "Limpar filtros" volta a lista inteira');
    // Painel obedece à cidade
    await p.evaluate(() => document.getElementById('v-painel').click()); await espera(900);
    await p.evaluate(() => { const fa = document.getElementById('filtros-avancados'); if (fa.hidden) document.getElementById('b-mais-filtros').click(); }); await espera(300);
    await p.evaluate(() => document.querySelector('#f-cidade > button').click()); await espera(300);
    await p.evaluate(() => { const lb = [...document.querySelectorAll('#f-cidade .multi-lista label')].find(l => /Niteroi/.test(l.textContent)); lb.querySelector('input').click(); }); await espera(900);
    const kp = await p.evaluate(() => (document.querySelector('.kpis .kpi .val') || {}).textContent || '');
    confere(kp.trim() === '3', 'Cidade: o Painel obedece ao filtro (' + kp + ' processos)');
    await p.evaluate(() => document.getElementById('b-limpar-filtros').click()); await espera(500);
    // limpeza do banco em Armazenamento: prazos, o que nunca sai e confirmação em dois cliques
    await abrirConfig(p); await espera(700);
    const lp = await p.evaluate(() => { const w = document.getElementById('c-limpeza'); return w ? { t: w.innerText, r: document.getElementById('c-res-meses').value, a: document.getElementById('c-apa-meses').value, dentro: !!w.closest('#c-limpeza-wrap') } : null; });
    confere(lp && lp.dentro && lp.r === '6' && lp.a === '24' && /O que nunca sai/.test(lp.t), 'Limpeza: na Rotina de limpeza (0.7.50), prazos 6 e 24 meses e "O que nunca sai"');
    const ok1 = await p.evaluate(() => { const bt = [...document.querySelectorAll('#c-limpeza button')].find(x => /^Limpar agora$/.test(x.textContent)); bt.click(); return { bt: bt.textContent, msg: document.getElementById('c-limpeza').innerText }; });
    confere(/Confirmar a limpeza/.test(ok1.bt) && /Clique de novo para confirmar/.test(ok1.msg), 'Limpeza: o primeiro clique só pede confirmação');
    await p.evaluate(() => [...document.querySelectorAll('#c-limpeza button')].find(x => /Confirmar a limpeza/.test(x.textContent)).click());
    await p.waitForFunction(() => /Limpeza feita/.test(document.getElementById('c-limpeza').innerText), null, { timeout: 15000 }).catch(() => {});
    confere(await p.evaluate(() => /Limpeza feita: .* resumidos, .* apagados/.test(document.getElementById('c-limpeza').innerText)), 'Limpeza: o segundo clique limpa sem travar a tela e diz o resultado');
    await p.evaluate(() => { document.getElementById('c-apa-meses').value = '3'; document.getElementById('c-apa-meses').dispatchEvent(new Event('input', { bubbles: true })); });
    confere(await p.evaluate(() => { const r_ = [...document.querySelectorAll('#c-limpeza .alerta')][0]; return r_ && !r_.hidden; }), 'Limpeza: prazo fora da regra mostra a regra');
    const arm = await p.evaluate(() => ({ t: document.getElementById('c-arm').innerText, alertas: [...document.querySelectorAll('#c-arm .alerta')].filter(x => !x.closest('#c-limpeza') && !x.hidden).map(x => x.textContent) }));  // a regra do prazo da limpeza não é aviso de armazenamento
    confere(arm.alertas.length ? !/Tudo certo/.test(arm.t) : /Tudo certo: planilha abaixo de 80 % do limite e espaço no disco/.test(arm.t), 'Armazenamento: "Tudo certo…" só quando não há aviso (' + (arm.alertas.join(' | ') || 'sem aviso') + ')');
    confere(await p.evaluate(() => /ana@example\.com/.test(document.getElementById('c-avisar-cnj-x').textContent)), 'Aviso do CNJ: a opção mostra o endereço que recebe o e-mail');
    confere(p._erros.length === 0, '0.7.48: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 11. 0.7.49: Modo no alto, filtros salvos de fábrica (lista própria com descrição), Tribunal na 1ª linha, Varas com "Nº",
  //     lista aberta acompanha a rolagem, (?) na cor de link e Agrupar por empresa com o alcance
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); localStorage.removeItem('lexsuite:filtro-atual'); localStorage.removeItem('lexsuite:filtros-fabrica'); localStorage.removeItem('lexsuite:filtros'); localStorage.removeItem('lexsuite:agrupar'); } catch (e) {} });
    await espera(600);
    const topo = await p.evaluate(() => ({ modo: document.getElementById('b-modo').textContent, plan: document.getElementById('b-planilha').hidden, tribPai: document.getElementById('f-trib').parentElement.id, tribVis: !document.getElementById('f-trib').hidden }));
    confere(/Modo: Trabalhista/.test(topo.modo) && topo.plan, 'Modo: "Modo: Trabalhista" no alto, no lugar de "Abrir a planilha"');
    confere(topo.tribPai === 'filtros-extra' && topo.tribVis, 'Filtros: Tribunal na primeira linha, à vista');
    await p.click('#b-modo'); await espera(300);
    const modo = await p.evaluate(() => [...document.querySelectorAll('.modo-item')].map(x => x.className + ':' + x.innerText.replace(/\n/g, ' ')));
    confere(modo.length === 5 && /ativo:✓ Trabalhista/.test(modo[0]) && modo.slice(1).every(x => /apagado:.*Não incluído na sua licença/.test(x)), 'Modo: Trabalhista ativo e os outros 4 apagados, "Não incluído na sua licença"');
    await p.evaluate(() => document.querySelector('.modo-item.apagado').click()); await espera(200);
    confere(await p.evaluate(() => /não está incluído na licença deste escritório/.test(document.querySelector('.modo-nota').textContent)), 'Modo: clicar num apagado diz com quem falar, dentro da própria lista');
    await p.keyboard.press('Escape'); await espera(200);
    await p.click('#b-menu'); await espera(400);
    confere(await p.evaluate(() => /Abrir a planilha oficial \(só leitura\)/.test(document.getElementById('gaveta').innerText)), 'Menu ☰ → Planilha: "Abrir a planilha oficial (só leitura)"');
    await p.keyboard.press('Escape'); await espera(300);
    const bs = await p.evaluate(() => document.getElementById('b-salvos').textContent);
    confere(/Filtros salvos \(3\)/.test(bs), 'Filtros salvos: três de fábrica (' + bs.trim() + ')');
    await p.click('#b-salvos'); await espera(300);
    const sv = await p.evaluate(() => { const pn = document.querySelector('.salvos-painel'), r = pn.getBoundingClientRect(), bt = document.getElementById('b-salvos').getBoundingClientRect(); return { t: pn.innerText, cortado: [...pn.querySelectorAll('.salvo-item b')].some(x => x.scrollWidth > x.clientWidth + 1), dentro: r.left >= 0 && r.right <= innerWidth, esq: Math.abs(r.right - bt.right) <= 2 || r.left <= 9, nums: [Math.round(r.left), Math.round(r.right), Math.round(bt.left), Math.round(bt.right)] }; });
    confere(/Para contatar \(7 dias\)[\s\S]*Com telefone ou e-mail/.test(sv.t) && /Buscar contato na área logada \(7 dias\)/.test(sv.t) && /Empresas da semana \(visão completa\)/.test(sv.t), 'Filtros salvos: nome em negrito e descrição embaixo');
    confere(!sv.cortado && sv.dentro && sv.esq, 'Filtros salvos: a lista abre para a esquerda (ou encosta na borda quando não cabe), dentro da tela, sem cortar o nome (' + JSON.stringify(sv.nums) + ', cortado=' + sv.cortado + ')');
    await p.evaluate(() => [...document.querySelectorAll('.salvo-item')].find(x => /Para contatar/.test(x.textContent)).click()); await espera(2500);
    const ap = await p.evaluate(() => ({ per: document.getElementById('periodo').value, cont: document.getElementById('f-contato').value }));
    confere(ap.per === '7' && ap.cont === 'com', 'Filtros salvos: "Para contatar" aplica 7 dias e "Só com contato" (' + JSON.stringify(ap) + ')');
    await p.evaluate(() => document.getElementById('b-limpar-filtros').click());
    await p.evaluate(() => { const s_ = document.getElementById('periodo'); s_.value = '90'; s_.dispatchEvent(new Event('change', { bubbles: true })); }); await espera(2500);
    await p.evaluate(() => { const fa = document.getElementById('filtros-avancados'); if (fa.hidden) document.getElementById('b-mais-filtros').click(); }); await espera(300);
    await p.evaluate(() => document.querySelector('#f-vara > button').click()); await espera(300);
    const va = await p.evaluate(() => { const pn = document.querySelector('#f-vara .multi-painel'); return { cab: (pn.querySelector('.multi-cab') || {}).innerText || '', l: pn.querySelector('.multi-lista label').innerText, uma: [...pn.querySelectorAll('.multi-lista label')].every(l => l.getBoundingClientRect().height < 40) }; });
    confere(/Nº\s*VARA/i.test(va.cab) && /^\d+\s*\n?\s*\d+ª Vara/.test(va.l) && va.uma, 'Varas: cabeçalho "Nº | Vara", número antes do nome, uma linha por vara');
    const d1 = await p.evaluate(() => Math.round(document.querySelector('#f-vara .multi-painel').getBoundingClientRect().top - document.querySelector('#f-vara > button').getBoundingClientRect().bottom));
    await p.mouse.wheel(0, 250); await espera(300);
    const d2 = await p.evaluate(() => Math.round(document.querySelector('#f-vara .multi-painel').getBoundingClientRect().top - document.querySelector('#f-vara > button').getBoundingClientRect().bottom));
    confere(Math.abs(d1 - d2) <= 2, 'Filtros: a lista aberta acompanha o botão ao rolar a tela (' + d1 + ' → ' + d2 + ')');
    await p.keyboard.press('Escape'); await espera(200);
    const aj = await p.evaluate(() => { const a = document.querySelector('#lista .ajuda'); const c0 = getComputedStyle(a).color; a.click(); const c1 = getComputedStyle(a).color; const an = getComputedStyle(document.querySelector('.balao')).animationName; return { c0, c1, an }; });
    confere(aj.c0 === 'rgb(43, 98, 173)' && aj.c1 !== aj.c0 && aj.an === 'balao-cresce', '(?): azul de link parado, volta ao cinza aberto, e o balão cresce (' + JSON.stringify(aj) + ')');
    await p.evaluate(() => document.body.click());
    await p.evaluate(() => { const a = document.getElementById('agrupar'); a.value = 'empresa'; a.dispatchEvent(new Event('change', { bubbles: true })); }); await espera(2000);
    const ag = await p.evaluate(() => ({ dis: document.getElementById('ordem').disabled && document.getElementById('ordem2').disabled, alc: document.getElementById('alcance').value, vis: !document.getElementById('alcance').hidden,
      cab: (document.querySelector('.grupo-emp .ge-cab') || {}).innerText || '', blocos: document.querySelectorAll('.grupo-emp').length, mais: document.getElementById('mais-txt').textContent }));
    confere(ag.dis && ag.vis && ag.alc === 'hibrido', 'Agrupar por empresa: "Ordenar por" apagado e o alcance "Até 50 dos últimos 6 meses"');
    confere(ag.blocos > 0 && /no período · \d+ de \d+ da empresa/.test(ag.cab) && /empresas/.test(ag.mais), 'Agrupar por empresa: blocos com "N no período · X de Y da empresa" (' + ag.cab.replace(/\n/g, ' | ') + ')');
    await p.evaluate(() => document.querySelector('#ordem-ajuda .ajuda').click()); await espera(300);
    confere(await p.evaluate(() => /Agrupar por empresa[\s\S]*até 50 dos últimos 6 meses/i.test(document.querySelector('.balao').innerText)), '(?) de Ordenar explica ordenar × agrupar e o alcance');
    await p.evaluate(() => { document.body.click(); const a = document.getElementById('agrupar'); a.value = ''; a.dispatchEvent(new Event('change', { bubbles: true })); }); await espera(800);
    confere(await p.evaluate(() => !document.getElementById('ordem').disabled && !document.querySelector('.grupo-emp')), 'Agrupar: desligar volta a lista e os "Ordenar por"');
    confere(p._erros.length === 0, '0.7.49: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  // 12. 0.7.50 (dono, 16/Nov): agrupamento (alcance no bloco, setinha, caixinha da empresa, triângulo, etiqueta na linha, excluir pelo
  // nome), notebook (filtros numa linha, rótulos curtos com dica, barra compacta), barra de seleção com Aplicar, Configurações (Rotina de
  // limpeza, Não confirmar, frase do Salvar, rodapé largo, volta do Histórico no mesmo ponto), registro com "Enviar ao suporte"
  {
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); localStorage.removeItem('lexsuite:filtro-atual'); localStorage.setItem('lexsuite:agrupar', JSON.stringify({ a: 'empresa', l: '10' })); } catch (e) {} });
    await p.waitForFunction(() => document.querySelectorAll('.grupo-emp').length > 0, null, { timeout: 20000 }).catch(() => {}); await espera(2500);
    await p.evaluate(() => [...document.querySelectorAll('.ge-barra button')][0].click()); await espera(700);
    const g1 = await p.evaluate(() => [...document.querySelectorAll('.grupo-emp')].map(g => g.querySelectorAll('article.item').length));
    confere(g1.length > 0 && Math.max(...g1) <= 10, 'Agrupar: "Últimos 10 processos" vale para o bloco inteiro (no máximo 10 por empresa: ' + g1.slice(0, 6).join(',') + ')');
    const g2 = await p.evaluate(() => { const g = document.querySelector('.grupo-emp'); const et = document.querySelector('.grupo-emp .etq-anterior'); return { ch: !!g.querySelector('.ge-chevron'), cb: !!g.querySelector('.ge-cb'), tri: document.querySelectorAll('.tri-aviso').length, etq: et ? et.parentElement.className : 'sem etiqueta', prim: et ? et.closest('article').firstElementChild.className : '' }; });
    confere(g2.ch && g2.cb, 'Agrupar: setinha e caixinha no cabeçalho de cada empresa');
    confere(g2.etq === 'sem etiqueta' || (g2.etq === 'meta' && g2.prim === 'sel'), 'Agrupar: a etiqueta "anterior"/"fora dos filtros" fica na linha da data, sem mudar a grade do cartão (' + g2.etq + ')');
    confere(g2.tri > 0, 'Agrupar: empresa sem CNPJ traz o triângulo de aviso (' + g2.tri + ')');
    await p.evaluate(() => document.querySelector('.grupo-emp .ge-cb').click()); await espera(500);
    const lt = await p.evaluate(() => { const g = document.querySelector('.grupo-emp'); const l = document.getElementById('lote'); return { n: g.querySelectorAll('article.item').length, sel: (l.querySelector('b') || {}).textContent, bts: [...l.querySelectorAll('button')].map(x => x.textContent + (x.disabled ? '(apagado)' : '')) }; });
    confere(String(lt.n) === lt.sel, 'Agrupar: a caixinha da empresa marca todos os processos dela (' + lt.sel + ' de ' + lt.n + ')');
    confere(lt.bts.includes('Aplicar(apagado)') && lt.bts.includes('Arquivar'), 'Barra de seleção: "Aplicar" apagado até escolher e "Arquivar" sem número (' + lt.bts.join(' | ') + ')');
    await p.evaluate(() => { const s = document.querySelector('#lote select'); s.value = 'visto'; s.dispatchEvent(new Event('change', { bubbles: true })); }); await espera(200);
    confere(await p.evaluate(() => document.querySelector('#lote select').value === 'visto' && !document.querySelector('#lote .forte').disabled), 'Barra de seleção: a escolha fica à vista e acende o "Aplicar"');
    await p.evaluate(() => document.getElementById('lote').querySelectorAll('button')[[...document.getElementById('lote').querySelectorAll('button')].findIndex(x => /Limpar seleção/.test(x.textContent))].click()); await espera(300);
    // excluir pelo nome (item 33): a empresa sem CNPJ some do agrupamento
    const nomeSem = await p.evaluate(() => { const t_ = document.querySelector('.tri-aviso'); return t_ ? t_.closest('.grupo-emp').querySelector('.ge-nome').textContent : ''; });
    if (nomeSem) {
      await p.evaluate(n => { const g = [...document.querySelectorAll('.grupo-emp')].find(x => x.querySelector('.ge-nome').textContent === n); [...g.querySelectorAll('.ge-acoes button')].find(x => /Excluir esta empresa/.test(x.textContent)).click(); }, nomeSem); await espera(300);
      await p.evaluate(() => [...document.querySelectorAll('#janela .botoes button')].find(x => x.textContent === 'Excluir').click());
      await p.waitForFunction(n => ![...document.querySelectorAll('.ge-nome')].some(x => x.textContent === n), nomeSem, { timeout: 15000 }).catch(() => {});
      confere(await p.evaluate(n => ![...document.querySelectorAll('.ge-nome')].some(x => x.textContent === n), nomeSem), 'Excluir esta empresa: a empresa sem CNPJ, excluída pelo nome, some do agrupamento (' + nomeSem + ')');
    } else confere(false, 'Excluir esta empresa: não achei empresa sem CNPJ nos dados fictícios');
    // rótulos curtos e dica com os marcados
    await p.evaluate(() => { const b_ = document.querySelector('#f-sit > button'); b_.click(); }); await espera(300);
    for (let k = 0; k < 2; k++) { await p.evaluate(() => { const x = [...document.querySelectorAll('#f-sit .multi-lista input')].find(y => !y.checked); if (x) x.click(); }); await espera(500); }  // a lista se redesenha a cada clique
    const rot = await p.evaluate(() => ({ trib: document.querySelector('#f-trib > button').textContent, sit: document.querySelector('#f-sit > button').textContent, dica: document.querySelector('#f-sit > button').title }));
    confere(rot.trib === 'Tribunais' && /^Situação \(2\)$/.test(rot.sit) && /^Situações selecionadas: .+, .+/.test(rot.dica), 'Filtros: rótulo curto ("Tribunais", "Situação (2)") e a dica com os marcados (' + rot.dica + ')');
    await p.evaluate(() => document.getElementById('b-limpar-filtros').click()); await espera(500);
    await p.close();
  }
  {  // notebook com 125 % (~1093 px): a 1ª linha dos filtros numa linha só e a barra compacta ao rolar
    const p = await abrirPagina(b, () => { try { localStorage.setItem('lexsuite:visao', 'lista'); localStorage.removeItem('lexsuite:filtro-atual'); localStorage.removeItem('lexsuite:agrupar'); } catch (e) {} });
    await p.setViewportSize({ width: 1093, height: 760 }); await espera(800);
    const linha = await p.evaluate(() => { const fx = document.getElementById('filtros-extra'); const rs = [...fx.children].filter(c => !c.hidden && c.offsetParent && c.getBoundingClientRect().width && !c.classList.contains('espaco')).map(c => c.getBoundingClientRect()); return rs.every(r => r.top < rs[0].bottom - 4); });
    confere(linha, 'Notebook (1093 px): a primeira linha dos filtros cabe numa linha só');
    await p.evaluate(() => window.scrollTo(0, 1500)); await espera(500);
    const cp = await p.evaluate(() => { const b_ = document.getElementById('barra-lista'); return { c: b_.classList.contains('compacta'), ord: getComputedStyle(document.getElementById('ordenacao')).display }; });
    await p.evaluate(() => window.scrollTo(0, 0)); await espera(500);
    const volta = await p.evaluate(() => !document.getElementById('barra-lista').classList.contains('compacta'));
    confere(cp.c && cp.ord === 'none' && volta, 'Ao rolar, a barra dos filtros fica numa linha (sem "Ordenar por") e volta inteira ao subir');
    await p.setViewportSize({ width: 1366, height: 900 }); await espera(400);
    // Configurações
    await abrirConfig(p); await espera(900);
    const cf = await p.evaluate(() => { const c = document.getElementById('config'), r = c.getBoundingClientRect(), f = c.querySelector('.painel-rodape').getBoundingClientRect(); const ids = [...c.querySelectorAll('fieldset')].map(x => x.id); const i = ids.indexOf('c-agendar-wrap'); return { larg: Math.abs(f.left - r.left) <= 2 && Math.abs(r.right - f.right) <= 2, ordem: ids.slice(i, i + 3).join(','), aj: !!document.querySelector('#c-l-consulta .ajuda'), x: document.getElementById('c-consulta-x').hidden }; });
    confere(cf.ordem === 'c-agendar-wrap,c-limpeza-wrap,c-arm-wrap', 'Configurações: Rotina de limpeza entre Rotina de leitura e Armazenamento (' + cf.ordem + ')');
    confere(cf.larg, 'Configurações: o rodapé ocupa a largura toda da janela');
    confere(cf.aj && cf.x, 'Configurações: a consulta pública com (?) e sem a frase embaixo');
    await p.evaluate(() => { const i = document.getElementById('c-res-meses'); i.value = '8'; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }); await espera(300);
    confere(await p.evaluate(() => document.getElementById('c-msg').textContent === 'As alterações desta janela passam a valer depois de Salvar.'), 'Configurações: qualquer alteração mostra "As alterações desta janela passam a valer depois de Salvar."');
    await p.evaluate(() => [...document.querySelectorAll('#c-limpeza button')].find(x => /^Limpar agora$/.test(x.textContent)).click()); await espera(300);
    const cc = await p.evaluate(() => { const bt = [...document.querySelectorAll('#c-limpeza button')].filter(x => !x.hidden); const c_ = bt.find(x => /Confirmar a limpeza/.test(x.textContent)); return { tem: !!c_ && bt.some(x => x.textContent === 'Não confirmar'), cor: c_ && getComputedStyle(c_).backgroundColor, msg: document.getElementById('c-limpeza').innerText }; });
    confere(cc.tem && cc.cor === 'rgb(179, 38, 30)' && /Os prazos de 8 e 24 meses passam a valer também nas próximas limpezas/.test(cc.msg), 'Limpeza: "Confirmar a limpeza" em vermelho, "Não confirmar" ao lado e o aviso dos prazos novos');
    await p.evaluate(() => [...document.querySelectorAll('#c-limpeza button')].find(x => x.textContent === 'Não confirmar').click()); await espera(200);
    confere(await p.evaluate(() => [...document.querySelectorAll('#c-limpeza button')].some(x => x.textContent === 'Limpar agora') && ![...document.querySelectorAll('#c-limpeza button')].some(x => !x.hidden && x.textContent === 'Não confirmar')), 'Limpeza: "Não confirmar" desiste sem sair da tela');
    await p.evaluate(() => { const i = document.getElementById('c-res-meses'); i.value = '6'; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }); await espera(200);
    const y0 = await p.evaluate(() => { document.getElementById('c-limpeza').scrollIntoView({ block: 'center' }); return document.getElementById('config').scrollTop; });
    await p.evaluate(() => [...document.querySelectorAll('#c-limpeza button')].find(x => /Ver no Histórico/.test(x.textContent)).click()); await espera(700);
    const fim = await p.evaluate(() => !!document.querySelector('#c-hist .c-voltar-fim'));
    await p.evaluate(() => document.getElementById('c-hist-voltar').click()); await espera(500);
    const y1 = await p.evaluate(() => document.getElementById('config').scrollTop);
    confere(fim && Math.abs(y1 - y0) <= 2, 'Histórico: "← Configurações" também no fim, e a volta é para o mesmo ponto (' + y0 + ' → ' + y1 + ')');
    await p.evaluate(() => document.getElementById('c-registro').click()); await espera(800);
    confere(await p.evaluate(() => !!document.querySelector('#janela .al-copiar-ic') && [...document.querySelectorAll('#janela .botoes button')].some(x => x.textContent === 'Enviar ao suporte')), 'Registro técnico: ícone de copiar e "Enviar ao suporte"');
    confere(p._erros.length === 0, '0.7.50: nenhum erro na página ' + p._erros.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(res.join('\n'));
  console.log(falhas ? `\n${falhas} FALHA(S)` : '\nTUDO OK');
  process.exit(falhas ? 1 : 0);
})().catch(e => { console.log(res.join('\n')); console.log('ERRO NO ROTEIRO:', e.message); process.exit(1); });
