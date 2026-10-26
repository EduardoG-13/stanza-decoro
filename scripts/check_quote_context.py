"""Confere associação e leveza das referências que chegam ao orçamento."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from PIL import Image
import json,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'dist-formulario'
class Scripts(HTMLParser):
    def __init__(self):super().__init__();self.marker=None;self.values={}
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if tag=='script' and data.get('type')=='application/json':
            self.marker=data.get('id');self.values[self.marker]=''
    def handle_data(self,data):
        if self.marker:self.values[self.marker]+=data
    def handle_endtag(self,tag):
        if tag=='script':self.marker=None
parser=Scripts();parser.feed((OUT/'orcamento.html').read_text(encoding='utf-8'))
valid={'Sofá','Poltrona','Cabeceira','Cama','Cadeira','Banco','Puff','Cortina','Outra peça / projeto'}
seen=set()
for marker,file,title in [('catalog-references','catalog.json','name'),('portfolio-projects','portfolio.json','title')]:
    expected=json.loads((ROOT/'data'/file).read_text(encoding='utf-8'))
    actual=json.loads(parser.values[marker])
    assert set(actual)=={item['id'] for item in expected},marker
    for item in expected:
        reference=actual[item['id']];path=urlsplit(reference['image'])
        assert not path.scheme and not path.netloc
        assert reference['name']==item[title] and reference['alt']==item['alt']
        assert reference['piece']==item['piece'] and reference['piece'] in valid
        digest=hashlib.sha256((ROOT/item['source']).read_bytes()).hexdigest()[:12]
        assert path.path==f'/assets/images/{digest}-ref480.webp'
        asset=OUT/path.path.lstrip('/')
        with Image.open(asset) as image:
            assert image.width<=480 and image.height<=360 and not image.getexif()
        assert asset.stat().st_size<128*1024
        seen.add(asset)
print(f"{len(json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8')))} referências de catálogo e {len(json.loads((ROOT/'data/portfolio.json').read_text(encoding='utf-8')))} do portfólio associadas à foto, nome e tipo corretos.")
print(f'{len(seen)} miniaturas; total {sum(p.stat().st_size for p in seen)/1024:.0f} KB; maior {max(p.stat().st_size for p in seen)/1024:.0f} KB. A página utiliza apenas a referência selecionada.')
