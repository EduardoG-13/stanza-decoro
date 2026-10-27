"""Compila páginas estáticas e cópias otimizadas, preservando fotos originais."""
from pathlib import Path
from datetime import date
from html import escape
from urllib.parse import quote
import hashlib
import json
import shutil
import sys
import argparse
import os
import tomllib
from PIL import Image, ImageOps

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ignore-local-config', action='store_true', help='Gerar a versão padrão sem alterar a configuração local da demonstração.')
parser.add_argument('--config-file', help='Arquivo de configuração para uma geração separada.')
parser.add_argument('--output', default='dist', help='Pasta de saída dentro do projeto.')
parser.add_argument('--no-source-entries', action='store_true', help='Não atualizar as páginas de entrada do projeto.')
parser.add_argument('--production', action='store_true', help='Gerar a publicação oficial com indexação habilitada.')
ARGS = parser.parse_args()
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]
OUT = (ROOT / ARGS.output).resolve()
assert OUT.is_relative_to(ROOT) and OUT != ROOT, 'A saída deve ficar dentro do projeto.'
CONFIG = json.loads((ROOT / (ARGS.config_file or 'site.config.json')).read_text(encoding='utf-8'))
LOCAL_CONFIG = ROOT / 'site.config.local.json'
if LOCAL_CONFIG.exists() and not ARGS.ignore_local_config and not ARGS.config_file:
    local = json.loads(LOCAL_CONFIG.read_text(encoding='utf-8'))
    assert set(local).issubset({'quote'}), 'A configuração local aceita apenas quote.'
    CONFIG.update(local)
if ARGS.production:
    CONFIG['production'] = True
assert CONFIG['quote']['mode'] in ['manual','emulator','firebase']
assert not (CONFIG['production'] and CONFIG['quote']['mode'] == 'emulator'), 'Demonstração local não pode ser publicada.'
CATALOG = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
PORTFOLIO = json.loads((ROOT / 'data/portfolio.json').read_text(encoding='utf-8'))
# 3D model registry (EXT queue). Only models whose assets exist may be listed with assets.
MODELS_3D = json.loads((ROOT / 'data/models-3d.json').read_text(encoding='utf-8'))
STUDY_OPTIONS = json.loads((ROOT / 'data/sofa-pilot.json').read_text(encoding='utf-8'))
REGION_NAMES = {'body','decorative','contrast','exterior-structure'}

def validate_models_3d():
    """Registry consistency (models3d pipeline): ids, files, sha256/bytes/revision against each
    model manifest, regions and options. Returns {catalogId: model} of VERIFIED models."""
    catalog_ids = {item['id'] for item in CATALOG}; portfolio_ids = {item['id'] for item in PORTFOLIO}
    seen = set(); verified = {}
    statuses = set(MODELS_3D.get('verifiedStatuses', ['technical-validated-visual-review-pending','approved']))
    for model in MODELS_3D['models']:
        mid = model['modelId']; assert mid not in seen, mid; seen.add(mid)
        assert model['catalogId'] in catalog_ids, mid
        assert model.get('portfolioId') in (None, *portfolio_ids), (mid, model.get('portfolioId'))
        for key in ('main','mobile','poster','manifest'):
            assert (ROOT / model['assets'][key].lstrip('/')).is_file(), (mid, key)
        manifest_path = ROOT / model['assets']['manifest'].lstrip('/')
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        assert manifest['modelId'] == mid and manifest['revision'] == model['revision'], (mid, 'manifest identity/revision')
        for variant in ('main','mobile'):
            glb = ROOT / model['assets'][variant].lstrip('/'); data = glb.read_bytes()
            entry = manifest['models'][variant]
            assert (manifest_path.parent / entry['uri']).resolve() == glb.resolve(), (mid, variant, 'uri')
            assert hashlib.sha256(data).hexdigest() == entry['sha256'] and len(data) == entry['bytes'], (mid, variant, 'sha256/bytes')
            assert data[:4] == b'glTF' and int.from_bytes(data[8:12],'little') == len(data), (mid, variant, 'GLB header')
        assert set(model['materialRegions']) <= REGION_NAMES and model['materialRegions'].get('body'), mid
        opts = model['options']
        assert opts['appliesTo'] == 'body', mid
        assert set(opts['fabrics']) <= set(STUDY_OPTIONS['fabrics']) and set(opts['colors']) <= set(STUDY_OPTIONS['colors']), mid
        assert opts['default']['fabricId'] in opts['fabrics'] and opts['default']['colorId'] in opts['colors'], mid
        for fabric in opts['fabrics']:
            folder = MODELS_3D.get('materialLibrary', {}).get(fabric, model['assets']['viewerBase'] + 'materials/' + fabric + '/')
            for name in ('basecolor.jpg','normal.png','roughness.jpg'):
                assert (ROOT / folder.lstrip('/') / name).is_file(), (mid, fabric, name)
        if model['status'] in statuses:
            assert model['catalogId'] not in verified, ('one verified 3D study per catalog item', model['catalogId'])
            verified[model['catalogId']] = model
    assert MODELS_3D['defaultModelId'] in seen
    return verified

VERIFIED_3D = validate_models_3d()

def model_experience(item):
    """'Ver em 3D' entry on the product page ONLY for a registered and verified 3D study."""
    model = VERIFIED_3D.get(item['id'])
    if not model: return ''
    href = '/explorar-sofa.html' if model['modelId'] == MODELS_3D['defaultModelId'] else '/explorar-sofa.html?modelo=' + quote(model['modelId'])
    return f'<a class="text-link model-experience-link" href="{escape(href,quote=True)}" data-model-3d="{escape(model["modelId"],quote=True)}">Ver em 3D e experimentar cores e tecidos ↗</a>'
FAMILIES = {'sofas':'Sofás','assentos':'Poltronas e assentos','complementos':'Cabeceiras e puffs','revestimentos':'Capas e cortinas','cortinas':'Cortinas'}
images = {}
image_sizes = {}
reference_thumbnails = {}

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
    with Image.open(target) as exported:
        image_sizes[source] = exported.size
    images[source] = '/assets/images/' + target.name
    return images[source]


def reference_thumbnail(source):
    if source in reference_thumbnails:
        return reference_thumbnails[source]
    path = (ROOT / source).resolve()
    assert path.is_relative_to(ROOT) and path.is_file(), source
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    target = OUT / 'assets/images' / (digest + '-ref480.webp')
    if not target.exists():
        with Image.open(path) as original:
            thumb = ImageOps.exif_transpose(original).convert('RGB')
            thumb.thumbnail((480,360))
            thumb.save(target,'WEBP',quality=82,method=6)
    reference_thumbnails[source] = '/assets/images/' + target.name
    return reference_thumbnails[source]

def quote_reference(item, portfolio=False):
    return {'name':item['title'] if portfolio else item['name'],'piece':item['piece'],
            'image':reference_thumbnail(item['source']),'alt':item['alt']}


def reference(item):
    url = '/modelos/' + item['id'] + '.html'
    search = escape(' '.join([item['name'],item['description'],item['piece']]),quote=True)
    return f'''<article class="reference" data-family="{escape(item['family'])}" data-search="{search}"><a class="reference-link" href="{url}" aria-label="Conhecer {escape(item['name'])}"><div class="reference-image"><img src="{image_url(item['source'])}" alt="{escape(item['alt'])}" width="800" height="1000" loading="lazy" decoding="async"><span class="reference-open" aria-hidden="true">↗</span></div><div class="reference-copy"><h3>{escape(item['name'])}</h3><p>{escape(item['description'])}</p><span class="text-link">Conhecer a peça <span aria-hidden="true">→</span></span></div></a></article>'''


def project(item, compact=False):
    action = ''  # The enlarged photo carries its contextual quote action.
    search = escape(item['title']+' '+item['alt'],quote=True)
    return f'''<figure data-family="{escape(item['family'])}" data-search="{search}"><a class="project-photo" href="{image_url(item['source'])}" data-photo data-photo-group="portfolio" data-photo-caption="{escape(item['title'],quote=True)}" data-photo-quote="/orcamento.html?projeto={item['id']}" aria-label="Ampliar: {escape(item['title'],quote=True)}"><img src="{image_url(item['source'])}" alt="{escape(item['alt'])}" width="800" height="600" loading="lazy" decoding="async"><span class="photo-enlarge">Ver foto <span aria-hidden="true">↗</span></span></a><figcaption>{escape(item['title'])}</figcaption>{action}</figure>'''

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
    defaults = {key:'' for key in ['NAV_CUSTOM','NAV_REFORM','NAV_MODELS','NAV_PORTFOLIO','NAV_ABOUT']}
    active = {'about':'NAV_ABOUT','custom':'NAV_CUSTOM','reform':'NAV_REFORM','models':'NAV_MODELS','model':'NAV_MODELS','portfolio':'NAV_PORTFOLIO'}
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
    if not ARGS.no_source_entries:
        source_entry = ROOT / path
        source_entry.parent.mkdir(parents=True,exist_ok=True)
        source_entry.write_text(rendered,encoding='utf-8')

def main():
    OUT.mkdir(exist_ok=True)
    # Inclui as regras no próprio pacote, inclusive em publicação de arquivos pré-compilados.
    hosting=tomllib.loads((ROOT/'netlify.toml').read_text(encoding='utf-8'))
    redirects=[f"{r['from']} {r['to']} {r['status']}{'!' if r.get('force') else ''}" for r in hosting.get('redirects',[])]
    (OUT/'_redirects').write_text('\n'.join(redirects)+'\n',encoding='utf-8')
    (OUT / 'assets/images').mkdir(parents=True,exist_ok=True)
    assert len({item['id'] for item in CATALOG}) == len(CATALOG)
    assert len({item['id'] for item in PORTFOLIO}) == len(PORTFOLIO)
    for file in ['site.css','app.js','quote-api.js','quote-fields.js','quote-message.js','quote-redirect.js','sofa-experience.css','sofa-experience.js','home-opening.js']:
        shutil.copy2(ROOT / 'assets' / file, OUT / 'assets' / file)
    cities = json.loads((ROOT/'data/cities-br.json').read_text(encoding='utf-8'))['states']
    assert len(cities) == 27
    (OUT/'assets/cities').mkdir(exist_ok=True)
    for uf, data in cities.items():
        assert len(uf) == 2 and uf.isalpha() and uf.isupper() and data['cities']
        (OUT/'assets/cities'/f'{uf}.json').write_text(json.dumps(data['cities'],ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    shutil.copy2(ROOT / 'icon/Logo Stanza Decoro Grande.png', OUT / 'assets/images/stanza-logo.png')
    shutil.copytree(ROOT / 'icon', OUT / 'icon', dirs_exist_ok=True)
    # Clean copy: files removed from the package (e.g. the 1.x layer/scroll adapter) must not linger.
    shutil.rmtree(OUT / 'assets/sofa-pilot', ignore_errors=True)
    shutil.copytree(ROOT / 'assets/sofa-pilot', OUT / 'assets/sofa-pilot', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'data/models-3d.json', OUT / 'assets/models-3d.json')
    # models3d pipeline: publish only what the viewer needs (GLBs, posters, manifests, shared maps);
    # the parametric sources, derived .blend files and the Blender library stay in the repository.
    shutil.rmtree(OUT / 'assets/models-3d', ignore_errors=True)
    shutil.copytree(ROOT / 'assets/models-3d', OUT / 'assets/models-3d', ignore=shutil.ignore_patterns('source','lib','*.py','__pycache__','*.blend','*.blend1'))
    # Corrige os endereços dos ícones no manifesto original, sem trocar a marca.
    manifest = {'name':'Stanza Decoro','short_name':'Stanza','icons':[{'src':'/icon/android-chrome-192x192.png','sizes':'192x192','type':'image/png'},{'src':'/icon/android-chrome-512x512.png','sizes':'512x512','type':'image/png'}],'theme_color':'#3e573e','background_color':'#f5f3ed','display':'browser'}
    for icon in manifest['icons']:
        assert (ROOT / icon['src'].lstrip('/')).exists(),icon['src']
    (OUT / 'icon/site.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    if not ARGS.no_source_entries:
        (ROOT / 'icon/site.webmanifest').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    common = {'ABOUT_IMAGE':image_url('acervo/sofa-dois-assentos.webp'),'PIPING_IMAGE':image_url('acervo/sofa-com-vivo.webp'),'PIPING_WIDTH':image_sizes['acervo/sofa-com-vivo.webp'][0],'PIPING_HEIGHT':image_sizes['acervo/sofa-com-vivo.webp'][1],'HERO_IMAGE':image_url('sofas/SOFA-2.jpg'),'DETAIL_IMAGE':image_url('sofas/SOFA-9.2.png'),'REFORM_IMAGE':image_url('poltronas/poltronas-11.jpg'),'FEATURED':''.join(reference(item) for item in CATALOG if item['featured']),'CATALOG':''.join(reference(item) for item in CATALOG),'PORTFOLIO':''.join(project(item) for item in PORTFOLIO),'HOME_PROJECTS':''.join(project(item,True) for item in [next(p for p in PORTFOLIO if p['id']==key) for key in ['projeto-3','projeto-21','projeto-48']]),'CATALOG_COUNT':len(CATALOG),'PORTFOLIO_COUNT':len(PORTFOLIO)}
    states = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
    common['STATES'] = '<option value="">Selecione</option>' + ''.join(f'<option>{state}</option>' for state in states)
    pages = [
      ('home','index.html','home.html','Stanza Decoro — estofados sob medida e reformas','Estofados feitos para o seu espaço. Explore referências de sofás, poltronas e cabeceiras e converse sobre fabricação ou reforma.'),
      ('about','a-stanza.html','about.html','A Stanza Decoro | Sob medida e reformas','Conheça como a Stanza organiza projetos de fabricação sob medida e reforma, da ideia ao acabamento e ao transporte.'),
      ('materials','tecidos-e-acabamentos.html','materials.html','Tecidos e acabamentos | Stanza Decoro','Cor, textura, costuras e detalhes para conversar sobre a sua peça. Veja referências reais e o que confirmar antes da escolha.'),
      ('models','modelos.html','models.html','Modelos e referências | Stanza Decoro','Sofás, poltronas, cabeceiras e puffs como referências para o seu projeto. Medidas e acabamentos sob avaliação.'),
      ('custom','sob-medida.html','custom.html','Estofados sob medida | Stanza Decoro','Conte sua ideia de sofá, poltrona, cabeceira ou outro estofado. Modelos e medidas especiais sujeitos à avaliação técnica.'),
      ('reform','reformas.html','reform.html','Reforma de estofados | Stanza Decoro','Converse sobre a reforma da sua peça. Fotos, referências e informações de acesso ajudam na avaliação.'),
      ('portfolio','portfolio.html','portfolio.html','Portfólio de peças e ambientes | Stanza Decoro','Explore referências do acervo Stanza, entre sofás, assentos, complementos e revestimentos.'),
      ('explore','explorar-sofa.html','explore.html','Explore um estudo de sofá em 3D | Stanza Decoro','Gire um estudo 3D do sofá orgânico e experimente cores e tecidos no corpo da peça. Acabamentos ilustrativos para conversar sobre o seu projeto.'),
      ('quote','orcamento.html','quote.html','Planejar meu projeto | Stanza Decoro','Prepare as informações de fabricação ou reforma e continue o atendimento da Stanza no WhatsApp.'),
      ('privacy','privacidade.html','privacy.html','Privacidade | Stanza Decoro','Entenda como funciona a preparação do resumo e o atendimento pelos canais da Stanza.')
    ]
    paths = []
    for page,path,source,title,description in pages:
        if page == 'quote' and CONFIG['quote'].get('hostedUrl'):
            source='quote-handoff.html'
        content = replace((ROOT / 'pages' / source).read_text(encoding='utf-8'),{**common,'QUOTE_HOSTED_URL':escape(CONFIG['quote'].get('hostedUrl',''),quote=True)})
        if page in ['quote','explore']:
            content += '<script type="application/json" id="sofa-options">' + (ROOT / 'data/sofa-pilot.json').read_text(encoding='utf-8').replace('<','\\u003c') + '</script>'
        if page == 'explore':
            content += '<script type="application/json" id="models-3d">' + json.dumps(MODELS_3D,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c') + '</script>'
        if page == 'quote':
            content += '<script type="application/json" id="quote-config">' + json.dumps(CONFIG['quote'],ensure_ascii=False).replace('<','\\u003c') + '</script>'
            if CONFIG['quote']['mode'] != 'manual' or CONFIG['quote'].get('hostedUrl'):
                content = content.replace('Prepare as informações do projeto e continue a conversa com a Stanza no WhatsApp.', 'Envie seu projeto e suas fotos para a equipe avaliar. Depois, continue a conversa pelo WhatsApp.')
                content = content.replace('As fotos ficam neste dispositivo. Você poderá anexá-las diretamente na conversa do WhatsApp.', 'As fotos ficam no dispositivo até você confirmar o envio. Depois, a equipe da Stanza poderá consultá-las no atendimento privado.')
            if CONFIG['quote']['mode'] == 'emulator':
                content = '<div class="availability">Demonstração local: use dados fictícios. Nenhum e-mail será enviado à Stanza.</div>' + content
        if page == 'privacy':
            content = replace(content,{'QUOTE_PRIVACY':('O formulário prepara o resumo no seu navegador. O site não grava os dados de contato e não recebe as fotos selecionadas.' if (CONFIG['quote']['mode']=='manual' and not CONFIG['quote'].get('hostedUrl')) else 'Após você confirmar o envio, os dados e fotos ficam registrados no atendimento privado da Stanza. O protocolo confirma o registro; preço e prazo dependem de avaliação.'),'PHOTO_PRIVACY':('As fotos precisam ser anexadas na conversa.' if (CONFIG['quote']['mode']=='manual' and not CONFIG['quote'].get('hostedUrl')) else 'As fotos enviadas são preparadas para avaliação, com redução de tamanho e remoção de metadados como localização. Os originais não são conservados por este formulário.'),'STORAGE_PRIVACY':('O registro pelo site está desativado nesta versão.' if (CONFIG['quote']['mode']=='manual' and not CONFIG['quote'].get('hostedUrl')) else 'O registro utiliza Firebase/Google Cloud para armazenamento privado e proteção de envio. Somente administrador ou secretária autorizados consultam o atendimento. Um aviso com o resumo pode ser enviado ao e-mail da Stanza; as fotos ficam fora desse aviso. Rascunhos expiram após uma hora; a limpeza é agendada. Pedidos concluídos permanecem no atendimento até a revisão da conservação pela empresa. Para solicitar correção ou exclusão, use o contato abaixo. O envio não autoriza publicidade.')})
        if page == 'quote':
            lookup = {item['id']:{'name':item['name'],'piece':item['piece']} for item in CATALOG}
            if not CONFIG['quote'].get('hostedUrl'):
                lookup = {item['id']:quote_reference(item) for item in CATALOG}
                projects = {item['id']:quote_reference(item,True) for item in PORTFOLIO}
                content += '<script type="application/json" id="portfolio-projects">' + json.dumps(projects,ensure_ascii=False).replace('<','\\u003c') + '</script>'
            content += '<script type="application/json" id="catalog-references">' + json.dumps(lookup,ensure_ascii=False).replace('<','\\u003c') + '</script>'
        if page == 'quote' and CONFIG['quote'].get('hostedUrl'):
            content += '<script type="application/json" id="portfolio-references">' + json.dumps([p['id'] for p in PORTFOLIO]) + '</script>'
        render(page,path,title,description,content)
        paths.append(path)
    for item in CATALOG:
        model_image = image_url(item['source'])
        model_width, model_height = image_sizes[item['source']]
        related = sorted([other for other in CATALOG if other['id'] != item['id']],key=lambda other:other['family']!=item['family'])[:4]
        gallery_label = 'Registro original' if item.get('originalGallery') else 'Outro enquadramento'
        gallery = ''.join(f'<a class="model-thumbnail" href="{image_url(source)}" data-photo data-photo-group="model" data-photo-caption="{escape(item["name"],quote=True)} — {gallery_label.lower()}" data-photo-quote="/orcamento.html?referencia={item["id"]}" aria-label="Ampliar {gallery_label.lower()} de {escape(item["name"],quote=True)}"><img src="{image_url(source)}" alt="{gallery_label} de {escape(item["name"])}" width="240" height="180" loading="lazy"></a>' for source in item.get('gallery',[]))
        notes = ''.join('<li>'+escape(note)+'</li>' for note in item['projectNotes'])
        content = replace((ROOT / 'pages/model.html').read_text(encoding='utf-8'),{'MODEL_IMAGE':model_image,'MODEL_IMAGE_WIDTH':model_width,'MODEL_IMAGE_HEIGHT':model_height,'MODEL_ALT':escape(item['alt']),'MODEL_NAME':escape(item['name']),'MODEL_DESCRIPTION':escape(item['description']),'MODEL_ID':item['id'],'RELATED':''.join(reference(other) for other in related),'MODEL_GALLERY':gallery,'MODEL_NOTES':notes,'MODEL_VISIBLE_DETAILS':''.join('<li>'+escape(detail)+'</li>' for detail in item['visibleDetails']),'MODEL_PHOTO_NOTE':('<figcaption class="model-photo-note">'+escape(item['photoNote'])+'</figcaption>' if item.get('photoNote') else ''),'MODEL_EXPERIENCE':model_experience(item)})
        path = 'modelos/' + item['id'] + '.html'
        render('model',path,item['name']+' | Stanza Decoro',item['description'],content,image_url(item['source']))
        paths.append(path)
    # Preserva também o acesso divulgado sem extensão: /portfolio.
    render('notfound','404.html','Página não encontrada | Stanza Decoro','Explore as referências da Stanza Decoro.',(ROOT/'pages/not-found.html').read_text(encoding='utf-8'))
    error_page=OUT/'404.html'
    error_page.write_text(error_page.read_text(encoding='utf-8').replace('content="index,follow"','content="noindex,nofollow"'),encoding='utf-8')
    (OUT / 'portfolio').mkdir(exist_ok=True)
    shutil.copy2(OUT / 'portfolio.html', OUT / 'portfolio/index.html')
    (OUT / 'robots.txt').write_text('User-agent: *\n' + ('Allow: /\n' if CONFIG['production'] else 'Disallow: /\n') + 'Sitemap: '+CONFIG['url']+'/sitemap.xml\n',encoding='utf-8')
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+CONFIG['url']+'/'+path+'</loc></url>' for path in paths)+'</urlset>\n',encoding='utf-8')
    (OUT / 'assets/build-info.json').write_text(json.dumps({'catalogCount':len(CATALOG),'portfolioCount':len(PORTFOLIO),'production':CONFIG['production'],'date':date.today().isoformat(),'revision':os.environ.get('COMMIT_REF','')[:12]},indent=2),encoding='utf-8')
    # Permite prévia na raiz, além da pasta de publicação dist.
    if not ARGS.no_source_entries:
        shutil.copytree(OUT / 'assets/images', ROOT / 'assets/images', dirs_exist_ok=True)
    totals = sum(p.stat().st_size for p in (OUT/'assets/images').glob('*'))
    print(f'{len(paths)} páginas, {len(CATALOG)} modelos e {len(PORTFOLIO)} referências. Imagens web: {totals/1024/1024:.2f} MB.')

if __name__ == '__main__':
    main()
