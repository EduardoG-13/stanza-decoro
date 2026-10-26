"""Gera somente orçamento, privacidade e consulta privada no endereço separado."""
from pathlib import Path
import json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'data/quote-host.json').read_text(encoding='utf-8'))
firebase=config['quote']['firebase']
protection={'siteKey':config['quote']['recaptchaSiteKey']}
config['url']='https://stanza-atendimento-820e4.web.app'
config['production']=False
config['quote']={'mode':'firebase','endpoint':'https://southamerica-east1-cadastro-820e4.cloudfunctions.net/receberPedidoSite','firebase':firebase,'recaptchaSiteKey':protection['siteKey']}
(ROOT/'data/quote-host.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),'--config-file','data/quote-host.json','--output','.quote-build','--no-source-entries'],cwd=ROOT,check=True)
source=ROOT/'.quote-build';out=ROOT/'dist-formulario';out.mkdir(exist_ok=True)
for page in ['orcamento.html','privacidade.html']:
    text=(source/page).read_text(encoding='utf-8')
    text=re.sub(r'      <button class="menu-toggle".*?</button>\n','',text)
    text=re.sub(r'      <nav class="site-nav".*?</nav>\n','',text,flags=re.S)
    text=text.replace('href="/index.html"','href="/orcamento.html"')
    if page=='orcamento.html':
        text=text.replace('Ao continuar, voc\u00ea prepara uma conversa.','Ao enviar, voc\u00ea registra seu projeto para avalia\u00e7\u00e3o.')
        text=text.replace('Este site n\u00e3o registrou nem enviou o pedido.','O pedido s\u00f3 \u00e9 registrado ap\u00f3s a confirma\u00e7\u00e3o do envio.')
    else:
        text=text.replace('<h2>Contato</h2>','<h2>Prote\u00e7\u00e3o do envio</h2><p>Este formul\u00e1rio utiliza o reCAPTCHA Enterprise do Google para reduzir envios automatizados. Consulte a <a href="https://policies.google.com/privacy">Pol\u00edtica de Privacidade</a> e os <a href="https://policies.google.com/terms">Termos de Servi\u00e7o do Google</a>.</p><h2>Contato</h2>')
    if page=='orcamento.html':
        assert 'method="post" action="/orcamento.html"' in text
        assert 'type="submit" disabled' in text
    (out/page).write_text(text,encoding='utf-8')
(out/'assets/images').mkdir(parents=True,exist_ok=True)
for file in ['site.css','app.js','quote-api.js','quote-fields.js','quote-message.js','atendimento.js','atendimento.css']:
    shutil.copy2(ROOT/'assets'/file,out/'assets'/file)
shutil.copytree(source/'assets/cities',out/'assets/cities',dirs_exist_ok=True)
shutil.copy2(ROOT/'pages/atendimento.html',out/'atendimento.html')
shutil.copy2(source/'assets/images/stanza-logo.png',out/'assets/images/stanza-logo.png')
# Publicar apenas as miniaturas exigidas pelo contexto, sem copiar o acervo completo.
quote=(source/'orcamento.html').read_text(encoding='utf-8')
thumbnails=set()
for marker in ['catalog-references','portfolio-projects']:
    raw=re.search('<script type="application/json" id="'+marker+'">(.*?)</script>',quote,re.S)
    assert raw,marker
    for item in json.loads(raw.group(1)).values():
        relative=item['image'].lstrip('/')
        assert re.fullmatch(r'assets/images/[a-f0-9]{12}-ref480\.webp',relative),relative
        assert (source/relative).is_file(),relative
        assert item['name'] and item['alt'] and item['piece']
        thumbnails.add(relative)
for relative in thumbnails:
    shutil.copy2(source/relative,out/relative)
for stale in (out/'assets/images').glob('*-ref480.webp'):
    assert stale.resolve().is_relative_to(out.resolve())
    if str(stale.relative_to(out)).replace('\\','/') not in thumbnails:
        stale.unlink()
print(f'{len(thumbnails)} miniaturas de referências; somente a selecionada é pedida pela página.')

shutil.copytree(source/'icon',out/'icon',dirs_exist_ok=True)
(out/'assets/atendimento-publico.json').write_text(json.dumps({'firebase':firebase},indent=2)+'\n',encoding='utf-8')
(out/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
allowed={'orcamento.html','privacidade.html','atendimento.html','robots.txt'}
assert all(p.name in allowed for p in out.glob('*') if p.is_file())
assert not list(out.rglob('*.glb')) and not list(out.rglob('*.env*'))
for page in out.glob('*.html'):
    text=page.read_text(encoding='utf-8')
    assert '@@' not in text and '\ufffd' not in text
    for match in re.findall(r'(?:href|src)="(/[^"]*)"',text):
        path=match.split('?')[0]
        assert (out/path.lstrip('/')).is_file(),(page.name,path)
print('Pacote HTTPS separado: or\u00e7amento, privacidade e atendimento. Site principal fora da publica\u00e7\u00e3o.')
