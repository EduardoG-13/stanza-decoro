import * as THREE from 'three';
import { GLTFLoader } from './vendor/three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from './vendor/three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from './vendor/three/addons/environments/RoomEnvironment.js';

export const IDENTITY = Object.freeze({ modelId: 'stanza-organic-01', revision: '2.1.0' });
export const DIMENSIONS = Object.freeze({ width:2.503, height:1.132, depth:1.098, unit:'m', estimated:true });
// Colour IDs are global and only ever ADDED (never renamed); each model exposes a subset.
// gelo (EXT-002): cool light grey of the bouclé in SOFA-5.jpg (visual estimate).
// grafite-quente (EXT-003): warm dark grey of the twill in SOFA-3.jpg (visual estimate).
// cru (EXT-004): warm off-white of the linen-look cloth in sofa-dois-assentos.webp (visual estimate).
// cinza-malva (EXT-005): mauve-tinted mid grey of sofa-com-vivo.webp (visual estimate).
// petroleo (EXT-014): deep teal-blue velvet of poltronas-11.jpg (visual estimate).
export const COLORS = Object.freeze({ areia: '#b6b0a8', oliva: '#72765a', terracota: '#ae6952', grafite: '#494b4b', gelo: '#babcc0', 'grafite-quente': '#545050', cru: '#e2ddd2', 'cinza-malva': '#8a8286', petroleo: '#0e5668' });
export const FABRICS = Object.freeze({
  linen: { label:'Trama plana', roughness: 1, normalStrength: .78, sheen: .12, sheenRoughness: .85, repeatMeters: .14 },
  boucle: { label:'Bouclé', roughness: 1, normalStrength: 1.8, sheen: .12, sheenRoughness: .95, repeatMeters: .30 },
  velvet: { label:'Veludo', roughness: 1, normalStrength: .38, sheen: .72, sheenRoughness: .55, repeatMeters: .14 },
  // EXT-002: heathered bouclé of SOFA-5.jpg (shared library assets/models-3d/materials/boucle-mescla).
  'boucle-mescla': { label:'Bouclé mescla', roughness: 1, normalStrength: 1.5, sheen: .12, sheenRoughness: .95, repeatMeters: .30 },
  // EXT-003: flat matte 2/2 twill of SOFA-3.jpg (assets/models-3d/materials/sarja).
  sarja: { label:'Sarja', roughness: 1, normalStrength: .9, sheen: .10, sheenRoughness: .8, repeatMeters: .30 },
  // EXT-004: slubbed linen-look plain weave of sofa-dois-assentos.webp (assets/models-3d/materials/linho-rustico).
  'linho-rustico': { label:'Linho rústico', roughness: 1, normalStrength: 1, sheen: .10, sheenRoughness: .85, repeatMeters: .30 }
});
// 2.1.0: one body UV unit = BODY_UV_METERS (build_sofa.BODY_TILE). Each fabric's maps are scaled
// with texture.repeat so they keep their own physical repeat (bouclé 0.30 m = the embedded maps).
export const BODY_UV_METERS = .30;
export const CAMERAS = Object.freeze({
  threequarter: { position:[2.6,1.65,3.1], target:[0,.5,0] },
  front: { position:[0,1.15,4.5], target:[0,.48,0] },
  side: { position:[4.4,1.2,0], target:[0,.48,0] },
  detail: { position:[.55,.63,1], target:[.5,.43,.35] },
  // SOFA-2.jpg angle. 2.1.0: re-fitted against the photo (closer, from slightly left of centre,
  // looking down onto the seat as the photographer did); 2.0.0 was [.4,1.13,3.05] -> [-.05,.5,0].
  photo: { position:[-.15,1.35,2.45], target:[-.05,.55,0] }
});
const zero = [0,0,0];
// EXT-001 / 2.0.0: exterior-only asset. The illustrative layered opening (FEAT-004) and the
// interior groups padding/frame/suspension were removed. LAYER_STAGES survives only as a
// DEPRECATED single assembled stage so old importers keep working; setProgress() is a no-op
// that keeps the assembled piece. Do not build new UI on either.
export const LAYER_STAGES = Object.freeze([
  Object.freeze({ progress:0, label:'Peça montada', offsets:Object.freeze({ upholstery:zero,legs:zero,cushions:zero }), camera:CAMERAS.threequarter })
]);
// Material regions. ONLY body materials are customizable (stanzaFabric). Decorative cushion
// covers/welts keep their fixed reference finish; the feet keep their dark finish. The region
// comes from the GLB material extras (`stanza_region`), with these names as fallback.
export const MATERIAL_REGIONS = Object.freeze({
  body: Object.freeze(['fabric_main','fabric_seam']),
  decorative: Object.freeze(['cushion_light_boucle','cushion_light_seam','cushion_olive_weave','cushion_olive_seam','cushion_olive_reverse']),
  'exterior-structure': Object.freeze(['legs_dark'])
});
// Fixed decorative look (sheen is a viewer-side MeshPhysicalMaterial addition; maps/colours come from the GLB).
const DECORATIVE = Object.freeze({
  cushion_light_boucle: { sheen:.15, sheenRoughness:.95, sheenColor:'#e6e1d8' },
  cushion_light_seam: { sheen:.15, sheenRoughness:.95, sheenColor:'#e6e1d8' },
  cushion_olive_weave: { sheen:.12, sheenRoughness:.8, sheenColor:'#b9b48a' },
  cushion_olive_seam: { sheen:.12, sheenRoughness:.8, sheenColor:'#b9b48a' },
  cushion_olive_reverse: { sheen:.15, sheenRoughness:.85, sheenColor:'#f1ece0' }
});
// Multi-model (models3d pipeline): a model registered in data/models-3d.json is passed as
// options.model ({modelId, revision, materialRegions, options:{fabrics, colors, default}, cameras}).
// Without it the viewer behaves exactly as for EXT-001 (stanza-organic-01).
export const REGION_NAMES = Object.freeze(['body','decorative','contrast','exterior-structure']);
export const DEFAULT_MODEL_OPTIONS = Object.freeze({
  fabrics: Object.freeze(['boucle','linen','velvet']), colors: Object.freeze(['areia','oliva','terracota','grafite']),
  default: Object.freeze({ fabricId:'boucle', colorId:'areia' })
});
/** Camera presets framed from model bounds (glTF axes: +Z front, Y up). Pure, testable. */
export const framedCameras = (min, max) => {
  const c = [0,1,2].map(k => (min[k]+max[k])/2), s = [0,1,2].map(k => max[k]-min[k]);
  const r = Math.hypot(s[0], s[1]*.8, s[2]) / 2, dist = r / Math.tan(18*Math.PI/180) * 1.05;
  const ty = min[1] + s[1]*.42, target = [c[0],ty,c[2]].map(v=>+v.toFixed(3));
  const at = (dx,dy,dz,k=1) => { const L = Math.hypot(dx,dy,dz); return [c[0]+dx/L*dist*k, ty+dy/L*dist*k, c[2]+dz/L*dist*k].map(v=>+v.toFixed(3)); };
  const dt = [max[0]-s[0]*.22, min[1]+s[1]*.40, max[2]-s[2]*.12].map(v=>+v.toFixed(3));
  return {
    threequarter: { position:at(.62,.36,.70), target },
    front: { position:at(0,.24,1), target },
    side: { position:at(1,.22,0,.85), target },
    back: { position:at(-.35,.32,-1), target },
    detail: { position:[dt[0]+.25,dt[1]+.22,dt[2]+.7].map(v=>+v.toFixed(3)), target:dt },
    photo: { position:at(-.5,.4,.8), target }
  };
};
const clamp = (v,a,b) => Math.max(a,Math.min(b,v));
const ease = t => t*t*(3-2*t);
const groups = ['upholstery','legs','cushions'];
function regionOf(material, regions = MATERIAL_REGIONS) {
  const tagged = material.userData?.stanza_region;
  if (tagged && REGION_NAMES.includes(tagged)) return tagged;
  for (const [region,names] of Object.entries(regions)) if (names.includes(material.name)) return region;
  return 'other';
}
const parseExtra = value => { if (typeof value !== 'string') return value ?? null; try { return JSON.parse(value); } catch { return null; } };

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
  const model = options.model || null;
  let modelOptions = model?.options || DEFAULT_MODEL_OPTIONS;
  let allowedFabrics = modelOptions.fabrics.filter(id => Object.hasOwn(FABRICS,id));
  let allowedColors = modelOptions.colors.filter(id => Object.hasOwn(COLORS,id));
  // The initial finish is the one embedded in the GLB (pre-tinted maps, white multiplier).
  let embedded = { ...(modelOptions.embedded || modelOptions.default || DEFAULT_MODEL_OPTIONS.default) };
  let identity = model ? { modelId:model.modelId, revision:model.revision } : { ...IDENTITY };
  let regions = model?.materialRegions || MATERIAL_REGIONS;
  let cameras = CAMERAS;
  let desired = { fabricId: options.fabricId || modelOptions.default?.fabricId || 'boucle', colorId: options.colorId || modelOptions.default?.colorId || 'areia' };
  let selection = { ...identity, ...desired };
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
        // Shared material library: options.materialUrls maps a fabric family to its folder.
        const folder = new URL(options.materialUrls?.[fabricId] || `materials/${fabricId}/`,baseUrl);
        const texture = await loader.loadAsync(new URL(name,folder).href);
        if (disposed) { texture.dispose(); throw new Error('Visualizador desmontado durante carga.'); }
        textures.add(texture); texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
        texture.flipY = false; texture.colorSpace = name.startsWith('basecolor') ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        texture.anisotropy = Math.min(8,renderer.capabilities.getMaxAnisotropy());
        const k = BODY_UV_METERS / FABRICS[fabricId].repeatMeters; texture.repeat.set(k,k); return texture;
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
    if (!allowedFabrics.includes(candidate.fabricId) || !allowedColors.includes(candidate.colorId)) throw new RangeError('Identificador de tecido ou cor inválido.');
    desired = candidate;
    const token = ++finishToken;
    options.onStatus?.('Carregando acabamento…');
    // The GLB embeds sand-colored bouclé. Its color is already baked into baseColor;
    // multiplying by sand again would darken it. Other choices use neutral source maps.
    const useEmbedded = candidate.fabricId === embedded.fabricId && candidate.colorId === embedded.colorId && embeddedFinishes.size > 0;
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
    selection = { ...identity,...candidate };
    options.onFinish?.({ ...selection }); options.onStatus?.('Pronto para explorar'); invalidate();
    return { ...selection };
  }
  function setView(viewId) {
    assertAlive();
    const view = Object.hasOwn(cameras,viewId) && cameras[viewId];
    if (!view) throw new RangeError(`Vista desconhecida: ${viewId}`);
    // Fitted views (view.fov, authored for a 4:3 photo) keep their horizontal field on narrower canvases.
    const fitted = view.fov && camera.aspect < 4/3 ? 2*Math.atan(Math.tan(view.fov*Math.PI/360)*(4/3)/camera.aspect)*180/Math.PI : view.fov;
    camera.fov = fitted || 36; camera.updateProjectionMatrix();
    camera.position.fromArray(view.position); controls.target.fromArray(view.target);
    controls.update(); invalidate();
  }
  // DEPRECATED since 2.0.0: exterior-only asset, no layered opening. Kept for compatibility:
  // validates the argument, keeps the assembled piece and reports the single stage.
  function setProgress(value) {
    assertAlive();
    if (!Number.isFinite(value)) throw new TypeError('O progresso deve ser numérico.');
    progress = 0;
    options.onProgress?.(0,LAYER_STAGES[0].label);
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
    const variantUrl = options.modelUrls?.[variant];
    const url = new URL(options.modelUrl || variantUrl || (variant==='mobile'?'models/sofa-mobile.glb':'models/sofa.glb'),baseUrl).href;
    const gltf = await loader.loadAsync(url);
    loadedRoot = gltf.scene;
    const rootNode = loadedRoot.getObjectByName('sofa_root') || loadedRoot.getObjectByName('model_root');
    if (!rootNode) throw new Error('O GLB não contém o nó sofa_root.');
    const extras = rootNode.userData || {};
    if (model && extras.modelId && (extras.modelId !== model.modelId || (extras.revision && extras.revision !== model.revision)))
      throw new Error('O GLB não corresponde ao modelo registrado.');
    if (!model && extras.modelId && extras.modelId !== IDENTITY.modelId) {
      // Unregistered non-EXT-001 GLB loaded directly (e.g. capture harness): trust its own extras.
      identity = { modelId:extras.modelId, revision:extras.revision || '' };
      embedded = parseExtra(extras.embeddedFinish) || embedded;
      allowedFabrics = Object.keys(FABRICS); allowedColors = Object.keys(COLORS);
      if (!options.fabricId && !options.colorId) desired = { ...embedded };
    }
    if (!model?.materialRegions && extras.materialRegions) regions = parseExtra(extras.materialRegions) || regions;
    for (const name of groups) {
      const node = loadedRoot.getObjectByName(name);
      if (!node) throw new Error(`Grupo ausente no GLB: ${name}`);
      originalPositions.set(name,node.position.clone());
    }
    loadedRoot.traverse(node => {
      if (!node.isMesh) return;
      // Millimetre welts receive lighting but do not cast subpixel shadow-map speckles.
      node.castShadow = !/(seam|welt)/.test(node.name);
      node.receiveShadow = true;
      // GLTFLoader may hand out the same material instance to several meshes (or clones that
      // keep the name); conversion is cached per instance and classified per material, never
      // by mesh, so a body instance can never be shared with a cushion and vice versa.
      const convert = material => {
        if (convertedMaterials.has(material)) return convertedMaterials.get(material);
        const region = regionOf(material,regions);
        if (region !== 'body' && region !== 'decorative') {
          material.userData.stanzaRegion = region; materials.add(material); convertedMaterials.set(material,material); return material;
        }
        // Physical material preserves the MR baseline and adds sheen (velvet / soft fibres).
        const physical = new THREE.MeshPhysicalMaterial();
        THREE.MeshStandardMaterial.prototype.copy.call(physical,material);
        physical.name = material.name; physical.userData = { ...material.userData, stanzaRegion:region, stanzaFabric: region === 'body' };
        materials.add(physical); convertedMaterials.set(material,physical);
        [physical.map,physical.normalMap,physical.roughnessMap].forEach(texture=>{
          if (!texture) return; textures.add(texture); texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
        });
        if (region === 'body') {
          if (material.map && material.normalMap && material.roughnessMap && !embeddedFinishes.has(material.name))
            embeddedFinishes.set(material.name,{map:material.map,normalMap:material.normalMap,roughnessMap:material.roughnessMap});
        } else {
          const look = DECORATIVE[material.name] || { sheen:.15, sheenRoughness:.85, sheenColor:'#ffffff' };
          physical.metalness = 0; physical.sheen = look.sheen; physical.sheenRoughness = look.sheenRoughness; physical.sheenColor.set(look.sheenColor);
          physical.needsUpdate = true;
        }
        return physical;
      };
      node.material = Array.isArray(node.material)?node.material.map(convert):convert(node.material);
    });
    scene.add(loadedRoot);
    if (identity.modelId !== IDENTITY.modelId) {
      const box = new THREE.Box3().setFromObject(loadedRoot);
      cameras = { ...framedCameras(box.min.toArray(),box.max.toArray()), ...(model?.cameras || {}) };
    }
    if (![...materials].some(material=>material.userData.stanzaFabric)) throw new Error('Nenhum material de corpo (fabric_main/fabric_seam) foi exportado.');
    await setFinish(desired);
    container.append(canvas); originalChildren.forEach(({child})=>{child.hidden=true;});
    const resize = () => {
      if (disposed) return;
      const width=Math.max(container.clientWidth,1),height=Math.max(container.clientHeight,1);
      renderer.setSize(width,height,false); camera.aspect=width/height; camera.updateProjectionMatrix(); invalidate();
    };
    resizeObserver=new ResizeObserver(resize); resizeObserver.observe(container); resize();
    const api = Object.freeze({ setProgress,setFinish,setView,getSelection:()=>({...selection}),dispose,zoom,rotate,
      inspect:()=>({ ...identity,variant,progress,disposed,reducedMotion:reducedMotion.matches,renders,
        texturesLoaded:[...(embeddedFinishes.size?[`${embedded.fabricId}:embedded-${embedded.colorId}`]:[]),...textureCache.keys()],camera:{position:camera.position.toArray(),target:controls.target.toArray(),fov:camera.fov},
        options:{ fabrics:[...allowedFabrics], colors:[...allowedColors], embedded:{...embedded} }, views:Object.keys(cameras),
        groups:Object.fromEntries(groups.filter(name=>originalPositions.has(name)).map(name=>[name,loadedRoot.getObjectByName(name).position.toArray()])),
        canvas:{width:canvas.width,height:canvas.height}, renderer:renderer.info.render,
        disposal:{resources:resources.size,imageBitmapsClosed:closedImages.size},
        construction:rootNode.userData?.construction ?? null,
        meshes:(()=>{const names=[];loadedRoot.traverse(n=>{if(n.isMesh)names.push(n.name);});return names;})(),
        materialRegions:[...materials].map(material=>({ name:material.name, region:material.userData.stanzaRegion,
          stanzaFabric:material.userData.stanzaFabric===true, type:material.type, color:material.color?.getHexString(),
          sheen:material.sheen ?? null, map:material.map?.uuid ?? null })),
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
