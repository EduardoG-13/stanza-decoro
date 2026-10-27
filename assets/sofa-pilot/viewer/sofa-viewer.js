import * as THREE from 'three';
import { GLTFLoader } from './vendor/three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from './vendor/three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from './vendor/three/addons/environments/RoomEnvironment.js';

export const IDENTITY = Object.freeze({ modelId: 'stanza-organic-01', revision: '1.3.0' });
export const DIMENSIONS = Object.freeze({ width:2.487, height:0.993, depth:1.084, unit:'m', estimated:true });
export const COLORS = Object.freeze({ areia: '#d8c9b2', oliva: '#72765a', terracota: '#ae6952', grafite: '#494b4b' });
export const FABRICS = Object.freeze({
  linen: { label:'Trama plana', roughness: 1, normalStrength: .78, sheen: .12, sheenRoughness: .85 },
  boucle: { label:'Bouclé', roughness: 1, normalStrength: .9, sheen: .2, sheenRoughness: .9 },
  velvet: { label:'Veludo', roughness: 1, normalStrength: .38, sheen: .72, sheenRoughness: .55 }
});
export const CAMERAS = Object.freeze({
  threequarter: { position:[2.6,1.65,3.1], target:[0,.5,0] },
  front: { position:[0,1.15,4.5], target:[0,.48,0] },
  side: { position:[4.4,1.2,0], target:[0,.48,0] },
  detail: { position:[.55,.63,1], target:[.5,.43,.35] },
  layers: { position:[3.5,2.7,4.5], target:[0,1,0] }
});
const zero = [0,0,0];
// Exported local offsets in metres; original exported transforms are never overwritten.
// All stages are illustrative, not instructions for dismantling a real product.
// FEAT-004: the illustrative opening now reads in the construction order
// fabric -> batting -> foam -> webbing -> wood frame (feet stay with the frame; cushions
// lift with the fabric since they are the loose top layer). Because the real build nests
// the foam and the batting inside the same public `padding` group, each stage also carries
// optional `subOffsets` keyed by the padding sub-node names so the thin manta can separate
// from the foam core WITHOUT adding a new public group. The six public groups are unchanged.
// Contract preserved: progress 0 and 1 are the assembled piece (identical); ~.5 = separated
// (fabric + batting lifted off the foam); ~.7 = structure exposed (foam up, webbing + wood
// frame legible). 1 is NOT redefined as maximum explosion.
const paddingSub = { seat_batting:zero, back_batting:zero, seat_foam:zero, back_foam:zero };
export const LAYER_STAGES = Object.freeze([
  { progress:0, label:'Peça montada',
    offsets:{ upholstery:zero,padding:zero,frame:zero,legs:zero,cushions:zero,suspension:zero },
    subOffsets:{ ...paddingSub }, camera:CAMERAS.threequarter },
  { progress:.2, label:'Almofadas e revestimento se soltam',
    offsets:{ upholstery:[0,.45,.18],padding:zero,frame:zero,legs:zero,cushions:[0,.6,.42],suspension:zero },
    subOffsets:{ ...paddingSub }, camera:{ position:[2.1,1.5,2.6],target:[0,.6,.15] } },
  { progress:.35, label:'Manta exposta sob o tecido',
    offsets:{ upholstery:[0,.95,.42],padding:zero,frame:zero,legs:zero,cushions:[0,1.05,.72],suspension:zero },
    subOffsets:{ seat_batting:[0,.3,.12],back_batting:[0,.3,.12],seat_foam:zero,back_foam:zero }, camera:CAMERAS.layers },
  { progress:.5, label:'Revestimento e manta separados da espuma',
    offsets:{ upholstery:[0,1.25,.55],padding:zero,frame:zero,legs:zero,cushions:[0,1.4,.9],suspension:zero },
    subOffsets:{ seat_batting:[0,.62,.26],back_batting:[0,.62,.26],seat_foam:[0,.18,0],back_foam:[0,.18,0] }, camera:CAMERAS.layers },
  { progress:.7, label:'Estrutura exposta · percintas e madeira',
    offsets:{ upholstery:[0,1.6,.7],padding:[0,.5,0],frame:zero,legs:zero,cushions:[0,1.75,1.05],suspension:[0,.16,0] },
    subOffsets:{ seat_batting:[0,.95,.4],back_batting:[0,.95,.4],seat_foam:[0,.5,.2],back_foam:[0,.5,.2] }, camera:CAMERAS.layers },
  { progress:1, label:'Retorno à peça montada',
    offsets:{ upholstery:zero,padding:zero,frame:zero,legs:zero,cushions:zero,suspension:zero },
    subOffsets:{ ...paddingSub }, camera:CAMERAS.threequarter }
]);
const clamp = (v,a,b) => Math.max(a,Math.min(b,v));
const ease = t => t*t*(3-2*t);
const groups = ['upholstery','padding','frame','legs','cushions','suspension'];
const paddingSubNodes = ['seat_batting','back_batting','seat_foam','back_foam'];

/** Create an independent viewer in a sized HTML element. See API.md. */
export async function createSofaViewer(container, options = {}) {
  if (!(container instanceof HTMLElement)) throw new TypeError('Um elemento HTML é obrigatório.');
  const baseUrl = new URL(options.baseUrl || '../', import.meta.url);
  const variant = options.variant === 'mobile' || (options.variant !== 'main' && matchMedia('(max-width: 760px)').matches) ? 'mobile' : 'main';
  const resources = new Set();
  const materials = new Set();
  const textures = new Set();
  const textureCache = new Map();
  const originalPositions = new Map();
  const convertedMaterials = new Map();
  const embeddedFinishes = new Map();
  const closedImages = new Set();
  let disposed = false, raf = 0, renders = 0, finishToken = 0, progress = 0;
  let loadedRoot, scene, renderer, controls, resizeObserver, environment;
  let desired = { fabricId: options.fabricId || 'boucle', colorId: options.colorId || 'areia' };
  let selection = { ...IDENTITY, ...desired };
  const originalChildren = [...container.children].map(child=>({child,hidden:child.hidden}));
  const abort = new AbortController();
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const canvas = document.createElement('canvas');
  canvas.className = 'sofa-canvas';
  canvas.tabIndex = 0;
  canvas.setAttribute('role','img');
  canvas.setAttribute('aria-label','Sofá tridimensional. Arraste para girar. Setas giram; mais e menos aproximam; Home restaura a vista. A rolagem continua livre.');
  const camera = new THREE.PerspectiveCamera(36,1,.02,100);
  const invalidate = () => {
    if (disposed || raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      if (disposed) return;
      renderer.render(scene,camera); renders++;
    });
  };
  const assertAlive = () => { if (disposed) throw new Error('Visualizador já desmontado.'); };
  function disposeResource(value) {
    if (value?.dispose && !resources.has(value)) {
      value.dispose(); resources.add(value);
      const image=value.isTexture && value.source?.data;
      if(image?.close && !closedImages.has(image)){image.close();closedImages.add(image);}
    }
  }
  function dispose() {
    if (disposed) return;
    disposed = true; finishToken++;
    if (raf) cancelAnimationFrame(raf);
    raf = 0; abort.abort(); resizeObserver?.disconnect(); controls?.dispose();
    scene?.traverse(node => {
      if (node.shadow) disposeResource(node.shadow);
      if (node.geometry) disposeResource(node.geometry);
      for (const material of Array.isArray(node.material) ? node.material : [node.material]) {
        if (!material) continue;
        for (const value of Object.values(material)) if (value?.isTexture) disposeResource(value);
        disposeResource(material);
      }
    });
    textures.forEach(disposeResource); materials.forEach(material=>{
      for (const value of Object.values(material)) if (value?.isTexture) disposeResource(value);
      disposeResource(material);
    });
    disposeResource(environment); renderer?.dispose(); renderer?.forceContextLoss();
    canvas.remove(); originalChildren.forEach(({child,hidden})=>{child.hidden=hidden;});
  }
  async function loadFabric(fabricId) {
    if (textureCache.has(fabricId)) return textureCache.get(fabricId);
    const pending = (async () => {
      const loader = new THREE.TextureLoader();
      // Load each family only when requested; no preload of the other finishes.
      const result = await Promise.all(['basecolor.jpg','normal.png','roughness.jpg'].map(async (name) => {
        const texture = await loader.loadAsync(new URL(`materials/${fabricId}/${name}`,baseUrl).href);
        if (disposed) { texture.dispose(); throw new Error('Visualizador desmontado durante carga.'); }
        textures.add(texture); texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
        texture.flipY = false; texture.colorSpace = name.startsWith('basecolor') ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        texture.anisotropy = Math.min(8,renderer.capabilities.getMaxAnisotropy());
        texture.repeat.set(1,1); return texture;
      }));
      return { map:result[0],normalMap:result[1],roughnessMap:result[2] };
    })();
    textureCache.set(fabricId,pending);
    pending.catch(() => { if (textureCache.get(fabricId) === pending) textureCache.delete(fabricId); });
    return pending;
  }
  async function setFinish(next) {
    assertAlive();
    const candidate = { ...desired,...next };
    if (!Object.hasOwn(FABRICS,candidate.fabricId) || !Object.hasOwn(COLORS,candidate.colorId)) throw new RangeError('Identificador de tecido ou cor inválido.');
    desired = candidate;
    const token = ++finishToken;
    options.onStatus?.('Carregando acabamento…');
    // The GLB embeds sand-colored bouclé. Its color is already baked into baseColor;
    // multiplying by sand again would darken it. Other choices use neutral source maps.
    const useEmbedded = candidate.fabricId === 'boucle' && candidate.colorId === 'areia' && embeddedFinishes.size > 0;
    const maps = useEmbedded ? null : await loadFabric(candidate.fabricId);
    if (disposed || token !== finishToken) return { ...selection };
    const params = FABRICS[candidate.fabricId];
    for (const material of materials) {
      if (!material.userData.stanzaFabric) continue;
      const finishMaps = useEmbedded ? embeddedFinishes.get(material.name) : maps;
      material.map = finishMaps.map; material.normalMap = finishMaps.normalMap; material.roughnessMap = finishMaps.roughnessMap;
      material.color.set(useEmbedded ? '#ffffff' : COLORS[candidate.colorId]); material.metalness = 0;
      material.roughness = params.roughness; material.normalScale.setScalar(params.normalStrength);
      material.sheen = params.sheen; material.sheenRoughness = params.sheenRoughness;
      material.sheenColor.set(COLORS[candidate.colorId]); material.sheenColor.lerp(new THREE.Color('white'),.35);
      material.needsUpdate = true;
    }
    selection = { ...IDENTITY,...candidate };
    options.onFinish?.({ ...selection }); options.onStatus?.('Pronto para explorar'); invalidate();
    return { ...selection };
  }
  function setView(viewId) {
    assertAlive();
    const view = Object.hasOwn(CAMERAS,viewId) && CAMERAS[viewId];
    if (!view) throw new RangeError(`Vista desconhecida: ${viewId}`);
    camera.position.fromArray(view.position); controls.target.fromArray(view.target);
    controls.update(); invalidate();
  }
  function setProgress(value) {
    assertAlive();
    if (!Number.isFinite(value)) throw new TypeError('O progresso deve ser numérico.');
    progress = clamp(value,0,1);
    let after = LAYER_STAGES.findIndex(stage => stage.progress >= progress);
    if (after <= 0) after = 1;
    const a = LAYER_STAGES[after-1], b = LAYER_STAGES[after];
    const t = ease((progress-a.progress)/(b.progress-a.progress));
    for (const name of groups) {
      const node = loadedRoot.getObjectByName(name); if (!node) continue;
      node.position.copy(originalPositions.get(name));
      node.position.add(new THREE.Vector3().fromArray(a.offsets[name]).lerp(new THREE.Vector3().fromArray(b.offsets[name]),t));
    }
    // Padding sub-nodes (foam core vs batting loft) move in their LOCAL padding space,
    // recomputed from their original positions every call (no delta accumulation). Their
    // parent `padding` group offset above is added by the scene graph automatically.
    for (const name of paddingSubNodes) {
      const node = loadedRoot.getObjectByName(name); if (!node || !originalPositions.has(name)) continue;
      const sa = (a.subOffsets && a.subOffsets[name]) || zero;
      const sb = (b.subOffsets && b.subOffsets[name]) || zero;
      node.position.copy(originalPositions.get(name));
      node.position.add(new THREE.Vector3().fromArray(sa).lerp(new THREE.Vector3().fromArray(sb),t));
    }
    if (options.cameraNarrative !== false) {
      camera.position.fromArray(a.camera.position).lerp(new THREE.Vector3().fromArray(b.camera.position),t);
      controls.target.fromArray(a.camera.target).lerp(new THREE.Vector3().fromArray(b.camera.target),t);
      controls.update();
    }
    const nearest = LAYER_STAGES.reduce((best,s) => Math.abs(progress-s.progress)<Math.abs(progress-best.progress)?s:best);
    options.onProgress?.(progress,nearest.label); invalidate();
  }
  function zoom(amount) {
    assertAlive();
    if (!Number.isFinite(amount) || amount <= 0) throw new TypeError('A aproximação deve ser um número positivo.');
    const offset = camera.position.clone().sub(controls.target);
    offset.setLength(clamp(offset.length()*amount,.45,9));
    camera.position.copy(controls.target).add(offset); controls.update(); invalidate();
  }
  function rotate(angle) {
    assertAlive();
    const offset = camera.position.clone().sub(controls.target);
    offset.applyAxisAngle(new THREE.Vector3(0,1,0),angle);
    camera.position.copy(controls.target).add(offset); controls.update(); invalidate();
  }
  try {
    const context = canvas.getContext('webgl2',{ antialias:true,alpha:false,preserveDrawingBuffer:options.preserveDrawingBuffer === true });
    if (!context) throw new Error('WebGL 2 não está disponível neste navegador. Use o poster e as imagens do pacote.');
    renderer = new THREE.WebGLRenderer({ canvas,context,antialias:true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, variant==='mobile'?1.5:2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = .9;
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    scene = new THREE.Scene(); scene.background = new THREE.Color(options.backgroundColor || '#e9e6e0');
    const room = new RoomEnvironment();
    const pmrem = new THREE.PMREMGenerator(renderer);
    environment = pmrem.fromScene(room,.05); scene.environment = environment.texture;
    scene.environmentIntensity = .35; room.dispose(); pmrem.dispose();
    scene.add(new THREE.HemisphereLight(0xf8f4e9,0x95958b,.65));
    const key = new THREE.DirectionalLight(0xfff9ed,2.3); key.position.set(-3,5,4); key.castShadow=true;
    key.shadow.mapSize.set(2048,2048); key.shadow.camera.left=-4; key.shadow.camera.right=4;
    key.shadow.camera.top=5; key.shadow.camera.bottom=-3; key.shadow.normalBias=.018; key.shadow.bias=-.0001;
    key.shadow.camera.near=.1; key.shadow.camera.far=15; scene.add(key);
    const fill = new THREE.DirectionalLight(0xe5ebff,.45); fill.position.set(4,2,-2); scene.add(fill);
    const floorMaterial = new THREE.MeshStandardMaterial({ color:options.floorColor || 0xe5e2dc,roughness:1,metalness:0 });
    const floor = new THREE.Mesh(new THREE.CircleGeometry(12,96),floorMaterial); floor.rotation.x=-Math.PI/2; floor.position.y=-.009; floor.receiveShadow=true; scene.add(floor);
    controls = new OrbitControls(camera,canvas); controls.enableDamping=false; controls.enablePan=false;
    // OrbitControls sets touch-action:none on connect; retain vertical native scrolling.
    canvas.style.touchAction='pan-y';
    // Wheel remains native page scrolling. Use visible +/- buttons or keyboard to zoom.
    controls.enableZoom=false; controls.minDistance=.45; controls.maxDistance=9;
    controls.minPolarAngle=.08; controls.maxPolarAngle=Math.PI*.48;
    controls.addEventListener('change',invalidate);
    canvas.addEventListener('keydown',event => {
      const handled = ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','_','Home'];
      if (!handled.includes(event.key)) return;
      event.preventDefault();
      if (event.key==='Home') setView('threequarter');
      else if (event.key==='ArrowLeft') rotate(-.12);
      else if (event.key==='ArrowRight') rotate(.12);
      else if (event.key==='+' || event.key==='=') zoom(.9);
      else if (event.key==='-' || event.key==='_') zoom(1.1);
      else {
        const offset = camera.position.clone().sub(controls.target);
        const spherical = new THREE.Spherical().setFromVector3(offset);
        spherical.phi = clamp(spherical.phi+(event.key==='ArrowUp'?-.08:.08),.08,Math.PI*.48);
        camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); controls.update(); invalidate();
      }
    },{ signal:abort.signal });
    canvas.addEventListener('webglcontextlost',event => { event.preventDefault(); options.onStatus?.('Contexto gráfico perdido. Recarregue para continuar.'); },{ signal:abort.signal });
    const loader = new GLTFLoader();
    const url = options.modelUrl ? new URL(options.modelUrl,baseUrl).href : new URL(variant==='mobile'?'models/sofa-mobile.glb':'models/sofa.glb',baseUrl).href;
    const gltf = await loader.loadAsync(url);
    loadedRoot = gltf.scene;
    if (!loadedRoot.getObjectByName('sofa_root')) throw new Error('O GLB não contém o nó sofa_root.');
    for (const name of groups) {
      const node = loadedRoot.getObjectByName(name);
      if (node) originalPositions.set(name,node.position.clone());
      else if (name !== 'suspension') throw new Error(`Grupo ausente no GLB: ${name}`);
    }
    // FEAT-004: remember the padding sub-nodes (foam/batting) so the opening can separate
    // the thin manta from the foam core without introducing a new public group. Absent on
    // pre-1.2.0 assets; the opening then simply moves the padding group as a whole.
    for (const name of paddingSubNodes) {
      const node = loadedRoot.getObjectByName(name);
      if (node) originalPositions.set(name,node.position.clone());
    }
    loadedRoot.traverse(node => {
      if (!node.isMesh) return;
      // Millimetre welts receive lighting but do not cast subpixel shadow-map speckles.
      node.castShadow = !/(seam|welt)/.test(node.name);
      node.receiveShadow = true;
      const convert = material => {
        if (convertedMaterials.has(material)) return convertedMaterials.get(material);
        materials.add(material);
        if (!['fabric_main','fabric_seam'].includes(material.name)) return material;
        // Physical material preserves the MR baseline and adds optional sheen for velvet.
        const physical = new THREE.MeshPhysicalMaterial();
        THREE.MeshStandardMaterial.prototype.copy.call(physical,material);
        physical.name=material.name; physical.userData.stanzaFabric=true; materials.add(physical);
        convertedMaterials.set(material,physical);
        if (material.map && material.normalMap && material.roughnessMap) {
          const maps={map:material.map,normalMap:material.normalMap,roughnessMap:material.roughnessMap};
          embeddedFinishes.set(material.name,maps);
          Object.values(maps).forEach(texture=>{
            textures.add(texture); texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
          });
        }
        return physical;
      };
      node.material = Array.isArray(node.material)?node.material.map(convert):convert(node.material);
    });
    scene.add(loadedRoot);
    if (![...materials].some(material=>material.userData.stanzaFabric)) throw new Error('Nenhum material fabric_main ou fabric_seam foi exportado.');
    await setFinish(desired);
    container.append(canvas); originalChildren.forEach(({child})=>{child.hidden=true;});
    const resize = () => {
      if (disposed) return;
      const width=Math.max(container.clientWidth,1),height=Math.max(container.clientHeight,1);
      renderer.setSize(width,height,false); camera.aspect=width/height; camera.updateProjectionMatrix(); invalidate();
    };
    resizeObserver=new ResizeObserver(resize); resizeObserver.observe(container); resize(); setProgress(0);
    const api = Object.freeze({ setProgress,setFinish,setView,getSelection:()=>({...selection}),dispose,zoom,rotate,
      inspect:()=>({ ...IDENTITY,variant,progress,disposed,reducedMotion:reducedMotion.matches,renders,
        texturesLoaded:[...(embeddedFinishes.size?['boucle:embedded-areia']:[]),...textureCache.keys()],camera:{position:camera.position.toArray(),target:controls.target.toArray()},
        groups:Object.fromEntries(groups.filter(name=>originalPositions.has(name)).map(name=>[name,loadedRoot.getObjectByName(name).position.toArray()])),
        canvas:{width:canvas.width,height:canvas.height}, renderer:renderer.info.render,
        disposal:{resources:resources.size,imageBitmapsClosed:closedImages.size},
        fabricMaterials:[...materials].filter(material=>material.userData.stanzaFabric).map(material=>({
          name:material.name,color:material.color.getHexString(),metalness:material.metalness,
          roughness:material.roughness,sheen:material.sheen,normalScale:material.normalScale.toArray(),
          maps:Object.fromEntries(['map','normalMap','roughnessMap'].map(key=>[key,material[key]?{
            uuid:material[key].uuid,colorSpace:material[key].colorSpace,width:material[key].image?.width,height:material[key].image?.height
          }:null]))
        })),
        bounds:new THREE.Box3().setFromObject(loadedRoot).getSize(new THREE.Vector3()).toArray()
      })
    });
    return api;
  } catch (error) { dispose(); throw error; }
}
