"""0.7.51 (decisão 58 do dono): gera paginas/versoes.html (histórico de versões do site) a partir das Novidades da tela.
Rode depois de mudar as Novidades: python ferramentas/versoes.py && python ferramentas/marca.py"""
import re, json, html
import os
RAIZ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(RAIZ+'/robo/radar_modelo.html',encoding='utf-8').read()
i=s.index('var NOVIDADES = {'); j=s.index('\n  };\n', i)
bloco=s[i:j]
vers=re.findall(r'\n    "(\d+\.\d+\.\d+)": \{', bloco)
def lista(v, lang):
    a=bloco.index('"%s": {'%v); b=bloco.find('\n    "', a+5); seg=bloco[a:b if b>0 else len(bloco)]
    k=seg.index(lang+': ['); seg2=seg[k:]; fim=seg2.index(']')
    itens=re.findall(r'"((?:[^"\\]|\\.)*)"', seg2[:fim])
    return [json.loads('"'+x+'"') for x in itens]
av=open(RAIZ+'/paginas/antivirus.html',encoding='utf-8').read()
head=av[:av.index('<main>')]
head=re.sub(r'<title>.*?</title>','<title>Histórico de versões · {{marca.nome}} · LexSuiteONE</title>',head,flags=re.S)
head=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="O que mudou em cada versão do {{marca.nome}}, da mais nova para a mais antiga.">',head)
def secao(lang):
    out=[]
    for v in vers:
        itens=lista(v,lang)
        out.append(f'<section class="cartao" id="{lang}-{v}"><h2>{"Versão" if lang=="pt" else "Version"} {v}</h2><ul>'+''.join(f'<li>{html.escape(x)}</li>' for x in itens)+'</ul></section>')
    return '\n'.join(out)
main=f'''<main><div class="miolo">
<div id="pt">
<h1>Histórico de versões</h1>
<p class="mudo">O que mudou em cada versão do {{{{marca.nome}}}}, da mais nova para a mais antiga. Dentro do programa, o mesmo texto fica em menu ☰ → Ajuda → <b>Novidades da versão</b>.</p>
{secao("pt")}
</div>
<div id="en" hidden>
<h1>Version history</h1>
<p class="mudo">What changed in each version of {{{{marca.nome}}}}, newest first. Inside the program, the same text is under menu ☰ → Help → <b>What’s new</b>.</p>
{secao("en")}
</div>
</div></main>
'''
foot=av[av.index('<footer>'):]
foot=re.sub(r'\n  \["pt", "en"\]\.forEach\(function \(l\) \{.*?\n  \}\);\n','\n',foot,flags=re.S)
open(RAIZ+'/paginas/versoes.html','w',encoding='utf-8').write(head+main+foot)
print(len(vers), vers[:3], vers[-1])
