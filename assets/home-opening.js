// Home hero: decorative EXTERIOR rotation only (no layer opening since 2.0.0). Motion exists
// only while the product is visible and the tab is active; reduced motion / Save-Data keep the poster.
const host = document.querySelector('#home-sofa');
const motion = matchMedia('(prefers-reduced-motion: reduce)');
const connection = navigator.connection;
let viewer, frame = 0, initialized = false, disposed = false, visible = false;
let lastStep = 0, observer, sizingObserver, headingAngle = 0;
const radiansPerSecond = Math.PI * 2 / 38;
function stop() {cancelAnimationFrame(frame); frame = 0; lastStep = 0;}
function state() {
  if (motion.matches || document.documentElement.classList.contains('reduce-motion')) return 'reduced';
  if (document.hidden) return 'background';
  if (!visible) return 'offscreen';
  return viewer ? 'running' : 'poster';
}
function reconcile() {
  if (disposed) return;
  const next = state();
  host.dataset.motionState = next;
  if (next !== 'running') {stop(); return;}
  if (!frame) frame = requestAnimationFrame(tick);
}
function tick(now) {
  frame = 0;
  if (disposed || state() !== 'running') {reconcile(); return;}
  if (!lastStep) lastStep = now;
  const delta = now - lastStep;
  // Ambient rotation renders at most 30 times per second, without a catch-up jump.
  if (delta >= 1000/30) {
    const step = radiansPerSecond * Math.min(delta,100)/1000;
    viewer.rotate(step); headingAngle = (headingAngle + step) % (Math.PI * 2); lastStep = now;
  }
  frame = requestAnimationFrame(tick);
}
async function initialize() {
  if (initialized || disposed || state() === 'reduced' || connection?.saveData || /(^|-)2g$/.test(connection?.effectiveType || '')) return;
  initialized = true; host.dataset.scene = 'loading';
  try {
    const {createSofaViewer} = await import('./sofa-pilot/viewer/sofa-viewer.js');
    if (disposed || state() === 'reduced') {initialized = false; host.dataset.scene = 'poster'; return;}
    viewer = await createSofaViewer(host, {variant:'mobile', backgroundColor:'#f4f1e9', floorColor:'#f4f1e9'});
    if (disposed) {viewer.dispose(); return;}
    const fit = () => {
      const aspect = Math.max(host.clientWidth,1) / Math.max(host.clientHeight,1);
      // fit:false keeps the hero's own aspect-based framing (the viewer's auto-fit would back off twice).
      viewer.setView('threequarter', {fit:false}); viewer.zoom(Math.max(1,1.12/aspect));
      viewer.rotate(headingAngle);
    };
    fit(); sizingObserver = new ResizeObserver(fit); sizingObserver.observe(host);
    const canvas = host.querySelector('canvas');
    canvas.tabIndex = -1; canvas.setAttribute('aria-hidden','true'); canvas.style.pointerEvents = 'none';
    host.dataset.scene = 'ready';
    reconcile();
  } catch {host.dataset.scene = 'poster';}
}
function onVisibility() {reconcile();}
function onMotion() {if (!motion.matches && visible && !viewer) initialize(); reconcile();}
document.addEventListener('visibilitychange', onVisibility);
motion.addEventListener('change', onMotion);
document.addEventListener('stanza:motion', onMotion);
if ('IntersectionObserver' in window) {
  observer = new IntersectionObserver(entries => {
    visible = entries.some(entry => entry.isIntersecting);
    if (visible) initialize();
    reconcile();
  }, {threshold:0});
  observer.observe(host);
} else {visible = true; initialize();}
window.addEventListener('pageshow', reconcile);
window.addEventListener('pagehide', event => {
  stop();
  if (event.persisted) return;
  disposed = true; observer?.disconnect(); sizingObserver?.disconnect(); viewer?.dispose();
  document.removeEventListener('visibilitychange', onVisibility); motion.removeEventListener('change', onMotion);
  window.removeEventListener('pageshow', reconcile); document.removeEventListener('stanza:motion', onMotion);
});
