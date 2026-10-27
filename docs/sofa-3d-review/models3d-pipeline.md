# Pipeline models3d — modelos 3D exteriores da coleção Stanza

Infraestrutura mínima e incremental para produzir a fila ([QUEUE.md](QUEUE.md)) modelo a modelo,
sem migrar o site (HTML/CSS/JS estático + `scripts/build.py`) e sem dependências pagas.
EXT-001 (`stanza-organic-01`) mantém sua fonte própria em `assets/sofa-pilot/`; EXT-002
(`stanza-straight-01`) é o primeiro modelo do pipeline.

## Estrutura

```
assets/models-3d/
  lib/stanza3d.py                 biblioteca Blender compartilhada (bpy)
  materials/                      biblioteca de acabamentos compartilhada (CC0, procedural)
    generate_materials.py         gera as famílias abaixo + materials.json
    boucle-mescla/                basecolor/normal/roughness 1024 neutros + embedded/ (tintas, 512/256)
    wood-wenge/                   madeira escura para plintos/pés
    sarja/                        sarja 2/2 fosca (EXT-003, EXT-005)
    linho-rustico/                tela simples com flamê (EXT-004)
    decor-losango/, decor-quadrados/  desenhos procedurais das almofadas decorativas (fixas)
  <modelId>/
    source/build.py               fonte paramétrica (verdade); gera GLBs + .blend num passe
    source/<modelId>.blend        derivado (não editar à mão)
    source/metrics.json           triângulos por objeto, posições resolvidas, métricas dos GLBs
    models/<modelId>.glb          principal (≤ 60k tri, ≤ 5 MB)
    models/<modelId>-mobile.glb   móvel (≤ 25k tri)
    previews/poster.jpg           1200×900, render do visualizador real
    manifest.json                 identidade, relação catálogo/portfólio, regiões, opções, medidas, sha256, limitações
scripts/models3d/                 captura, métricas, validação, contatos, composições, comportamento
data/models-3d.json               registro (lido pelo configurador e validado no build)
```

Famílias já existentes (`boucle`, `linen`, `velvet`) continuam em `assets/sofa-pilot/materials/` e
são reutilizadas **por referência** (`materialLibrary` do registro), sem cópia. O build publica de
`assets/models-3d/` só GLBs, posters, manifestos e mapas (fontes, `.blend` e `.py` ficam no repositório).

## Convenções

- Metros; Blender X largura, −Y frente, Z para cima (glTF: Y para cima, +Z frente). Origem no piso, centro da peça.
- Raiz `model_root` com extras `modelId`, `revision`, `construction:"exterior-only"`, `materialRegions`, `embeddedFinish`.
- Grupos `upholstery` (corpo), `cushions` (decorativas), `legs` (estrutura aparente).
- Regiões por material (`stanza_region`): `body`, `decorative`, `contrast`, `exterior-structure` (regra em [QUEUE.md](QUEUE.md)). Só `body` muda no configurador; nomes estáveis `fabric_main`/`fabric_seam`.
- UV do corpo: 1 unidade = 0,30 m (`BODY_UV_METERS`); cada família declara `repeatMeters` e o visualizador ajusta `texture.repeat`.
- Acabamento inicial embutido = `options.default` (mapa pré-tingido × multiplicador branco; tinta = valor de `COLORS`, sem tingimento duplo).
- IDs de tecido/cor só são **acrescentados** (`COLORS`/`FABRICS` em `sofa-viewer.js` + `contract.json` + rótulos em `data/sofa-pilot.json`), nunca renomeados.
- Somente exterior: nada de armação, espuma, percintas ou manta.

## Biblioteca `stanza3d.py`

| Peça | Uso |
|---|---|
| `RoundedBox(center,size,radius,mid,edge,crown,wrinkle)` | estofados retos: braços, base, painéis, almofadas caixa; `.seam_loop(face)` dá o vivo na linha de 45° da aresta; `.collider()` |
| `pillow_shape(...)` / `LooseCushion` | almofada de borda faca (porte do EXT-001) com `edge_round` para encostos; `solve()` posiciona por `solve_rest()` (marcha até o contato com sobreposição alvo), `settle()` aplica `settle_contacts()` (compressão local suave + vivo acima do contato) |
| `oriented_box(name,size,radius,pos,rot,…,welts)` / `rest_rigid(holder,ob,colliders,dir,overlap)` | almofada caixa inclinada no próprio referencial com vivos (`seam_loop`) por face; assentamento rígido por bisseção (desce/recua até a sobreposição alvo). `RoundedBox.collider()` agora aplica `matrix_world` (idêntico para malhas sem transformação) |
| `block`, `plinth` | blocos chanfrados, plinto (faixa + pés-bloco) com veio da madeira no eixo certo |
| `material`, `textured`, `library_maps` | materiais com `stanza_region`; mapas da biblioteca nos tamanhos pedidos (rugosidade pequena: o exportador a regrava em PNG) |
| `export_variant`, `glb_metrics`, `triangle_count` | GLB (+ `.blend` na principal) e métricas |

## Visualizador

Um único módulo: `assets/sofa-pilot/viewer/sofa-viewer.js` (API em [`viewer/API.md`](../../assets/sofa-pilot/viewer/API.md)).
`createSofaViewer(el, { model, materialUrls, modelUrls, baseUrl })` carrega qualquer modelo
registrado; sem `model` o comportamento da EXT-001 é idêntico (regressão: 0 px de diferença). Câmeras
dos novos modelos vêm de `framedCameras(bounds)` + `cameras` do registro (ex.: `photo` ajustada à foto).

## Registro e site

- `data/models-3d.json` (v2): `materialLibrary`, `verifiedStatuses` e, por modelo, `modelId`,
  `catalogId`, `portfolioId`, `queue`, `title`, `revision`, `status`, `reference`, `page`,
  `productPage`, `posterAlt`, `assets`, `materialRegions`, `options{fabrics,colors,default,embedded}`, `cameras`.
- `scripts/build.py` valida tudo (IDs, arquivos, sha256/bytes/revisão contra o manifesto, regiões,
  opções, mapas) e só gera o link **"Ver em 3D"** na página `modelos/<catalogId>.html` de modelos
  verificados. `scripts/check_site.py` confere GLB (magic, versão, tamanho, sha256), poster, mapas,
  ausência de fontes publicadas e que a home não referencia a coleção.
- Configurador: `/explorar-sofa.html?modelo=<modelId>` troca poster, título, opções e orçamento
  (`referencia=<catalogId>`) e carrega **só** o GLB desse modelo após o clique. Modelo desconhecido →
  sem 3D e sem outra peça (mensagem + catálogo). Home inalterada (só o sofá orgânico, móvel).
- Orçamento: `data/sofa-pilot.json` `studies` (modelId → catalogId) habilita `estudo/tecido/cor` no formulário e no redirecionamento seguro.

## Scripts (`scripts/models3d/`)

Ambiente gratuito: Blender 5.0.1 como módulo Python (`pip install bpy==5.0.1`, com libs GL no
`LD_LIBRARY_PATH`), Pillow + numpy, Node 22, `playwright-core` e Chrome for Testing headless
(`CHROME_PATH`; padrão do sandbox), `gltf-validator` (`npm i --no-save gltf-validator playwright-core@1.56`
ou `PLAYWRIGHT_CORE`/`GLTF_VALIDATOR` com caminho absoluto). WebGL roda em SwiftShader sem GPU.

| Script | Função |
|---|---|
| `capture.mjs <cfg.json>` | capturas pelo visualizador real servindo `dist/` via `page.route`: presets ou câmeras explícitas, acabamentos em sequência, máscaras de região |
| `mask_check.py <dir> <run> <view> <ref> <passes…>` | diferença de pixels por região (decorativas/contraste/estrutura devem ficar em 0; vivos finos: usar um close-up, a erosão de 2 px apaga linhas de 2 px) |
| `behaviour.mjs <modelId> <out>` | 73 verificações de comportamento (configurador, API, páginas, home) para o modelo + regressão do padrão |
| `contacts.py <glb> <out.json> [A:B…]` | penetração/folga assinada entre malhas (bpy) |
| `validate_gltf.mjs <modelId> <out>` | glTF-Validator nos dois GLBs |
| `glbtools.py <glb…>` / `update_manifest.py <dir>` | métricas puras em Python; atualiza a parte calculada do manifesto |
| `composite.py <spec.json>` | painéis rotulados (com sobreposição foto × render) |

## Como adicionar o próximo modelo

1. Ler a foto; achar o item em `data/catalog.json`/`data/portfolio.json` (não duplicar); classificar regiões.
2. Copiar `assets/models-3d/stanza-straight-01/source/build.py` para `assets/models-3d/<novoId>/source/build.py`, trocar identidade/regiões/componentes; se a foto pedir um tecido novo, acrescentar uma família em `materials/generate_materials.py` (e o ID em `FABRICS`/`COLORS` + `contract.json` + `data/sofa-pilot.json`).
3. `LD_LIBRARY_PATH=… .agents/venv/bin/python assets/models-3d/<novoId>/source/build.py`; criar `manifest.json` (campos autorais) e `python3 scripts/models3d/update_manifest.py assets/models-3d/<novoId>`.
4. Acrescentar a entrada no registro (com `studies` em `data/sofa-pilot.json`) e os `input` das opções novas em `pages/explore.html` (ocultos).
5. Build + `capture.mjs` (ângulo da foto ajustado), comparar com a foto, iterar; congelar; poster.
6. `npm test`, `check_site.py`, `validate_gltf.mjs`, `contacts.py`, `mask_check.py`, `behaviour.mjs`; relatório `extNNN-*.md`, imagens `images/extNNN_*.jpg`, atualizar a fila.
