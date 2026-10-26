"""Verificações do pacote público: páginas, arquivos, contatos e conteúdo."""
from pathlib import Path
from PIL import Image
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json
import hashlib
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',default='dist')
parser.add_argument('--production',action='store_true')
ARGS=parser.parse_args()
OUT = (ROOT / ARGS.output).resolve()
assert OUT.is_relative_to(ROOT) and OUT!=ROOT
sys.stdout.reconfigure(encoding='utf-8')

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.links=[]; self.images=[]; self.references=[]; self.families=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        for key in ['href','src']:
            if key in attrs: self.links.append(attrs[key])
        if tag=='img': self.images.append(attrs)
        if 'for' in attrs: self.references.append(attrs['for'])
        if 'aria-controls' in attrs: self.references.extend(attrs['aria-controls'].split())
        if 'data-family' in attrs: self.families.append(attrs['data-family'])

errors=[]
config=json.loads((ROOT/'site.config.json').read_text(encoding='utf-8'))
if ARGS.production:config['production']=True
catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
portfolio=json.loads((ROOT/'data/portfolio.json').read_text(encoding='utf-8'))
expected_robots='index,follow' if config['production'] else 'noindex,nofollow'
pages=sorted(OUT.rglob('*.html'))
exact_paths={p.relative_to(OUT).as_posix() for p in OUT.rglob('*')}
assert pages, 'Execute build.py primeiro.'
published_redirects=(OUT/'_redirects').read_text(encoding='utf-8').splitlines()
assert published_redirects[:2]==['/pedidos-site /404.html 404!','/pedidos-site/* /404.html 404!'], 'O pacote público não deve encaminhar ao atendimento.'
for file in pages:
    text=file.read_text(encoding='utf-8')
    page=Page(); page.feed(text)
    if '\ufffd' in text or '@@' in text: errors.append((str(file),'Codificação ou marcador pendente'))
    if len(page.ids)!=len(set(page.ids)): errors.append((str(file),'IDs duplicados'))
    for ref in page.references:
        if ref not in page.ids: errors.append((str(file),'Referência sem alvo: '+ref))
    for link in page.links:
        parsed=urlsplit(link)
        if parsed.path.rstrip('/')=='/pedidos-site' or parsed.hostname=='gestao.stanzadecoro.com.br':
            errors.append((str(file),'Entrada da equipe não deve ficar nas páginas públicas: '+link))
        if parsed.scheme or parsed.netloc: continue
        if not parsed.path:
            if parsed.fragment and parsed.fragment not in page.ids: errors.append((str(file),'Âncora sem alvo: '+link))
            continue
        path=(OUT/unquote(parsed.path).lstrip('/')) if parsed.path.startswith('/') else (file.parent/unquote(parsed.path))
        if not path.exists(): errors.append((str(file),'Arquivo ausente: '+link))
        elif path.is_relative_to(OUT) and path.relative_to(OUT).as_posix() not in exact_paths:
            errors.append((str(file),'Maiúsculas/minúsculas incompatíveis com a hospedagem: '+link))
    for image in page.images:
        if 'data-model-image' in image:
            with Image.open(OUT/image['src'].lstrip('/')) as actual:
                assert (int(image['width']),int(image['height']))==actual.size, (file,image['src'])
        if not image.get('alt') or not image.get('width') or not image.get('height'): errors.append((str(file),'Imagem sem descrição/dimensões'))
    if '551197556-3037' in text or 'Nova pasta/' in text: errors.append((str(file),'Contato ou ícone legado inválido'))
    page_robots='noindex,nofollow' if file.name=='404.html' else expected_robots
    if f'name="robots" content="{page_robots}"' not in text: errors.append((str(file),'Indexação não corresponde à configuração'))
    if file.name=='portfolio.html':
        assert Counter(page.families)==Counter(item['family'] for item in portfolio),Counter(page.families)
    if file.name=='modelos.html': assert len(page.families)==len(catalog)

home=(OUT/'index.html').read_text(encoding='utf-8').lower()
assert 'empreendimento' not in home and 'data-partner' not in home
manifest=json.loads((OUT/'icon/site.webmanifest').read_text(encoding='utf-8'))
for icon in manifest['icons']: assert (OUT/icon['src'].lstrip('/')).exists()
script=(OUT/'assets/app.js').read_text(encoding='utf-8')
assert 'localStorage' not in script and 'sessionStorage' not in script
assert 'clipboard.writeText' not in script
assert (OUT/'assets/quote-message.js').is_file() and (OUT/'assets/quote-fields.js').is_file()
assert len(list((OUT/'assets/cities').glob('*.json'))) == 27
pilot=OUT/'assets/sofa-pilot'
integration=json.loads((pilot/'INTEGRATION.json').read_text(encoding='utf-8'))
for relative,digest in integration['modelSha256'].items():
    model=pilot/relative
    assert hashlib.sha256(model.read_bytes()).hexdigest()==digest, relative
    header=model.read_bytes()[:12]
    assert header[:4]==b'glTF' and int.from_bytes(header[4:8],'little')==2, relative
    assert int.from_bytes(header[8:12],'little')==model.stat().st_size, relative
assert (pilot/'viewer/vendor/three/LICENSE').exists()
assert not errors,errors
print(f'{len(pages)} páginas conferidas; links/arquivos, IDs, formulários, manifesto e contatos válidos.')
print(f'Portfólio: {len(portfolio)} referências; catálogo: {len(catalog)}; empreendimentos ausentes da principal.')
print('Dados do formulário sem armazenamento persistente no navegador; registro opcional por servidor configurável.')
print('Esta verificação não substitui navegação visual ou testes de interação em navegador.')
