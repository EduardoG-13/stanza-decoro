// The pilot owns geometry and materials; this adapter owns only site controls.
// EXT-001 (2.0.0+, now 2.1.0): exterior-only model. No layer/opening controls; fabric and colour apply to
// the sofa BODY only (decorative cushions keep their fixed finish inside the viewer).
// models3d pipeline (EXT-002+): ?modelo=<modelId> selects any REGISTERED model of data/models-3d.json;
// the page then shows that model's poster, title, options and quote reference, and loads ONLY that
// model's GLB after the visitor asks for the 3D. An unknown model never falls back to another piece.
const $ = selector => document.querySelector(selector);
const options = JSON.parse($('#sofa-options').textContent);
const registry = JSON.parse($('#models-3d')?.textContent || '{"models":[]}');
const start = $('#start-sofa'), stage = $('#sofa-stage'), status = $('#sofa-status');
const asked = new URLSearchParams(location.search).get('modelo');
const requested = asked || stage.dataset.modelId || registry.defaultModelId;
const verified = registry.verifiedStatuses || ['technical-validated-visual-review-pending','approved'];
const model = registry.models.find(entry => entry.modelId === requested && verified.includes(entry.status)) || null;
let viewer, loading = false, finishRequest = 0;
function report(message, error = false) { status.textContent = message; status.classList.toggle('is-error', error); }
const fabricInputs = () => [...document.querySelectorAll('input[name="sofa-fabric"]')];
const colorInputs = () => [...document.querySelectorAll('input[name="sofa-color"]')];
function applyModel() {
  if (!model) {
    // Unregistered/unverified study: photo/poster path only, no 3D and no other piece shown.
    stage.classList.add('is-unavailable'); stage.dataset.modelId = '';
    stage.querySelector('img')?.setAttribute('hidden', '');
    start.hidden = true; start.disabled = true;
    report('Este estudo 3D não está disponível. As fotos das peças continuam no catálogo.', true);
    $('#sofa-quote').href = '/orcamento.html';
    const back = $('.sofa-stage-panel .text-link'); if (back) { back.href = '/modelos.html'; back.textContent = 'Ver o catálogo de peças →'; }
    return;
  }
  stage.dataset.modelId = model.modelId;
  const poster = stage.querySelector('img');
  if (poster && model.assets.poster && poster.getAttribute('src') !== model.assets.poster) { poster.src = model.assets.poster; }
  if (poster && model.posterAlt) poster.alt = model.posterAlt;
  const product = model.productPage || `/modelos/${model.catalogId}.html`;
  document.querySelectorAll('[data-model-product]').forEach(link => { link.href = product; });
  const crumb = $('[data-model-crumb]'); if (crumb) crumb.textContent = model.title;
  const allowed = {fabric: model.options.fabrics, color: model.options.colors};
  for (const [kind, inputs] of [['fabric', fabricInputs()], ['color', colorInputs()]]) {
    for (const input of inputs) {
      const show = allowed[kind].includes(input.value);
      input.closest('label').hidden = !show; input.disabled = !show;
      input.checked = input.value === model.options.default[kind === 'fabric' ? 'fabricId' : 'colorId'];
    }
  }
  showSelection({modelId: model.modelId, ...model.options.default});
}
function showSelection(selection) {
  const fabric = options.fabrics[selection.fabricId], color = options.colors[selection.colorId];
  if (!fabric || !color) return;
  fabricInputs().forEach(input => input.checked = input.value === selection.fabricId);
  colorInputs().forEach(input => input.checked = input.value === selection.colorId);
  $('#sofa-selection-name').textContent = fabric + ' · ' + color;
  const params = new URLSearchParams({referencia: model?.catalogId || 'sofa-organico', estudo: selection.modelId, tecido: selection.fabricId, cor: selection.colorId});
  $('#sofa-quote').href = '/orcamento.html?' + params;
}
async function initialize() {
  if (viewer || loading || !model) return;
  loading = true; start.disabled = true; stage.setAttribute('aria-busy','true');
  start.firstChild.textContent = 'Carregando o 3D… ';
  report('Preparando a visualização 3D…');
  try {
    const {createSofaViewer} = await import('./sofa-pilot/viewer/sofa-viewer.js');
    viewer = await createSofaViewer(stage, {
      baseUrl: model.assets.viewerBase, modelUrls: {main: model.assets.main, mobile: model.assets.mobile},
      model, materialUrls: registry.materialLibrary,
      onFinish: showSelection, onStatus: message => report(message)
    });
    document.querySelectorAll('.sofa-inspector fieldset, [data-camera]').forEach(control => control.disabled = false);
    stage.classList.add('is-ready');
    // The viewer's generic canvas label names a sofa; say which piece this is.
    stage.querySelector('canvas')?.setAttribute('aria-label', `${model.title} em 3D. Arraste para girar. Setas giram; mais e menos aproximam; Home restaura a vista. A rolagem continua livre.`);
    report('Pronto. Arraste para girar ou use os controles.');
  } catch {
    report('O 3D não abriu neste navegador. A imagem e o orçamento continuam disponíveis. Você pode tentar novamente.', true);
    start.firstChild.textContent = 'Tentar abrir o 3D '; start.disabled = false;
  } finally { loading = false; stage.setAttribute('aria-busy','false'); }
}
applyModel();
start.addEventListener('click', initialize);
document.querySelectorAll('[data-camera]').forEach(button => button.addEventListener('click', () => {
  if (!viewer) return;
  ({left: () => viewer.rotate(-Math.PI/8), right: () => viewer.rotate(Math.PI/8), in: () => viewer.zoom(.85), out: () => viewer.zoom(1.18)})[button.dataset.camera]();
}));
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
  if (!viewer) return; viewer.setView(button.dataset.view);
}));
document.querySelectorAll('input[name="sofa-fabric"], input[name="sofa-color"]').forEach(input => input.addEventListener('change', async () => {
  if (!viewer) return;
  const request = ++finishRequest;
  $('#sofa-quote').setAttribute('aria-disabled','true'); $('#sofa-quote').setAttribute('tabindex','-1');
  try {
    await viewer.setFinish({fabricId: $('input[name="sofa-fabric"]:checked').value, colorId: $('input[name="sofa-color"]:checked').value});
    if (request === finishRequest) {showSelection(viewer.getSelection()); report('Combinação atualizada.');}
  } catch {
    if (request === finishRequest) {showSelection(viewer.getSelection()); report('Este acabamento não carregou. Mantivemos a última combinação disponível.', true);}
  } finally {if (request === finishRequest) {$('#sofa-quote').removeAttribute('aria-disabled'); $('#sofa-quote').removeAttribute('tabindex');}}
}));
$('#sofa-quote').addEventListener('click', event => {if (event.currentTarget.getAttribute('aria-disabled') === 'true') event.preventDefault();});
window.addEventListener('pagehide', event => {
  if (event.persisted) return;
  viewer?.dispose();
}, {once:true});
