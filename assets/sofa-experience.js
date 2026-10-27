// The pilot owns geometry and materials; this adapter owns only site controls.
// EXT-001 (2.0.0+, now 2.1.0): exterior-only model. No layer/opening controls; fabric and colour apply to
// the sofa BODY only (decorative cushions keep their fixed finish inside the viewer).
const $ = selector => document.querySelector(selector);
const options = JSON.parse($('#sofa-options').textContent);
const registry = JSON.parse($('#models-3d')?.textContent || '{"models":[]}');
const start = $('#start-sofa'), stage = $('#sofa-stage'), status = $('#sofa-status');
// Model selection is incremental: the page names its model (data-model-id); an optional
// ?modelo=<modelId> may pick another REGISTERED model. Only that model's assets are loaded.
const requested = new URLSearchParams(location.search).get('modelo') || stage.dataset.modelId || registry.defaultModelId;
const model = registry.models.find(entry => entry.modelId === requested) || registry.models.find(entry => entry.modelId === registry.defaultModelId);
let viewer, loading = false, finishRequest = 0;
function report(message, error = false) { status.textContent = message; status.classList.toggle('is-error', error); }
function showSelection(selection) {
  const fabric = options.fabrics[selection.fabricId], color = options.colors[selection.colorId];
  if (!fabric || !color) return;
  document.querySelectorAll('input[name="sofa-fabric"]').forEach(input => input.checked = input.value === selection.fabricId);
  document.querySelectorAll('input[name="sofa-color"]').forEach(input => input.checked = input.value === selection.colorId);
  $('#sofa-selection-name').textContent = fabric + ' · ' + color;
  const params = new URLSearchParams({referencia: model?.catalogId || 'sofa-organico', estudo: selection.modelId, tecido: selection.fabricId, cor: selection.colorId});
  $('#sofa-quote').href = '/orcamento.html?' + params;
}
async function initialize() {
  if (viewer || loading) return;
  loading = true; start.disabled = true; stage.setAttribute('aria-busy','true');
  report('Preparando a visualização 3D…');
  try {
    if (!model) throw new Error('Modelo 3D não registrado.');
    const {createSofaViewer} = await import('./sofa-pilot/viewer/sofa-viewer.js');
    viewer = await createSofaViewer(stage, {
      baseUrl: model.assets.viewerBase, modelUrls: {main: model.assets.main, mobile: model.assets.mobile},
      onFinish: showSelection, onStatus: message => report(message)
    });
    document.querySelectorAll('.sofa-inspector fieldset, [data-camera]').forEach(control => control.disabled = false);
    stage.classList.add('is-ready');
    report('Pronto. Arraste para girar ou use os controles.');
  } catch {
    report('O 3D não abriu neste navegador. A imagem e o orçamento continuam disponíveis. Você pode tentar novamente.', true);
    start.textContent = 'Tentar abrir o 3D'; start.disabled = false;
  } finally { loading = false; stage.setAttribute('aria-busy','false'); }
}
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
