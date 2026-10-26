'use strict';
document.documentElement.classList.add('js');

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#site-nav');
if (menuButton && navigation) {
  const closeMenu = () => { navigation.dataset.open = 'false'; menuButton.setAttribute('aria-expanded', 'false'); };
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') !== 'true';
    navigation.dataset.open = String(open); menuButton.setAttribute('aria-expanded', String(open));
  });
  navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('click', event => { if (!navigation.contains(event.target) && !menuButton.contains(event.target)) closeMenu(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') { closeMenu(); menuButton.focus(); }
  });
  matchMedia('(min-width:851px)').addEventListener('change', closeMenu);
}

const filterGrid = document.querySelector('[data-filter-grid]');
if (filterGrid) {
  const filters = [...document.querySelectorAll('[data-filter]')];
  const items = [...filterGrid.querySelectorAll('[data-family]')];
  const count = document.querySelector('.result-count');
  const search = document.querySelector('[data-catalog-search]');
  const empty = document.querySelector('[data-empty-results]');
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  let family = new URLSearchParams(location.search).get('familia') || 'todos';
  if (!filters.some(button=>button.dataset.filter===family)) family='todos';
  const applyFilters = () => {
    const words = normalize(search?.value.trim() || '').split(/\s+/).filter(Boolean);
    let visible = 0;
    items.forEach(item => {
      const text = normalize(item.dataset.search || item.textContent);
      item.hidden = (family !== 'todos' && item.dataset.family !== family) || !words.every(word=>text.includes(word));
      if (!item.hidden) visible++;
    });
    filters.forEach(peer => peer.setAttribute('aria-pressed', String(peer.dataset.filter === family)));
    count.textContent = visible + (visible === 1 ? ' referência' : ' referências');
    if (empty) empty.hidden=visible!==0;
  };
  filters.forEach(button => button.addEventListener('click', () => {family=button.dataset.filter;applyFilters();}));
  search?.addEventListener('input',applyFilters);
  document.querySelector('[data-clear-filters]')?.addEventListener('click',()=>{family='todos';if(search)search.value='';applyFilters();search?.focus();});
  applyFilters();
}

const photoDialog = document.querySelector('#photo-dialog');
if (photoDialog && typeof photoDialog.showModal === 'function') {
  const links = [...document.querySelectorAll('[data-photo]')];
  const image = photoDialog.querySelector('#photo-dialog-image');
  const caption = photoDialog.querySelector('#photo-dialog-caption');
  const photoStatus = photoDialog.querySelector('#photo-dialog-status');
  const previous = photoDialog.querySelector('[aria-label="Foto anterior"]');
  const next = photoDialog.querySelector('[aria-label="Próxima foto"]');
  let gallery=[], index=0, opener;
  const showPhoto = () => {
    const link=gallery[index];
    photoStatus.textContent='Carregando foto…';image.hidden=true;
    caption.textContent=link.dataset.photoCaption;
    image.alt=link.querySelector('img')?.alt || link.dataset.photoCaption;
    photoDialog.querySelector('#photo-dialog-count').textContent=`${index+1} / ${gallery.length}`;
    photoDialog.querySelector('#photo-dialog-quote').href=link.dataset.photoQuote;
    previous.disabled=next.disabled=gallery.length<2;
    image.src=link.href;
  };
  image.addEventListener('load',()=>{image.hidden=false;photoStatus.textContent='';});
  image.addEventListener('error',()=>{photoStatus.textContent='Não foi possível carregar a foto. Feche e tente novamente.';});
  const move = direction => {index=(index+direction+gallery.length)%gallery.length;showPhoto();};
  links.forEach(link=>link.addEventListener('click',event=>{
    event.preventDefault();opener=link;
    gallery=links.filter(peer=>peer.dataset.photoGroup===link.dataset.photoGroup && !peer.closest('[hidden]'));
    index=gallery.indexOf(link);showPhoto();photoDialog.showModal();document.body.classList.add('photo-open');
  }));
  previous.addEventListener('click',()=>move(-1));next.addEventListener('click',()=>move(1));
  photoDialog.querySelector('.photo-close').addEventListener('click',()=>photoDialog.close());
  photoDialog.addEventListener('click',event=>{if(event.target===photoDialog)photoDialog.close();});
  photoDialog.addEventListener('keydown',event=>{if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();move(event.key==='ArrowLeft'?-1:1);}});
  photoDialog.addEventListener('close',()=>{document.body.classList.remove('photo-open');image.removeAttribute('src');opener?.focus({preventScroll:true});});
}

const form = document.querySelector('#quote-form');
if (form) {
  const field = name => form.elements.namedItem(name);
  const review = document.querySelector('#quote-review');
  const summary = document.querySelector('#quote-summary');
  const quoteError = document.querySelector('#quote-error');
  const photoError = document.querySelector('#photo-error');
  const photoInput = document.querySelector('#quote-photos');
  const previews = document.querySelector('#photo-previews');
  const copyStatus = document.querySelector('#copy-status');
  const quoteConfig = JSON.parse(document.querySelector('#quote-config').textContent);
  const automatic = quoteConfig.mode !== 'manual';
  const sendButton = document.querySelector('#send-quote');
  const sendStatus = document.querySelector('#send-status');
  const sendError = document.querySelector('#send-error');
  const editButton = document.querySelector('#edit-quote');
  let reviewedData, submission, sending = false;
  document.querySelector('#manual-instructions').hidden = automatic;
  document.querySelector('#api-instructions').hidden = !automatic;
  const params = new URLSearchParams(location.search);
  const references = JSON.parse(document.querySelector('#catalog-references').textContent);
  const option = (map,key) => Object.hasOwn(map,key) ? map[key] : undefined;
  const selected = option(references,params.get('referencia'));
  if (selected) { field('reference').value = selected.name; field('piece').value = selected.piece; }
  else if (params.get('referencia') === 'outro-projeto') field('reference').value = 'Tenho outro modelo ou projeto';
  else if (params.get('projeto') && /^projeto-\d+$/.test(params.get('projeto'))) field('reference').value = 'Referência do portfólio: ' + params.get('projeto');
  if (params.get('servico') === 'reforma') field('service').value = 'Reforma';
  const sofaOptions = JSON.parse(document.querySelector('#sofa-options').textContent);
  const fabric = option(sofaOptions.fabrics,params.get('tecido')), color = option(sofaOptions.colors,params.get('cor'));
  if (selected && params.get('referencia') === 'sofa-organico' && params.get('estudo') === sofaOptions.modelId && fabric && color) {
    field('reference').value = selected.name + ' · estudo 3D: ' + fabric + ' / ' + color;
  }
  if (selected) {
    const context=document.querySelector('#quote-selected-reference');
    context.hidden=false;context.querySelector('strong').textContent=field('reference').value;
  }
  let photos = [];
  const maxPhotos = 5, maxSize = 8 * 1024 * 1024;

  function renderPhotos() {
    previews.replaceChildren();
    photos.forEach(photo => {
      const figure = document.createElement('figure');
      const image = document.createElement('img'); image.src = photo.url; image.alt = 'Prévia local de ' + photo.file.name; image.width = 180; image.height = 180;
      const caption = document.createElement('figcaption'); caption.textContent = photo.file.name;
      const remove = document.createElement('button'); remove.type = 'button'; remove.textContent = 'Remover'; remove.setAttribute('aria-label', 'Remover foto ' + photo.file.name);
      remove.addEventListener('click', () => { URL.revokeObjectURL(photo.url); photos = photos.filter(item => item !== photo); renderPhotos(); });
      figure.append(image, caption, remove); previews.append(figure);
    });
  }
  photoInput.addEventListener('change', () => {
    photoError.hidden = true;
    const files = [...photoInput.files]; photoInput.value = '';
    if (!files.length) return;
    let error = '';
    if (photos.length + files.length > maxPhotos) error = 'Selecione no máximo 5 fotos. Remova uma para escolher outra.';
    else if (files.some(file => !['image/jpeg','image/png','image/webp'].includes(file.type))) error = 'Escolha fotos JPEG, PNG ou WebP.';
    else if (files.some(file => file.size > maxSize || file.size === 0)) error = 'Cada foto deve ter conteúdo e até 8 MB.';
    if (error) { photoError.textContent = error; photoError.hidden = false; return; }
    photos.push(...files.map(file => ({file, url: URL.createObjectURL(file)}))); renderPhotos();
  });
  field('phone').addEventListener('input', () => field('phone').setCustomValidity(''));
  const value = name => String(field(name).value).trim();
  form.addEventListener('submit', event => {
    event.preventDefault(); quoteError.hidden = true;
    const digits = value('phone').replace(/\D/g, '');
    field('phone').setCustomValidity(digits.length >= 10 && digits.length <= 13 ? '' : 'Informe um WhatsApp com DDD.');
    for (const name of ['name', 'city']) field(name).setCustomValidity(value(name) ? '' : 'Preencha este campo.');
    if (!form.reportValidity()) { quoteError.textContent = 'Confira os campos obrigatórios antes de continuar.'; quoteError.hidden = false; return; }
    const lines = ['Olá, Stanza! Gostaria de avaliar meu projeto.', '', 'Serviço: ' + value('service'), 'Peça: ' + value('piece'), 'Referência: ' + (value('reference') || 'A definir'), 'Medidas aproximadas: ' + (value('dimensions') || 'Ainda não informadas'), 'Observações: ' + (value('details') || 'Não informadas'), '', 'Nome: ' + value('name'), 'WhatsApp: ' + value('phone'), 'E-mail: ' + value('email'), 'Cidade/UF: ' + value('city') + ' / ' + value('state'), 'Período desejado: ' + (value('period') || 'A avaliar'), 'Fotos: ' + (photos.length ? photos.length + ' selecionada(s), a anexar na conversa' : 'Não selecionadas'), '', 'Viabilidade, prazo e transporte após avaliação.'];
    summary.textContent = lines.join('\n');
    reviewedData = Object.fromEntries(['service','piece','reference','dimensions','details','name','phone','email','city','state','period'].map(name=>[name,value(name)]));
    if (automatic) summary.textContent = summary.textContent.replace('selecionada(s), a anexar na conversa','selecionada(s), a enviar com o projeto');
    submission = undefined; sendStatus.textContent = ''; sendError.hidden = true; sendButton.disabled = false;
    // A URL abre só uma mensagem inicial. Dados pessoais permanecem no resumo local.
    const initial = 'Olá, Stanza! Gostaria de conversar sobre ' + (value('service') === 'Reforma' ? 'a reforma de uma peça' : 'uma peça sob medida') + '. Preparei um resumo do projeto para enviar na conversa.';
    document.querySelector('#continue-whatsapp').href = 'https://wa.me/' + document.body.dataset.whatsapp + '?text=' + encodeURIComponent(initial);
    form.hidden = true; document.querySelector('.quote-aside').hidden = true; review.hidden = false; copyStatus.textContent = '';
    const title = review.querySelector('h2'); title.tabIndex = -1; title.focus({preventScroll:true});
    review.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches ? 'instant' : 'smooth', block:'start'});
  });
  for (const name of ['name', 'city']) field(name).addEventListener('input', () => field(name).setCustomValidity(''));
  document.querySelector('#edit-quote').addEventListener('click', () => {
    if (sending || submission?.confirmacaoIniciada) return;
    submission = undefined;
    review.hidden = true; form.hidden = false; document.querySelector('.quote-aside').hidden = false;
    field('reference').focus({preventScroll:true}); form.scrollIntoView({behavior:'instant',block:'start'});
  });
  document.querySelector('#copy-summary').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(summary.textContent); copyStatus.textContent = automatic ? 'Resumo copiado.' : 'Resumo copiado. Cole na conversa e anexe as fotos.'; }
    catch { const range = document.createRange(); range.selectNodeContents(summary); const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range); copyStatus.textContent = 'Selecionei o resumo. Use Copiar no seu dispositivo.'; }
  });
  sendButton.addEventListener('click', async () => {
    if (sending || !automatic) return;
    sending = true; sendButton.disabled = true; editButton.disabled = true; sendError.hidden = true;
    try {
      const api = await import('/assets/quote-api.js');
      if (!submission) submission = await api.prepararEnvio(reviewedData,photos.map(photo=>photo.file));
      const received = await api.registrarEnvio(quoteConfig,submission,text=>{sendStatus.textContent=text;});
      if (!api.protocoloValido(received.protocolo)) throw new Error('O recebimento ainda não pôde ser confirmado. Tente novamente.');
      sendStatus.textContent = (quoteConfig.mode === 'emulator' ? 'Registrado somente na demonstração local. ' : 'Projeto recebido para avaliação. ') + 'Protocolo: ' + received.protocolo;
      sendButton.textContent = 'Projeto registrado';
      sendButton.hidden = true; editButton.hidden = true;
      sendStatus.classList.add('quote-received');
      const instructions = document.querySelectorAll('#api-instructions>p:not([id])');
      instructions[0].textContent = photos.length ? 'Os dados e as fotos do seu projeto foram recebidos pela Stanza.' : 'Os dados do seu projeto foram recebidos pela Stanza.';
      instructions[1].textContent = 'A equipe vai avaliar as informações para o atendimento. Se quiser, continue pelo WhatsApp com o protocolo abaixo.';
      document.querySelector('#continue-whatsapp').href = 'https://wa.me/' + document.body.dataset.whatsapp + '?text=' + encodeURIComponent('Olá, Stanza! Enviei o projeto pelo site. Meu protocolo é ' + received.protocolo + '.');
      document.querySelector('#review-title').textContent = quoteConfig.mode === 'emulator' ? 'Recebido na demonstração.' : 'Seu projeto chegou.';
      submission.confirmacaoIniciada = true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Não foi possível confirmar o envio.';
      const securityError = /AppCheck|reCAPTCHA|appCheck\//i.test(message);
      sendError.textContent = (securityError ? 'A verificação de segurança não pôde ser concluída agora.' : message) + ' Use Tentar novamente para conferir o mesmo envio, sem criar outro pedido. Você também pode conversar pelo WhatsApp.';
      sendError.hidden = false; sendStatus.textContent = 'Recebimento ainda não confirmado.';
      sendButton.textContent = 'Tentar novamente'; sendButton.disabled = false;
      editButton.disabled = !!submission?.confirmacaoIniciada;
    } finally {sending = false;}
  });
  window.addEventListener('pagehide', () => { photos.forEach(photo => URL.revokeObjectURL(photo.url)); }, {once:true});
  window.addEventListener('pageshow', event => {
    if (event.persisted) { photos.forEach(photo => { photo.url = URL.createObjectURL(photo.file); }); renderPhotos(); }
  });
}


// Content stays visible without JavaScript; each entrance runs only once.
if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const arrivals = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {entry.target.classList.add('has-arrived'); arrivals.unobserve(entry.target);}
    });
  }, {threshold:.1});
  document.querySelectorAll('.section-heading,.craft-grid,.service-paths>a,.project-strip>figure').forEach(element => arrivals.observe(element));
}


// This quiet page preference also pauses the decorative 3D opening.
const motionControl = document.querySelector('#reduce-motion');
if (motionControl) {
  const deviceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let pageMotionReduced = false;
  const applyMotionPreference = () => {
    const reduced = pageMotionReduced || deviceMotion.matches;
    document.documentElement.classList.toggle('reduce-motion',reduced);
    motionControl.disabled = deviceMotion.matches;
    motionControl.setAttribute('aria-pressed',String(reduced));
    motionControl.textContent = reduced ? 'Movimentos reduzidos' : 'Reduzir movimentos';
    motionControl.setAttribute('aria-label',reduced && !deviceMotion.matches ? 'Retomar os movimentos nesta página' : 'Reduzir os movimentos nesta página');
    document.dispatchEvent(new CustomEvent('stanza:motion'));
  };
  motionControl.addEventListener('click', () => {pageMotionReduced = !pageMotionReduced; applyMotionPreference();});
  deviceMotion.addEventListener('change',applyMotionPreference);
  applyMotionPreference();
}
