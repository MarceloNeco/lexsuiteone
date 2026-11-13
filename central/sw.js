/* Central LexSuiteONE: cópia do aplicativo no aparelho (não guarda dado nenhum: os dados vêm sempre da nuvem).
   Código com rede primeiro; sem rede, abre a cópia. O cache tem o nome do app e só ele é apagado. */
var VERSAO = "0.1.0", NOME = "central-lexsuiteone-" + VERSAO;
var ARQUIVOS = ["./", "index.html", "central.css", "central.js", "central-config.js", "manifest.json", "icone.svg"];
self.addEventListener("install", function (e) { e.waitUntil(caches.open(NOME).then(function (c) { return c.addAll(ARQUIVOS); })); self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k.indexOf("central-lexsuiteone-") === 0 && k !== NOME; }).map(function (k) { return caches.delete(k); })); }));
  self.clients.claim();
});
self.addEventListener("fetch", function (e) {
  var u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;  // a nuvem (Supabase) nunca passa pelo cache
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then(function (r) {
    var c = r.clone(); caches.open(NOME).then(function (cc) { cc.put(e.request, c); }); return r;
  }).catch(function () { return caches.match(e.request).then(function (r) { return r || caches.match("index.html"); }); }));
});
