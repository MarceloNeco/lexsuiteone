/* Central LexSuiteONE: o único arquivo que muda por ambiente. Endereço do Supabase da plataforma e a chave PÚBLICA
   (publishable): não é segredo; quem protege os dados é o banco (RLS e as funções admin_*, que conferem a equipe). */
window.CENTRAL_CFG = {
  supabase: "https://qvdvkqydhnadhewcidia.supabase.co",
  chavePublica: "sb_publishable_oRJmeUwlBbOP_HoOXf0xLw_4O8v43EA",
  versao: "0.1.0",
  rootify: "https://solverone.com.br/rootify-one/#/b2b/lexsuiteone",
  inatividadeMin: 15
};
