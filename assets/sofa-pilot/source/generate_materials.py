"""Original tileable PBR fabric studies for Stanza sofa pilot.

Run: python source/generate_materials.py
Requirements: numpy==2.5.2, Pillow==12.3.0. No network or third-party art.
All sampling is periodic. One UV repetition represents 0.14 metres.
Base colors have dye/fibre variation only, never baked illumination.
Normals: tangent-space OpenGL (+Y), RGB data, derived from metre heights.
Roughness: RGB data with identical channels (glTF uses green).
The thumbnails alone contain an illustrative grazing-light calculation.
Embedded variants use the areia tint [216, 201, 178] in sRGB; source maps stay neutral.
The 512-pixel variants cover the same 0.14-metre UV repeat as the full-size maps.
Original procedural output: CC0-1.0, to the extent rights exist.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
N = 1024
REPEAT_M = 0.14
Y, X = np.mgrid[0:N, 0:N].astype(np.float64)


def noise(rng, sx, sy=None):
    """Exactly periodic, normalized filtered noise; sigma in pixels."""
    if sy is None:
        sy = sx
    fx = np.fft.fftfreq(N)[None, :]
    fy = np.fft.fftfreq(N)[:, None]
    smooth = np.exp(-2 * np.pi**2 * (sx*sx*fx*fx + sy*sy*fy*fy))
    out = np.fft.ifft2(np.fft.fft2(rng.standard_normal((N, N))) * smooth).real
    return out / max(out.std(), 1e-8)


def normals(height):
    # Image rows run down; UV +v runs up: the green derivative is inverted.
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2*REPEAT_M/N)
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2*REPEAT_M/N)
    normal = np.stack([-dx, dy, np.ones_like(dx)], -1)
    return normal / np.linalg.norm(normal, axis=-1, keepdims=True)


def write_family(fabric_id, height, color, roughness, settings):
    folder = ROOT / 'materials' / fabric_id
    folder.mkdir(parents=True, exist_ok=True)
    normal = normals(height)
    color = np.clip(np.repeat(color[..., None], 3, -1), 0, 1)
    roughness = np.clip(roughness, 0, 1)
    Image.fromarray(np.uint8(np.round(color*255))).save(folder/'basecolor.jpg', quality=92, subsampling=0, optimize=True)
    Image.fromarray(np.uint8(np.round((normal*0.5+0.5)*255))).save(folder/'normal.png', optimize=True)
    Image.fromarray(np.uint8(np.round(np.repeat(roughness[...,None],3,-1)*255))).save(folder/'roughness.jpg', quality=93, subsampling=0, optimize=True)
    # Derive a close swatch from those same maps. This is UI art, never basecolor.
    light = np.array([-0.65,0.35,0.72]); light /= np.linalg.norm(light)
    lit = np.clip(normal@light,0,1)
    thumb = np.clip(color * (0.58+0.47*lit[...,None]),0,1)
    Image.fromarray(np.uint8(thumb*255)).crop((256,256,768,768)).resize((256,256),Image.Resampling.LANCZOS).save(folder/'thumbnail.jpg',quality=90,optimize=True)
    settings.update({
        'id':fabric_id,'repeatMeters':REPEAT_M,'textureSize':[N,N],
        'baseColorSpace':'sRGB','normalColorSpace':'linear-data','roughnessColorSpace':'linear-data',
        'normalConvention':'OpenGL +Y','metalness':0,
        'maps':{k:f'materials/{fabric_id}/{v}' for k,v in {'baseColor':'basecolor.jpg','normal':'normal.png','roughness':'roughness.jpg','thumbnail':'thumbnail.jpg'}.items()},
        'license':'CC0-1.0','source':'source/generate_materials.py',
        'validation':{'baseColorMean':float(color.mean()),'roughnessMean':float(roughness.mean()),'normalLengthMaxErrorBeforeQuantization':float(np.abs(np.linalg.norm(normal,axis=-1)-1).max()),'periodicity':'periodic Fourier noise, modular weave/loop sampling and wrapped normal derivatives'}
    })
    print(f'{fabric_id}: '+', '.join(f'{p.name}={p.stat().st_size}' for p in folder.iterdir()))
    return settings


def linen():
    rng=np.random.default_rng(501)
    # Interlacing 112 warp/weft ends across 140 mm; periodic slub modulation.
    wx=2*np.pi*(X*112/N + .022*noise(rng,14,90))
    wy=2*np.pi*(Y*112/N + .022*noise(rng,90,14))
    warp=np.maximum(0,np.cos(wx))**0.7
    weft=np.maximum(0,np.cos(wy))**0.7
    crossing=.5+.5*np.sin(wx*.5)*np.sin(wy*.5)
    weave = warp*(.58+.42*crossing)+weft*(1-.42*crossing)
    slub=.6*noise(rng,.7,15)+.4*noise(rng,15,.7)
    fuzz=noise(rng,.7)
    height=weave*.000095+slub*.000012+fuzz*.000004
    # Dye variation follows fibres, not their shadowing.
    color=.925+.011*slub+.003*fuzz+.005*noise(rng,3,30)
    rough=.86+.022*fuzz+.028*(1-weave)
    return write_family('linen',height,color,rough,{'label':'Trama plana','family':'plain_weave_linen_study','seed':501,'normalScale':.78,'roughness':1.0,'sheen':.12,'sheenRoughness':.85,'description':'Trama plana alternada, fios de aproximadamente 1,25 mm e espessura irregular discreta. Estudo visual sem composicao comercial atribuida.'})


def boucle():
    rng=np.random.default_rng(502)
    height=np.zeros((N,N))
    dye=np.zeros((N,N))
    # Individual soft loops of variable orientation and length, periodically wrapped.
    # Loops are height data only; there is no geometric yarn added to the sofa.
    count=74
    for iy in range(count):
        for ix in range(count):
            cx=(ix+rng.uniform(.05,.95))*N/count
            cy=(iy+rng.uniform(.05,.95))*N/count
            rx=rng.uniform(3.8,6.2); ry=rng.uniform(4.2,8.1)
            theta=rng.uniform(0,2*np.pi)
            radius=14
            xx,yy=np.meshgrid(np.arange(int(cx)-radius,int(cx)+radius+1),np.arange(int(cy)-radius,int(cy)+radius+1))
            dx=xx-cx;dy=yy-cy
            u=(dx*np.cos(theta)+dy*np.sin(theta))/rx
            v=(-dx*np.sin(theta)+dy*np.cos(theta))/ry
            rr=np.sqrt(u*u+v*v)
            angle=np.arctan2(v,u)
            ring=np.exp(-((rr-(.77+.07*np.sin(angle*3+theta)))/.24)**2)
            nest=.28*np.exp(-rr*rr/1.5)
            profile=(ring+nest)*rng.uniform(.72,1.16)
            height[yy%N,xx%N]+=profile*.00013
            dye[yy%N,xx%N]+=np.exp(-rr*rr/1.7)*rng.uniform(-.014,.014)
    fuzz=noise(rng,.65)
    height+=fuzz*.000009+noise(rng,1.8)*.000013
    color=.936+dye+.0065*fuzz+.004*noise(rng,2)
    rough=.91+.018*fuzz+.012*noise(rng,2.8)
    return write_family('boucle',height,color,rough,{'label':'Bouclé','family':'fine_loop_boucle_study','seed':502,'normalScale':.9,'roughness':1.0,'sheen':.2,'sheenRoughness':.9,'description':'Lacos irregulares finos com relevo suave e penugem; distribuicao media de 1,9 mm. Estudo visual, sem codigo comercial.'})


def velvet():
    rng=np.random.default_rng(503)
    # Dense short nap, subtly directional at the fibre scale, with almost flat colour.
    fibres=noise(rng,.5,3.5)
    nap=noise(rng,7,25)
    micro=noise(rng,.55)
    height=.000009*fibres+.000002*micro+.000003*nap
    color=.938+.004*fibres+.004*nap+.002*micro
    rough=.72+.025*fibres+.017*nap
    return write_family('velvet',height,color,rough,{'label':'Veludo','family':'short_pile_velvet_study','seed':503,'normalScale':.38,'roughness':1.0,'sheen':.72,'sheenRoughness':.55,'fallback':{'normalScale':.38,'roughness':1.0,'metalness':0,'note':'Metallic-roughness continua funcional sem sheen, com menor resposta a luz rasante.'},'description':'Pelo curto denso, microfibras de baixo relevo; sheen descreve a resposta suave a luz rasante, sem brilho metalico.'})


def embedded_variants():
    """Reproduce baked areia colour and reduced maps used by the GLB exports.

    This is a display tint, not a measured fabric dye. Base colour multiplication
    deliberately follows the configurator's sRGB tint contract. Box filtering
    uses complete 2x2 texel groups, preserving the 140-mm periodic tile extent.
    Normal vectors are decoded, averaged in signed vector space and normalized
    again before 8-bit quantization; normal pixels are never gamma corrected.
    """
    family = ROOT / 'materials' / 'boucle'
    source = ROOT / 'source'
    mobile = source / 'mobile-boucle'
    mobile.mkdir(parents=True, exist_ok=True)
    neutral = np.asarray(Image.open(family/'basecolor.jpg').convert('RGB'), dtype=np.float64)
    tint = np.array([216, 201, 178], dtype=np.float64) / 255.0
    tinted = np.uint8(np.round(np.clip(neutral * tint, 0, 255)))
    color_image = Image.fromarray(tinted)
    color_image.resize((512, 512), Image.Resampling.BOX).save(source/'embedded-boucle-areia.jpg', quality=92, subsampling=0, optimize=True)
    color_image.resize((512, 512), Image.Resampling.BOX).save(mobile/'basecolor.jpg', quality=92, subsampling=0, optimize=True)

    roughness_image = Image.open(family/'roughness.jpg').convert('RGB').resize((512, 512), Image.Resampling.BOX)
    roughness_image.save(source/'embedded-boucle-roughness.jpg', quality=93, subsampling=0, optimize=True)
    roughness_image.save(mobile/'roughness.jpg', quality=93, subsampling=0, optimize=True)

    encoded = np.asarray(Image.open(family/'normal.png').convert('RGB'), dtype=np.float64)
    if encoded.shape != (1024, 1024, 3):
        raise ValueError('Expected a 1024x1024 boucle normal map for exact 2x2 downsampling')
    vectors = encoded / 255.0 * 2.0 - 1.0
    downsampled = vectors.reshape(512, 2, 512, 2, 3).mean(axis=(1, 3))
    downsampled /= np.maximum(np.linalg.norm(downsampled, axis=-1, keepdims=True), 1e-12)
    Image.fromarray(np.uint8(np.round((downsampled * 0.5 + 0.5) * 255))).save(mobile/'normal.png', optimize=True)
    for path in [source/'embedded-boucle-areia.jpg', source/'embedded-boucle-roughness.jpg', *sorted(mobile.iterdir())]:
        print(f'{path.relative_to(ROOT)}: {path.stat().st_size} bytes')


if __name__=='__main__':
    materials=[linen(),boucle(),velvet()]
    (ROOT/'materials'/'materials.json').write_text(json.dumps({'contract':'stanza-fabric-studies/v1','note':'Estudos visuais originais, nao catalogo homologado. A tela nao substitui amostra fisica.','materials':materials},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    embedded_variants()
