"""Gera o manual em PDF a partir da fonte editável, sem alterar o logo."""
from pathlib import Path
import re
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]
B = json.loads((ROOT/'data/brand.json').read_text(encoding='utf-8'))
C = {key:HexColor(value) for key,value in B['colors'].items()}
FONTS = Path('C:/Windows/Fonts')
for name,file in [('StanzaSerif','pala.ttf'),('StanzaSerifBold','palab.ttf'),('StanzaSerifItalic','palai.ttf'),('StanzaSans','segoeui.ttf'),('StanzaSansBold','segoeuib.ttf'),('StanzaSansItalic','segoeuii.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONTS/file)))
pdfmetrics.registerFontFamily('StanzaSans',normal='StanzaSans',bold='StanzaSansBold',italic='StanzaSansItalic',boldItalic='StanzaSansBold')
pdfmetrics.registerFontFamily('StanzaSerif',normal='StanzaSerif',bold='StanzaSerifBold',italic='StanzaSerifItalic',boldItalic='StanzaSerifBold')

W,H = 595.28,841.89
M = 48
CW = W-2*M
ST = {
    'eyebrow':ParagraphStyle('eyebrow',fontName='StanzaSansBold',fontSize=8,leading=12,textColor=C['olive'],spaceAfter=18),
    'title':ParagraphStyle('title',fontName='StanzaSerif',fontSize=32,leading=35,textColor=C['ink'],spaceAfter=22),
    'body':ParagraphStyle('body',fontName='StanzaSans',fontSize=10,leading=15.5,textColor=C['ink'],spaceAfter=11),
    'small':ParagraphStyle('small',fontName='StanzaSans',fontSize=8.2,leading=12,textColor=C['muted'],spaceAfter=8),
    'sub':ParagraphStyle('sub',fontName='StanzaSerif',fontSize=19,leading=23,textColor=C['ink'],spaceBefore=12,spaceAfter=12),
    'cover':ParagraphStyle('cover',fontName='StanzaSerif',fontSize=45,leading=48,textColor=C['ink'],spaceAfter=22),
}

def markup(s):
    s=escape(s.strip())
    for a,b in [('&lt;br/&gt;','<br/>'),('&lt;i&gt;','<i>'),('&lt;/i&gt;','</i>')]:s=s.replace(a,b)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`(.+?)`',r'<font color="#40573E">\1</font>',s)
    return s

def p(s,style='body'):
    return Paragraph(markup(s),ST[style])

sections={}
current=None
for line in (ROOT/'brand/manual-da-marca.md').read_text(encoding='utf-8').splitlines():
    found=re.match(r'## (\d+)\. (.*)',line)
    if found:
        current=int(found[1]);sections[current]=[]
    elif current is not None:sections[current].append(line)

def section_body(n):
    content='\n'.join(sections[n]).strip()
    result=[]
    for block in content.split('\n\n'):
        if block.startswith('|'):continue
        if block.startswith('- '):
            for row in block.splitlines():
                result.append(p('• '+row.removeprefix('- ')))
        else:
            result.append(p(block.replace('  \n','<br/>').replace('\n',' ')))
    return result

def heading(k,title):
    return [p(k,'eyebrow'),p(title,'title')]

def photo(path,maxw,maxh):
    with PILImage.open(path) as im:w,h=im.size
    scale=min(maxw/w,maxh/h)
    return Image(str(path),width=w*scale,height=h*scale,hAlign='LEFT')

def footer(c,doc):
    c.saveState()
    c.setFillColor(C['paper']);c.rect(0,0,W,H,stroke=0,fill=1)
    # The background is drawn by onPage, before the page's flowables.
    c.setStrokeColor(C['line']);c.setLineWidth(.5);c.line(M,44,W-M,44)
    c.setFillColor(C['muted']);c.setFont('StanzaSans',7.5)
    c.drawString(M,29,'STANZA DECORO  /  MANUAL DE APLICAÇÃO  /  1.0')
    c.drawRightString(W-M,29,f'{doc.page:02d}')
    c.restoreState()

story=[]
story += [photo(ROOT/B['logo'],140,80),Spacer(1,20),p('IDENTIDADE · COMUNICAÇÃO · EXPERIÊNCIA','eyebrow'),p('A mesma Stanza,<br/>em cada contato.','cover'),p('Manual de aplicação da marca','sub'),p('Um guia para apresentar as peças reais, orientar o atendimento e manter a identidade da empresa no site, nos e-mails e nos próximos materiais.'),Spacer(1,8)]
story += [photo(ROOT/'sofas/SOFA-9.png',CW,190),Spacer(1,12),p('Acervo Stanza · sofá verde com o ambiente original preservado.','small'),Spacer(1,10),p('Versão 1.0 · 26 de outubro de 2026','small')]
story += [PageBreak()]+heading('01 / IDENTIDADE','Próxima da casa.<br/>Clara no atendimento.')+section_body(1)
story += [p('O logo original','sub'),photo(ROOT/B['logo'],155,90),Spacer(1,16)]+section_body(2)
story += [PageBreak()]+heading('02 / COR','Uma base calma.<br/>Um verde que orienta.')
palette=[('Oliva','olive','Ações e destaques'),('Profundo','oliveDark','Contraste e rodapé'),('Marfim','paper','Fundo principal'),('Branco quente','surface','Campos e papel'),('Verde claro','soft','Blocos de apoio'),('Tinta','ink','Texto principal'),('Secundário','muted','Legendas'),('Linha','line','Divisórias'),('Dourado de apoio','gold','Pequenos detalhes'),('Dourado do logo','logoGold','Referência do raster')]
rows=[]
for label,key,role in palette:
    rows.append(['',p(f'**{label}**\n{B["colors"][key]}'),p(role,'small')])
t=Table(rows,colWidths=[65,178,CW-243],hAlign='LEFT')
style=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(1,0),(-1,-1),.4,C['line'])]
for i,(_,key,_) in enumerate(palette):style.append(('BACKGROUND',(0,i),(0,i),C[key]))
t.setStyle(TableStyle(style));story+=[t,Spacer(1,18)]+section_body(3)
story += [PageBreak()]+heading('03 / TIPOGRAFIA E VOZ','Expressiva no título.<br/>Simples na conversa.')
story += [p('Feito para o seu<br/><i>jeito de morar.</i>','title'),p('Palatino Linotype · título de referência','small')]+section_body(4)+[p('Como escrever','sub')]+section_body(7)
story += [PageBreak()]+heading('04 / COMPOSIÇÃO','Cada bloco tem<br/>um propósito.')+section_body(5)
story += [Spacer(1,14)]
example=Table([[p('ESTOFADOS SOB MEDIDA','eyebrow')],[p('Seu espaço.<br/>Suas escolhas.','title')],[p('Mostre uma referência real, explique o que pode ser avaliado e ofereça uma ação clara.')],[p('Pedir orçamento →','body')]],colWidths=[CW])
example.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),C['surface']),('BOX',(0,0),(-1,-1),.6,C['line']),('LEFTPADDING',(0,0),(-1,-1),24),('RIGHTPADDING',(0,0),(-1,-1),24),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]));story+=[example,Spacer(1,14),p('Exemplo de hierarquia, sem criar uma oferta comercial.','small')]
story += [PageBreak()]+heading('05 / FOTOGRAFIA','A peça continua<br/>sendo a mesma.')
images=Table([[photo(ROOT/'sofas/SOFA-9.png',CW*.49,190),photo(ROOT/'acervo/sofa-azul-fundo-claro.png',CW*.49,190)]],colWidths=[CW/2,CW/2])
images.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),8)]));story += [images,Spacer(1,12),p('Verde: ambiente original. Azul: edição de fundo aceita na revisão. As peças não são referência de medidas ou composição interna.','small'),Spacer(1,12)]+section_body(6)
story += [PageBreak()]+heading('06 / E-MAILS','Organização que<br/>facilita o atendimento.')+section_body(8)
story += [p('Anatomia do aviso','sub')]
for label,text in [('01  Marca','Logo original e identificação da solicitação do site.'),('02  Projeto','Protocolo curto, resumo e informações de contato legíveis.'),('03  Próximo passo','Um botão para abrir o projeto no painel privado.'),('04  Assinatura','Nome da empresa, especialidade e canais de atendimento.')]:
    story += [p('**'+label+'** — '+text)]
story += [p('O HTML utiliza tabelas e estilos embutidos, com versão em texto simples. A prévia é um exemplo, sem criar um novo pedido ou enviar mensagens.','small')]
story += [PageBreak()]+heading('07 / APLICAÇÃO','Pronto para usar.<br/>Com revisão antes do envio.')
story += section_body(9)+[p('Arquivos do kit','sub')]+section_body(10)+[p('Revisão final','sub')]+section_body(11)

out=ROOT/'brand/manual-da-marca.pdf'
doc=SimpleDocTemplate(str(out),pagesize=(W,H),rightMargin=M,leftMargin=M,topMargin=48,bottomMargin=65,title='Stanza Decoro — Manual de aplicação da marca',author='Stanza Decoro',subject='Identidade, fotografia, linguagem e e-mails · versão 1.0')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
