"""Compila páginas estáticas e cópias otimizadas, preservando fotos originais."""
from pathlib import Path
from datetime import date
from html import escape
from urllib.parse import quote
import hashlib
import json
import shutil
import sys
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
CONFIG = json.loads((ROOT / 'site.config.json').read_text(encoding='utf-8'))
LOCAL_CONFIG = ROOT / 'site.config.local.json'
if LOCAL_CONFIG.exists():
    local = json.loads(LOCAL_CONFIG.read_text(encoding='utf-8'))
    assert set(local).issubset({'quote'}), 'A configuração local aceita apenas quote.'
    CONFIG.update(local)
assert CONFIG['quote']['mode'] in ['manual','emulator','firebase']
assert not (CONFIG['production'] and CONFIG['quote']['mode'] == 'emulator'), 'Demonstração local não pode ser publicada.'
CATALOG = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
PORTFOLIO = json.loads((ROOT / 'data/portfolio.json').read_text(encoding='utf-8'))
FAMILIES = {'sofas':'Sofás','assentos':'Poltronas e assentos','complementos':'Cabeceiras e puffs','revestimentos':'Capas e cortinas'}
images = {}

def image_url(source):
    if source in images:
        return images[source]
    path = ROOT / source
    assert path.is_file(), source
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    target = OUT / 'assets/images' / (digest + '.webp')
    if not target.exists():
        with Image.open(path) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
            image.thumbnail((1280,1280))
            image.save(target, 'WEBP', quality=84, method=6)
    images[source] = '/assets/images/' + target.name
    return images[source]

def reference(item):
    url = '/modelos/' + item['id'] + '.html'
    return f'''<article class="reference" data-family="{escape(item['family'])}"><a class="reference-image" href="{url}" aria-label="Conhecer {escape(item['name'])}"><img src="{image_url(item['source'])}" alt="{escape(item['alt'])}" width="800" height="1000" loading="lazy" decoding="async"></a><div class="reference-copy"><span class="eyebrow">{escape(item['label'])}</span><h3><a href="{url}">{escape(item['name'])}</a></h3><p>{escape(item['description'])}</p><a class="text-link" href="{url}">Explorar referência <span aria-hidden="true">→</span></a></div></article>'''

def project(item, compact=False):
    action = '' if compact else f'<a class="text-link" href="/orcamento.html?projeto={item["id"]}">Conversar sobre esta referência →</a>'
    return f'''<figure data-family="{escape(item['family'])}"><img src="{image_url(item['source'])}" alt="{escape(item['alt'])}" width="800" height="600" loading="lazy" decoding="async"><figcaption>{escape(item['title'])}</figcaption>{action}</figure>'''

def replace(text, mapping):
    for key, value in mapping.items():
        text = text.replace('@@' + key + '@@', str(value))
    return text

def availability():
    notice = CONFIG['availability']
    today = date.today().isoformat()
    if not notice['enabled'] or (notice['startsOn'] and today < notice['startsOn']) or (notice['endsOn'] and today > notice['endsOn']):
        return ''
    return '<div class="availability">' + escape(notice['text']) + '</div>'

def render(page, path, title, description, content, image=None):
    layout = (ROOT / 'templates/layout.html').read_text(encoding='utf-8')
    defaults = {key:'' for key in ['NAV_CUSTOM','NAV_REFORM','NAV_MODELS','NAV_PORTFOLIO']}
    active = {'custom':'NAV_CUSTOM','reform':'NAV_REFORM','models':'NAV_MODELS','model':'NAV_MODELS','portfolio':'NAV_PORTFOLIO'}
    if page in active:
        defaults[active[page]] = 'aria-current="page"'
    rendered = replace(layout, {**defaults,'TITLE':escape(title),'DESCRIPTION':escape(description),'ROBOTS':'index,follow' if CONFIG['production'] else 'noindex,nofollow','CANONICAL':CONFIG['url'] + '/' + path,'OG_IMAGE':CONFIG['url'] + (image or image_url('sofas/SOFA-2.jpg')),'PAGE':page,'WHATSAPP':CONFIG['whatsapp'],'NOTICE':availability(),'WHATSAPP_URL':'https://wa.me/' + CONFIG['whatsapp'] + '?text=' + quote('Olá, Stanza! Gostaria de conversar sobre um projeto.'),'PHONE':escape(CONFIG['phoneDisplay']),'EMAIL':escape(CONFIG['email']),'YEAR':date.today().year,'CONTENT':content})
    rendered = replace(rendered, {'EMAIL':escape(CONFIG['email']),'PHONE':escape(CONFIG['phoneDisplay']),'WHATSAPP_URL':'https://wa.me/' + CONFIG['whatsapp'] + '?text=' + quote('Olá, Stanza! Gostaria de conversar sobre um projeto.')})
    assert '@@' not in rendered, path
    rendered = '\n'.join(line.rstrip() for line in rendered.splitlines()) + '\n'
    target = OUT / path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(rendered,encoding='utf-8')
    # O repositório original é estático: manter seus pontos de entrada utilizáveis.
    source_entry = ROOT / path
    source_entry.parent.mkdir(parents=True,exist_ok=True)
    source_entry.write_text(rendered,encoding='utf-8')

def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'assets/images').mkdir(parents=True,exist_ok=True)
    assert len({item['id'] for item in CATALOG}) == len(CATALOG)
    assert len({item['id'] for item in PORTFOLIO}) == len(PORTFOLIO)
    for file in ['site.css','app.js','quote-api.js']:
        shutil.copy2(ROOT / 'assets' / file, OUT / 'assets' / file)
    shutil.copy2(ROOT / 'icon/Logo Stanza Decoro Grande.png', OUT / 'assets/images/stanza-logo.png')
    shutil.copytree(ROOT / 'icon', OUT / 'icon', dirs_exist_ok=True)
    # Corrige os endereços dos ícones no manifesto original, sem trocar a marca.
    manifest = {'name':'Stanza Decoro','short_name':'Stanza','icons':[{'src':'/icon/android-chrome-192x192.png','sizes':'192x192','type':'image/png'},{'src':'/icon/android-chrome-512x512.png','sizes':'512x512','type':'image/png'}],'theme_color':'#3e573e','background_color':'#f5f3ed','display':'browser'}
    for icon in manifest['icons']:
        assert (ROOT / icon['src'].lstrip('/')).exists(),icon['src']
    (OUT / 'icon/site.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT / 'icon/site.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    common = {'HERO_IMAGE':image_url('sofas/SOFA-2.jpg'),'DETAIL_IMAGE':image_url('sofas/SOFA-9.2.png'),'REFORM_IMAGE':image_url('poltronas/poltronas-11.jpg'),'FEATURED':''.join(reference(item) for item in CATALOG if item['featured']),'CATALOG':''.join(reference(item) for item in CATALOG),'PORTFOLIO':''.join(project(item) for item in PORTFOLIO),'HOME_PROJECTS':''.join(project(item,True) for item in [PORTFOLIO[2],PORTFOLIO[20],PORTFOLIO[30]])}
    states = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
    common['STATES'] = '<option value="">Selecione</option>' + ''.join(f'<option>{state}</option>' for state in states)
    pages = [
      ('home','index.html','home.html','Stanza Decoro — estofados sob medida e reformas','Estofados feitos para o seu espaço. Explore referências de sofás, poltronas e cabeceiras e converse sobre fabricação ou reforma.'),
      ('models','modelos.html','models.html','Modelos e referências | Stanza Decoro','Sofás, poltronas, cabeceiras e puffs como referências para o seu projeto. Medidas e acabamentos sob avaliação.'),
      ('custom','sob-medida.html','custom.html','Estofados sob medida | Stanza Decoro','Conte sua ideia de sofá, poltrona, cabeceira ou outro estofado. Modelos e medidas especiais sujeitos à avaliação técnica.'),
      ('reform','reformas.html','reform.html','Reforma de estofados | Stanza Decoro','Converse sobre a reforma da sua peça. Fotos, referências e informações de acesso ajudam na avaliação.'),
      ('portfolio','portfolio.html','portfolio.html','Portfólio de peças e ambientes | Stanza Decoro','Explore as 46 referências do acervo Stanza, entre sofás, assentos, complementos e revestimentos.'),
      ('quote','orcamento.html','quote.html','Planejar meu projeto | Stanza Decoro','Prepare as informações de fabricação ou reforma e continue o atendimento da Stanza no WhatsApp.'),
      ('privacy','privacidade.html','privacy.html','Privacidade | Stanza Decoro','Entenda como funciona a preparação do resumo e o atendimento pelos canais da Stanza.')
    ]
    paths = []
    for page,path,source,title,description in pages:
        content = replace((ROOT / 'pages' / source).read_text(encoding='utf-8'),common)
        if page == 'quote':
            content += '<script type="application/json" id="quote-config">' + json.dumps(CONFIG['quote'],ensure_ascii=False).replace('<','\\u003c') + '</script>'
            if CONFIG['quote']['mode'] != 'manual':
                content = content.replace('Prepare as informações do projeto e continue a conversa com a Stanza no WhatsApp.', 'Envie seu projeto e suas fotos para a equipe avaliar. Depois, continue a conversa pelo WhatsApp.')
                content = content.replace('As fotos ficam neste dispositivo. Você poderá anexá-las diretamente na conversa do WhatsApp.', 'As fotos ficam no dispositivo até você confirmar o envio. Depois, a equipe da Stanza poderá consultá-las no atendimento privado.')
            if CONFIG['quote']['mode'] == 'emulator':
                content = '<div class="availability">Demonstração local: use dados fictícios. Nenhum e-mail será enviado à Stanza.</div>' + content
        if page == 'privacy':
            content = replace(content,{'QUOTE_PRIVACY':('O formulário prepara o resumo no seu navegador. O site não grava os dados de contato e não recebe as fotos selecionadas.' if CONFIG['quote']['mode']=='manual' else 'Após você confirmar o envio, os dados e fotos ficam registrados no atendimento privado da Stanza. O protocolo confirma o registro; preço e prazo dependem de avaliação.'),'PHOTO_PRIVACY':('As fotos precisam ser anexadas na conversa.' if CONFIG['quote']['mode']=='manual' else 'As fotos enviadas são preparadas para avaliação, com redução de tamanho e remoção de metadados como localização. Os originais não são conservados por este formulário.'),'STORAGE_PRIVACY':('O registro pelo site está desativado nesta versão.' if CONFIG['quote']['mode']=='manual' else 'O registro utiliza Firebase/Google Cloud para armazenamento privado e proteção de envio. Somente administrador ou secretária autorizados consultam o atendimento. Um aviso com o resumo pode ser enviado ao e-mail da Stanza; as fotos ficam fora desse aviso. Rascunhos expiram após uma hora; a limpeza é agendada. Pedidos concluídos permanecem no atendimento até a revisão da conservação pela empresa. Para solicitar correção ou exclusão, use o contato abaixo. O envio não autoriza publicidade.')})
        if page == 'quote':
            lookup = {item['id']:{'name':item['name'],'piece':('Poltrona' if item['family']=='assentos' else 'Cabeceira' if 'cabeceira' in item['id'] else 'Puff' if 'puff' in item['id'] else 'Sofá')} for item in CATALOG}
            content += '<script type="application/json" id="catalog-references">' + json.dumps(lookup,ensure_ascii=False).replace('<','\\u003c') + '</script>'
        render(page,path,title,description,content)
        paths.append(path)
    for item in CATALOG:
        related = [other for other in CATALOG if other['id'] != item['id']][:4]
        content = replace((ROOT / 'pages/model.html').read_text(encoding='utf-8'),{'MODEL_IMAGE':image_url(item['source']),'MODEL_ALT':escape(item['alt']),'MODEL_LABEL':escape(item['label']),'MODEL_NAME':escape(item['name']),'MODEL_DESCRIPTION':escape(item['description']),'MODEL_ID':item['id'],'RELATED':''.join(reference(other) for other in related)})
        path = 'modelos/' + item['id'] + '.html'
        render('model',path,item['name']+' | Stanza Decoro',item['description'],content,image_url(item['source']))
        paths.append(path)
    # Preserva também o acesso divulgado sem extensão: /portfolio.
    (OUT / 'portfolio').mkdir(exist_ok=True)
    shutil.copy2(OUT / 'portfolio.html', OUT / 'portfolio/index.html')
    (OUT / 'robots.txt').write_text('User-agent: *\n' + ('Allow: /\n' if CONFIG['production'] else 'Disallow: /\n') + 'Sitemap: '+CONFIG['url']+'/sitemap.xml\n',encoding='utf-8')
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+CONFIG['url']+'/'+path+'</loc></url>' for path in paths)+'</urlset>\n',encoding='utf-8')
    (OUT / 'assets/build-info.json').write_text(json.dumps({'catalogCount':len(CATALOG),'portfolioCount':len(PORTFOLIO),'production':CONFIG['production'],'date':date.today().isoformat()},indent=2),encoding='utf-8')
    # Permite prévia na raiz, além da pasta de publicação dist.
    shutil.copytree(OUT / 'assets/images', ROOT / 'assets/images', dirs_exist_ok=True)
    totals = sum(p.stat().st_size for p in (OUT/'assets/images').glob('*'))
    print(f'{len(paths)} páginas, {len(CATALOG)} modelos e {len(PORTFOLIO)} referências. Imagens web: {totals/1024/1024:.2f} MB.')

if __name__ == '__main__':
    main()
