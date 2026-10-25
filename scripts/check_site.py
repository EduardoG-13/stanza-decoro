"""Verificações do pacote público: páginas, arquivos, contatos e conteúdo."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
import json
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
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
catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
expected_robots='index,follow' if config['production'] else 'noindex,nofollow'
pages=sorted(OUT.rglob('*.html'))
assert pages, 'Execute build.py primeiro.'
for file in pages:
    text=file.read_text(encoding='utf-8')
    page=Page(); page.feed(text)
    if '\ufffd' in text or '@@' in text: errors.append((str(file),'Codificação ou marcador pendente'))
    if len(page.ids)!=len(set(page.ids)): errors.append((str(file),'IDs duplicados'))
    for ref in page.references:
        if ref not in page.ids: errors.append((str(file),'Referência sem alvo: '+ref))
    for link in page.links:
        parsed=urlsplit(link)
        if parsed.scheme or parsed.netloc: continue
        if not parsed.path:
            if parsed.fragment and parsed.fragment not in page.ids: errors.append((str(file),'Âncora sem alvo: '+link))
            continue
        path=(OUT/unquote(parsed.path).lstrip('/')) if parsed.path.startswith('/') else (file.parent/unquote(parsed.path))
        if not path.exists(): errors.append((str(file),'Arquivo ausente: '+link))
    for image in page.images:
        if not image.get('alt') or not image.get('width') or not image.get('height'): errors.append((str(file),'Imagem sem descrição/dimensões'))
    if '551197556-3037' in text or 'Nova pasta/' in text: errors.append((str(file),'Contato ou ícone legado inválido'))
    if f'name="robots" content="{expected_robots}"' not in text: errors.append((str(file),'Indexação não corresponde à configuração'))
    if file.name=='portfolio.html':
        assert Counter(page.families)=={'sofas':10,'assentos':14,'complementos':12,'revestimentos':10},Counter(page.families)
    if file.name=='modelos.html': assert len(page.families)==len(catalog)

home=(OUT/'index.html').read_text(encoding='utf-8').lower()
assert 'empreendimento' not in home and 'data-partner' not in home
manifest=json.loads((OUT/'icon/site.webmanifest').read_text(encoding='utf-8'))
for icon in manifest['icons']: assert (OUT/icon['src'].lstrip('/')).exists()
script=(OUT/'assets/app.js').read_text(encoding='utf-8')
assert 'localStorage' not in script and 'sessionStorage' not in script
assert 'navigator.clipboard.writeText(summary.textContent)' in script
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
print(f'Portfólio: 46 referências; catálogo: {len(catalog)}; empreendimentos ausentes da principal.')
print('Dados do formulário sem armazenamento persistente no navegador; registro opcional por servidor configurável.')
print('Esta verificação não substitui navegação visual ou testes de interação em navegador.')
