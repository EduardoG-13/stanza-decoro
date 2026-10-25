// Separate, optional adapter: download GSAP only on the first scroll opt-in.
let library;
async function getScrollTrigger() {
  if (!library) library=Promise.all([
    import('./vendor/gsap/index.js'),import('./vendor/gsap/ScrollTrigger.js')
  ]).then(([{gsap},{ScrollTrigger}])=>{gsap.registerPlugin(ScrollTrigger);return ScrollTrigger;});
  return library;
}

/** Opt-in scroll demonstration; no pinning, snapping, scroll lock or independent model logic. */
export function attachScrollSequence({ viewer,trigger,onProgress=()=>{},onError=()=>{} }) {
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
  let effect=null,enabled=false,disposed=false,generation=0;
  function stop() { generation++; effect?.kill(); effect=null; }
  async function refresh() {
    stop();
    if (disposed || !enabled || reducedMotion.matches) return;
    const current=generation;
    try {
      const ScrollTrigger=await getScrollTrigger();
      if(disposed || !enabled || reducedMotion.matches || current!==generation)return;
      // Clamp the end to the document's reachable scroll extent so return=1 is
      // attainable even when the short demo area sits immediately above a footer.
      effect=ScrollTrigger.create({ trigger,start:'clamp(top 80%)',end:'clamp(bottom 35%)',
        onUpdate:self=>{ viewer.setProgress(self.progress); onProgress(self.progress); }
      });
      effect.refresh();viewer.setProgress(effect.progress);onProgress(effect.progress);
    } catch(error) { if(!disposed && current===generation)onError(error); }
  }
  reducedMotion.addEventListener('change',refresh);
  return { setEnabled(value){if(disposed)return;enabled=Boolean(value);return refresh();},
    isEnabled:()=>!disposed&&enabled&&!reducedMotion.matches,
    dispose(){if(disposed)return;disposed=true;stop();reducedMotion.removeEventListener('change',refresh);}
  };
}
