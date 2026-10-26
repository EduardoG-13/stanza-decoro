"""Produz o guia prático em HTML, Markdown e PDF, com tokens reutilizáveis."""
from pathlib import Path
import json,html,shutil,hashlib
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
B=json.loads((ROOT/'data/brand.json').read_text(encoding='utf-8'));G=json.loads((ROOT/'data/style-guide.json').read_text(encoding='utf-8'));C=B['colors'];OUT=ROOT/'brand'
def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(values,[.2126,.7152,.0722]))
def contrast(a,b):
    aa,bb=sorted([luminance(a),luminance(b)],reverse=True)
    return (aa+.05)/(bb+.05)
PAIRS=[('Tinta / marfim',C['ink'],C['paper']),('Oliva / branco',C['olive'],'#FFFFFF'),('Secundário / marfim',C['muted'],C['paper'])]
COLOR_NAMES={'ink':'Tinta','olive':'Oliva','oliveDark':'Verde profundo','paper':'Marfim','surface':'Branco quente','soft':'Verde claro','muted':'Texto secundário','line':'Linha','gold':'Dourado de apoio','logoGold':'Dourado do logo'}
for _,a,b in PAIRS:assert contrast(a,b)>=4.5
tokens=':root {\n'+''.join(f'  --stanza-{k}: {v};\n' for k,v in C.items())+'  --stanza-serif: "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;\n  --stanza-sans: "Segoe UI", Arial, sans-serif;\n'+''.join(f'  --stanza-space-{v}: {v}px;\n' for v in G['spacing'])+'  --stanza-radius: 2px;\n  --stanza-touch: 44px;\n}\n'
(OUT/'tokens.css').write_text(tokens,encoding='utf-8')
source=ROOT/'sofas/SOFA-9.png';digest=hashlib.sha256(source.read_bytes()).hexdigest()[:12]
photo=ROOT/'dist-producao/assets/images'/f'{digest}.webp';assert photo.is_file()
shutil.copy2(photo,OUT/'assets/sofa-verde-guia.webp')
md=['# '+G['title'],'',G['subtitle'],'','Versão '+G['version']+' - 26/10/2026','']
for s in G['sections']:
    md+=['## '+s['title'],'',s['intro'],'']+['- '+r for r in s['rules']]+['']
md+=['## Pares de contraste conferidos','']+[f'- {name}: {contrast(a,b):.2f}:1 ({a} sobre {b}).' for name,a,b in PAIRS]+['','## Arquivos reutilizáveis','','- tokens.css: cores, fontes e espaçamentos.','- data/style-guide.json: fonte estruturada deste guia.','- data/brand.json: referência de identidade e contatos.','','Referência de acessibilidade: '+G['reference'],'']
(OUT/'guia-de-estilos.md').write_text('\n'.join(md),encoding='utf-8')
esc=html.escape
palette=''.join(f'<div class="swatch"><span style="background:{v}"></span><strong>{esc(COLOR_NAMES[k])}</strong><code>{v}</code></div>' for k,v in C.items())
examples={
 'direcao':'<div class="split"><div class="sample"><span class="eyebrow">APRESENTAÇÃO</span><h3>Feito para o seu<br><em>jeito de morar.</em></h3><p>Uma fotografia real, uma escolha para começar.</p></div><div class="sample functional"><span class="eyebrow">OPERAÇÃO</span><h3>Orçamentos do site</h3><p>Encontre o projeto e confira o próximo passo.</p><label>Pesquisar por protocolo<input placeholder="Ex.: ST-26-0002"></label></div></div>',
 'tipografia':'<div class="sample"><h3>A peça ganha presença.</h3><p class="type-sample">Texto de interface: claro, próximo e legível.</p><p class="meta">Detalhe útil. Não uma condição escondida.</p></div>',
 'cores':'<div class="palette">'+palette+'</div><div class="ratios">'+''.join(f'<p><strong>{esc(name)}</strong><br>{contrast(a,b):.2f}:1</p>' for name,a,b in PAIRS)+'</div>',
 'layout':'<figure><img class="photo" src="assets/sofa-verde-guia.webp" width="563" height="450" alt="Sofá verde com o ambiente original preservado"><figcaption>A moldura organiza. A peça mantém sua proporção.</figcaption></figure>',
 'componentes':'<div class="sample"><div class="actions"><button type="button" class="primary">Pedir orçamento <span aria-hidden="true">↗</span></button><button type="button" class="secondary">Ver referências</button><button type="button" disabled>Enviando projeto...</button></div><div class="split fields"><label>WhatsApp com DDD<input placeholder="(11) 97556-3037" inputmode="tel"></label><label>Medidas aproximadas <span class="meta">opcional</span><input placeholder="Conte o que já sabe"></label></div><p class="meta">Amostras visuais: estes campos e botões não enviam dados.</p><p class="feedback">Preço, prazo e transporte após avaliação.</p></div>',
 'consistencia':'<div class="sample"><h3>Antes de aprovar.</h3><div class="checklist">'+''.join(f'<label><input type="checkbox"> {esc(t)}</label>' for t in ['A peça continua igual à fotografia original.','O texto explica uma informação real.','A ação principal está clara.','O celular e o teclado foram conferidos.','Cores, logo e fontes seguem a mesma referência.'])+'</div></div>'}
style='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--stanza-paper);color:var(--stanza-ink);font:16px/1.65 var(--stanza-sans)}main{max-width:1160px;margin:auto;padding:48px 32px}h1,h2,h3{font-family:var(--stanza-serif);font-weight:400;line-height:1.08;letter-spacing:-.035em}h1{font-size:clamp(44px,7vw,84px);max-width:850px;margin:34px 0 24px}h2{font-size:clamp(34px,4.4vw,56px);max-width:650px;margin:12px 0 22px}h3{font-size:36px;margin:12px 0 24px}p{color:var(--stanza-muted)}a{color:var(--stanza-olive);text-underline-offset:5px}header>p{max-width:680px}nav{display:flex;gap:16px;flex-wrap:wrap;padding:24px 0}section{border-top:1px solid var(--stanza-line);padding:48px 0}section>p{max-width:760px}.eyebrow{font:600 11px/1.6 var(--stanza-sans);letter-spacing:.13em;color:var(--stanza-olive)}.rules{display:grid;grid-template-columns:1fr 1fr;gap:0 48px;padding:0;list-style:none;counter-reset:rule}.rules li{counter-increment:rule;padding:18px 0;border-bottom:1px solid var(--stanza-line);color:var(--stanza-muted)}.rules li:before{content:counter(rule,decimal-leading-zero);display:block;color:var(--stanza-olive);font-size:12px;margin-bottom:8px}.sample{padding:28px;background:var(--stanza-surface);border:1px solid var(--stanza-line)}.split{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:32px}.functional h3{font:600 25px/1.3 var(--stanza-sans);letter-spacing:normal}.meta,figcaption{font-size:12px;color:var(--stanza-muted)}em{color:var(--stanza-olive)}.palette{display:grid;grid-template-columns:repeat(5,1fr);gap:20px;margin:32px 0}.swatch span{display:block;height:84px;border:1px solid var(--stanza-line);margin-bottom:8px}.swatch strong,.swatch code{display:block;font-size:12px}.ratios{display:flex;gap:32px;flex-wrap:wrap}.photo{display:block;width:100%;max-width:680px;height:auto;margin:24px 0 12px}.actions{display:flex;gap:16px;flex-wrap:wrap;align-items:center}button{font:500 14px var(--stanza-sans);min-height:52px;padding:14px 22px;border:1px solid var(--stanza-olive);border-radius:2px;background:var(--stanza-paper);color:var(--stanza-olive);cursor:pointer}.primary{background:var(--stanza-olive);color:white}.primary:hover{background:var(--stanza-oliveDark)}.primary span{margin-left:20px}button:disabled{opacity:.55;cursor:default}.secondary:hover{background:var(--stanza-soft)}input{font:16px var(--stanza-sans);border:1px solid #7b8475;background:var(--stanza-surface);color:var(--stanza-ink);border-radius:2px;max-width:100%;width:100%;min-height:48px;padding:12px;margin-top:8px}label{font-size:14px}button:focus-visible,input:focus-visible,a:focus-visible{outline:3px solid var(--stanza-olive);outline-offset:4px}.fields{margin-bottom:16px}.feedback{padding:16px;background:var(--stanza-soft);color:var(--stanza-ink)}.checklist{display:grid;gap:14px}.checklist label{display:flex;gap:12px;align-items:center}.checklist input{width:20px;min-height:20px;margin:0}footer{padding:32px 0;border-top:1px solid var(--stanza-line)}@media(max-width:700px){main{padding:28px 20px}.split,.rules{grid-template-columns:1fr}.palette{grid-template-columns:repeat(2,1fr)}.sample{padding:22px}.actions{align-items:stretch;flex-direction:column}section{padding:32px 0}}@media print{nav,.downloads{display:none}main{max-width:none;padding:0}section{break-before:page}section:first-of-type{break-before:auto}.sample,.rules li{break-inside:avoid}body{background:white}}
'''
sections=''.join(f'<section id="{s["id"]}"><span class="eyebrow">{i+1:02d} / APLICAÇÃO</span><h2>{esc(s["title"])}</h2><p>{esc(s["intro"])}</p>{examples[s["id"]]}<ol class="rules">'+''.join(f'<li>{esc(r)}</li>' for r in s['rules'])+'</ol></section>' for i,s in enumerate(G['sections']))
doc=f'<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{G["title"]}</title><link rel="stylesheet" href="tokens.css"><style>{style}</style><main><header><img src="assets/stanza-logo.png" width="150" height="85" alt="Stanza Decoro"><p class="eyebrow">GUIA DE ESTILOS / VERSÃO 1.0 / 26.10.2026</p><h1>Consistência para criar.<br>Personalidade para ficar.</h1><p>{esc(G["subtitle"])}</p><nav>'+''.join(f'<a href="#{s["id"]}">{esc(s["title"])}</a>' for s in G['sections'])+f'</nav><p class="downloads"><a href="guia-de-estilos.pdf">Baixar PDF</a> · <a href="guia-de-estilos.md">Fonte em texto</a> · <a href="tokens.css">Tokens CSS</a> · <a href="index.html">Kit da marca</a></p></header>{sections}<footer><p>Guia prático complementar ao manual da marca. As amostras não enviam dados.</p><a href="{G["reference"]}">Referência: contraste mínimo - W3C</a></footer></main></html>'
(OUT/'guia-de-estilos.html').write_text(doc,encoding='utf-8')

for name,file in [('GSans','segoeui.ttf'),('GSansBold','segoeuib.ttf'),('GSerif','pala.ttf')]:pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
S={
 'title':ParagraphStyle('title',fontName='GSerif',fontSize=33,leading=37,textColor=HexColor(C['ink']),spaceAfter=20),
 'body':ParagraphStyle('body',fontName='GSans',fontSize=10,leading=15,textColor=HexColor(C['ink']),spaceAfter=12),
 'small':ParagraphStyle('small',fontName='GSans',fontSize=8,leading=12,textColor=HexColor(C['muted']),spaceAfter=9),
 'eye':ParagraphStyle('eye',fontName='GSansBold',fontSize=8,leading=12,textColor=HexColor(C['olive']),spaceAfter=18),
 'specimen':ParagraphStyle('specimen',fontName='GSerif',fontSize=37,leading=42,textColor=HexColor(C['ink']),spaceAfter=16),
 'interface':ParagraphStyle('interface',fontName='GSansBold',fontSize=22,leading=28,textColor=HexColor(C['ink']),spaceAfter=18),
 'white':ParagraphStyle('white',fontName='GSansBold',fontSize=10,leading=15,textColor=HexColor('#FFFFFF'),spaceAfter=8),
}
def pp(t,style='body'):return Paragraph(esc(t),S[style])
def bg(c,d):
 c.saveState();c.setFillColor(HexColor(C['paper']));c.rect(0,0,595.28,841.89,stroke=0,fill=1);c.setStrokeColor(HexColor(C['line']));c.line(48,43,547,43);c.setFillColor(HexColor(C['muted']));c.setFont('GSans',7.5);c.drawString(48,28,'STANZA / GUIA DE ESTILOS / 1.0');c.drawRightString(547,28,f'{d.page:02d}');c.restoreState()
story=[]
for i,s in enumerate(G['sections']):
 if i:story.append(PageBreak())
 if i==0:story.extend([Image(str(OUT/'assets/stanza-logo.png'),width=140,height=79,hAlign='LEFT'),Spacer(1,18)])
 story += [pp(f'{i+1:02d} / GUIA DE APLICAÇÃO','eye'),pp(s['title'],'title'),pp(s['intro'])]
 if s['id']=='tipografia':story += [pp('Feito para o seu jeito de morar.','specimen'),pp('Orçamentos do site','interface'),pp('Editorial: Palatino. Interface: Segoe UI. Exemplo de hierarquia, sem representar um pedido real.','small'),Spacer(1,12)]
 if s['id']=='cores':
  rows=[[pp(COLOR_NAMES[k],'small'),pp(v,'small'),''] for k,v in C.items()];t=Table(rows,colWidths=[140,140,219]);sty=[('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
  for j,v in enumerate(C.values()):sty.append(('BACKGROUND',(2,j),(2,j),HexColor(v)))
  t.setStyle(TableStyle(sty));story+=[t,Spacer(1,14),pp(' | '.join(f'{n}: {contrast(a,b):.2f}:1' for n,a,b in PAIRS),'small')]
 if s['id']=='layout':
  from PIL import Image as PI
  with PI.open(OUT/'assets/sofa-verde-guia.webp') as im:w,h=im.size
  sc=min(499/w,235/h);story += [Image(str(OUT/'assets/sofa-verde-guia.webp'),width=w*sc,height=h*sc,hAlign='LEFT'),Spacer(1,8),pp('Ambiente original preservado. A peça mantém sua proporção.','small')]
 if s['id']=='componentes':
  t=Table([[pp('Pedir orçamento','white'),pp('Ver referências'),pp('Enviando...','small')]],colWidths=[166,166,167]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(0,0),HexColor(C['olive'])),('BOX',(0,0),(0,0),.6,HexColor(C['olive'])),('BOX',(1,0),(1,0),.6,HexColor(C['line'])),('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story += [t,Spacer(1,17)]
 for j,r in enumerate(s['rules']):story.append(pp(f'{j+1:02d}  {r}'))
 if i==5:story += [Spacer(1,10),pp('Fontes e reprodução: data/style-guide.json, data/brand.json e scripts/gerar-guia-estilos.py. Amostras interativas em brand/guia-de-estilos.html. Referência de contraste: W3C WCAG 2.2, Contrast (Minimum).','small')]
SimpleDocTemplate(str(OUT/'guia-de-estilos.pdf'),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=65,title=G['title'],author='Stanza Decoro').build(story,onFirstPage=bg,onLaterPages=bg)
print('Guia gerado: HTML, Markdown, PDF e tokens CSS.')
