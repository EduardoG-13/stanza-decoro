/* A prévia abre o formulário HTTPS antes da coleta de qualquer dado pessoal. */
(() => {
  const link = document.querySelector('#open-secure-quote');
  if (!link) return;
  const config = JSON.parse(document.querySelector('#quote-config').textContent);
  const destination = new URL(config.hostedUrl);
  if (destination.origin !== 'https://stanza-atendimento-820e4.web.app' || destination.pathname !== '/orcamento.html') return;
  const incoming = new URLSearchParams(location.search);
  const catalog = JSON.parse(document.querySelector('#catalog-references').textContent);
  const model = incoming.get('referencia');
  if (Object.hasOwn(catalog,model) || model === 'outro-projeto') destination.searchParams.set('referencia',model);
  if (incoming.get('servico') === 'reforma') destination.searchParams.set('servico','reforma');
  const projects = JSON.parse(document.querySelector('#portfolio-references').textContent);
  if (projects.includes(incoming.get('projeto'))) destination.searchParams.set('projeto',incoming.get('projeto'));
  const sofa = JSON.parse(document.querySelector('#sofa-options').textContent);
  const study = incoming.get('estudo');
  const known = (model === 'sofa-organico' && study === sofa.modelId) || (Object.hasOwn(sofa.studies || {}, study) && sofa.studies[study] === model);
  if (known) {
    destination.searchParams.set('estudo',study);
    for (const [key,allowed] of [['tecido',sofa.fabrics],['cor',sofa.colors]]) {
      const value=incoming.get(key);
      if (Object.hasOwn(allowed,value)) destination.searchParams.set(key,value);
    }
  }
  link.href=destination.href;
  location.replace(destination.href);
})();
