# FEAT-006 — Exportação final, metadados, enquadramento e validação

> **SUPERADO pela revisão 2.0.0 (EXT-001).** Medidas, hashes e o contrato de camadas descritos aqui valem para a 1.2.0. Ver [ext001-exterior.md](ext001-exterior.md).

Fechamento coerente do ativo na revisão **1.2.0**: medições vs alvos, metadados/contratos
sincronizados, hashes reais, enquadramento conferido nos dois consumidores e validação completa.

![Enquadramento nos dois consumidores (desktop)](images/final_framing_consumers.png)

![Enquadramento nos dois consumidores (mobile)](images/final_framing_consumers_mobile.png)

## Medições vs alvos — CONFIRMADO (sem sacrificar silhueta para bater número)

| Métrica | sofa.glb (main) | sofa-mobile.glb | Alvo | Desvio |
|---|---|---|---|---|
| Triângulos | **49 064** | **24 280** | 60 000 / 25 000 | OK (mobile perto do teto após FEAT-003) |
| Bytes | **4 132 288** | **1 784 072** | — | +161 KB / +97 KB vs 1.1.0 |
| Bytes iniciais (est.) | ~5,09 MB | ~2,74 MB | 5 MB inicial | main ~1,7% acima |
| Bounds (L×A×P) | 2.48669 × 1.04243 × 1.08427 | 2.4864 × 1.04243 × 1.08398 | — | inalterado vs 1.1.0 |
| Texturas | normal 1024 + areia 512 + roughness 512 | normal 512 + base 512 + rough 512 | ≤2048 | OK |

**Desvio reportado honestamente:** `mainInitialBytes` ~5,09 MB passa ~1,7% do alvo de 5 MB por
causa da geometria interna nova (espuma/manta/percintas/trilhos). **Não** foi reduzido cortando a
silhueta nem removendo as camadas internas (instrução explícita de não sacrificar a silhueta para
bater número). Mobile segue bem abaixo de 5 MB. Triângulos dentro dos alvos.

## Metadados, contratos e proveniência — CONFIRMADO

- **Revisão 1.2.0** coerente em: `data/sofa-pilot.json`, `viewer/contract.json` (IDENTITY +
  DIMENSIONS height corrigida para 1.042), `viewer/sofa-viewer.js` IDENTITY, `manifest.json`,
  `CREDITS.json`, `INTEGRATION.json` (`upstreamRevision`), o `extras.revision` do nó `sofa_root`
  dentro do GLB, e as prévias/`defaultSelection`/`orcamento.html` (sofa-options). `modelId`
  permanece `stanza-organic-01`. Diferenciada da upstream 1.0.0; proveniência preservada.
- **INTEGRATION.json**: `modelSha256` regenerados dos bytes REAIS
  (`d378…`/`87b3…`), `geometryChanged:true`. `check_site.py --production` passa porque os arquivos
  realmente batem (magic glTF, version 2, tamanho declarado == real), não por troca de hash.
- **manifest.json**: dimensões/bounds/bytes/triângulos/texturas reais; `groups[].subGroups` e
  `materialBindings` documentam espuma/manta como NOVOS (introducedIn 1.2.0); `layerSequence.stages`
  = contract = módulo; `performance` com `geometryActual` + `deviationNote`; `dependencies.blender`
  anota o uso do `bpy` 5.0.1 na regeneração (ressalva disclosed).
- **CREDITS.json**: `revision120Changes` descreve as mudanças internas e a proveniência (nenhuma
  referência externa redistribuída; foto consultada ≠ textura licenciada).
- **viewer/API.md**: exemplo de `getSelection()` atualizado para `revision:"1.2.0"`; contrato de
  `setProgress` descreve a nova ordem (manta/espuma/percintas).
- **previews/poster.jpg**: regenerado a partir de uma captura WebGL real do GLB 1.2.0 (bouclé-areia,
  três quartos, p0), coerente com a nova base (trilho de madeira visível). Sem fotografia de terceiro.
- **materials/validation.json / mapas**: nenhum mapa mudou → não regenerado; proveniência CC0 mantida.

## Enquadramento nos dois consumidores — CONFIRMADO (desktop + mobile)

Dirigido pelos adaptadores reais do site:

- **Configurador** (`sofa-experience.js`, página explorar): botão "Explorar em 3D" cria o viewer;
  sofá totalmente enquadrado no painel, sem corte nem zoom excessivo (desktop 1280×900 e mobile
  390×780). 0 erros de console.
- **Home/hero** (`home-opening.js`): `scene=ready/running`; sofá enquadrado no painel do hero com
  rotação ambiente (desktop e mobile). 0 erros de console.

Como os bounds não mudaram (altura 1.04243, largura 2.48669), nenhuma câmera precisou mudar; as
CAMERAS seguem idênticas em módulo/contract/manifest.

## Validação completa (fresca, tudo verde)

- **Khronos glTF-Validator 2.0.0-dev.3.10**: `sofa.glb` e `sofa-mobile.glb` = **0 erros, 0 warnings,
  56 infos, 0 hints**. Relatórios frescos salvos em
  [`validation/gltf-validation-sofa.json`](validation/gltf-validation-sofa.json) e
  [`validation/gltf-validation-sofa-mobile.json`](validation/gltf-validation-sofa-mobile.json). Os 56
  infos são `UNUSED_OBJECT (TEXCOORD_0)` / `UNUSED_MESH_TANGENT` benignos nas malhas ilustrativas sem
  textura (mais que os 38 da 1.1.0 por causa das novas malhas de espuma/manta/percintas/trilhos).
- `npm test`: **19/19** (13 originais + 6 de comportamento 3D em `tests/layer-stages.test.mjs`).
- `build.py --ignore-local-config --production` + `check_site.py --production`: **OK**.
- **Visualizador WebGL real** (Chrome for Testing / SwiftShader) dirigido pela API pública: GLB final
  aberto nos dois variantes, `getSelection` retorna `revision:'1.2.0'`, abertura em camadas e 12
  combinações sem erro de console. Capturas `after_feat003_*`, `fit_feat004_*`, `combo_*`,
  `final_cfg_*`, `final_home_*`.

## Testes de comportamento 3D adicionados (não substituem inspeção visual)

`tests/layer-stages.test.mjs` afirma a consistência `LAYER_STAGES (módulo) == contract.json ==
manifest.layerSequence.stages`, o contrato 0/1 montadas-idênticas, a ordem .5/.7 e a **não-deriva**
de `setProgress` (p0==p1==base após um ciclo). O próprio arquivo declara que esses testes verificam
invariantes estruturais/numéricos e **não** substituem a inspeção visual no visualizador real.

## Entrega

Tudo commitado na branch `work/sofa-3d-inspection`. **A `main` não foi tocada; nada foi mesclado nem
publicado no site oficial.** A abertura/atualização do PR é responsabilidade do orquestrador.
