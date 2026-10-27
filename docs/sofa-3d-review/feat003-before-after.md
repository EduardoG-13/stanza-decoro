# FEAT-003 — Interior por componentes: manta ≠ espuma, percintas tensionadas, armação e pés

> **SUPERADO (mudança de escopo, EXT-001 / revisão 2.0.0).** A construção interna (manta, espuma, percintas, armação) foi abandonada e não está mais nos GLBs. Mantido apenas como histórico; ver [ext001-exterior.md](ext001-exterior.md).

Edições **paramétricas** em `assets/sofa-pilot/source/build_sofa.py`, reexportadas para os dois GLBs
e o `source/sofa.blend` num único passe do gerador (bpy 5.0.1). Sem cirurgia de GLB. Revisão
`1.1.0 → 1.2.0`.

![Percintas tensionadas e armação (close, p.7)](images/structure_webbing_frame_closeup_main.png)

![Estrutura antes/depois (camadas em p.7)](images/structure_before_after_layers_main.png)

## O que mudou

### 1. Espuma com volume próprio (não mais a casca do revestimento reescalada) — CONFIRMADO
Antes, `seat_padding`/`back_padding` chamavam `seat(...,foam=True)`/`back(...,foam=True)`: a **mesma
casca** do revestimento, apenas reescalada (A.11.3). Agora o **núcleo de espuma** (`seat_foam`,
`back_foam`, material `padding_illustrative`) tem perfil próprio: mais baixo e de coroa mais plana
(`profile` do assento recomposto com fator 0.93 e altura 0.168+Δ·0.58; encosto com `thick*0.70`,
`hh*0.80`). É um bloco de espuma firme embutido, não a superfície externa encolhida.

### 2. Manta (batting) distinta da espuma — CONFIRMADO (camada nova)
Novos objetos `seat_batting`/`back_batting`, **material novo `batting_illustrative`** (mais claro,
quase-branco morno, rugosidade 0.99 — visualmente distinto da espuma). A manta é uma casca **fina**,
um pouco maior e mais alta que a espuma (0.945 vs 0.93 no assento; `thick*0.80` vs `0.70` no
encosto), mas ainda **dentro** do revestimento. Ela envolve o núcleo e arredonda as bordas — não é
uma segunda casca grossa. Fundamentação conceitual (Sailrite "Anatomy of a Cushion" / "Gluing
Batting to Foam", já lidas em INSPECTION I.8): a manta de poliéster sobre a espuma dá o aspecto
"plump", arredonda bordas e preenche o vão até a capa.

Medições no `.blend` regenerado (Z-up, Blender):

| Objeto | faixa Z | papel |
|---|---|---|
| `seat_foam` | [0.168, 0.403] | núcleo firme, mais baixo |
| `seat_batting` | [0.172, 0.416] | manta, levemente maior/mais alta, externa à espuma |
| `back_foam` | [0.348, 0.861] | núcleo do encosto |
| `back_batting` | [0.340, 0.877] | manta do encosto, externa à espuma |

A manta é sempre externa à espuma e interna ao revestimento → lê como camada fina de loft, não como
cópia grossa. (LIMITAÇÃO: medido sob bpy 5.0.1; coerente com o GLB exportado.)

### 3. Percintas (webbing) como faixas individuais tensionadas — CONFIRMADO
As 8 placas planas paralelas `suspension_band_0..7` (box `(.055,.61,.004)` em z=.24) foram
substituídas por **faixas individuais** geradas por um novo `strap(a,b,...)`: banda fina com leve
**catenária** no vão (webbing sob carga cede um pouco) e pequena saliência quando passa **por cima**
de uma faixa perpendicular. São ancoradas aos trilhos de madeira (front/rear), não flutuam.

**Decisão de disposição (fundamentada, sem impor cruzamento como regra universal):**
As fontes consultadas (Simplicity Sofas, em CREDITS/INSPECTION I.8) descrevem o cruzamento
(criss-crossing) como **um sinal de qualidade** — "tiras mais grossas, mais fios se cruzando e
firmemente presas ao frame" — **não** como obrigação. Escolhi, portanto, uma disposição **justificada
pela própria armação**: sete faixas **frente→fundo** (o vão principal que o corpo carrega, entre os
trilhos dianteiro e traseiro) e **interlace parcial** de apenas três faixas laterais, atravessando
somente os **três vãos centrais mais largos** — onde o entrelaçamento agrega suporte real. Os vãos
externos/curtos ficam em sentido único, como um estofador faria (não se desperdiça percinta onde o
vão é curto). Assim o cruzamento aparece onde é útil e é **omitido** onde não se justifica: isso é
uma decisão de projeto ancorada nas referências e na peça, não a aplicação de uma regra universal.
Total: 10 faixas (`suspension_band_0..9`), todas dentro do grupo público `suspension`.

### 4. Armação seguindo o contorno e sustentando — CONFIRMADO
Trilho de perímetro de madeira (`perimeter_support`) seguindo ~86% da silhueta (fator `FR_S`), mais
`front_rail`/`rear_rail` (os trilhos entre os quais as percintas tensionam), `side_rail_0/1` e dois
`cross_support_0/1` sob o vão mais largo (ideia de corner-block), e o `rear_support` do encosto.
Nenhuma barra fica sem função quando exposta. Fundamentação: Simplicity Sofas (quadro de madeira
maciça "corner-blocked, doweled, stapled and glued") e Beaumont & Fletcher (frame "screwed, glued
and dowelled"; **os pés fazem parte do frame**).

### 5. Pés apoiados no piso e ligados à base — CONFIRMADO
`foot_1..4` repousam no piso: faixa Z medida **[0.0000, 0.1500]** (base em z=0). Um
`foot_mount_1..4` curto liga o topo do pé ao trilho (≈0.147), de modo que o pé lê como **preso** à
armação (Beaumont & Fletcher), não flutuando sob ela. Acabamento próprio `legs_dark` preservado.

## Grupos públicos preservados e mapeamento documentado — CONFIRMADO

Os 6 grupos públicos `upholstery/padding/frame/legs/cushions/suspension` seguem intactos. As novas
sub-camadas vivem **dentro** de `padding` e estão documentadas em `manifest.json`
(`groups[].subGroups` e `materialBindings`) e em `CREDITS.json` (`revision120Changes`), deixando
claro que os nomes `seat_foam/back_foam/seat_batting/back_batting/batting_illustrative` **são novos**
desta revisão 1.2.0 (não se apresenta como pré-existente). Materiais ilustrativos
(padding/batting/frame/legs/suspension) **não** recebem `userData.stanzaFabric` → não são tingíveis.

Hierarquia exportada (do GLB regenerado):

```
padding    -> seat_foam, seat_batting, back_foam, back_batting
suspension -> suspension_band_0..9 (7 frente→fundo + 3 laterais centrais)
frame      -> perimeter_support, front_rail, rear_rail, side_rail_0/1, cross_support_0/1, rear_support
legs       -> foot_1..4, foot_mount_1..4
upholstery -> seat_cover, back_cover, seat_panel_seam
cushions   -> cushion_01..05 (cada um _cover + _welt)
```

## Métricas (GLB regenerado)

| Métrica | Antes (1.1.0) | Depois FEAT-003 (1.2.0) | Alvo |
|---|---|---|---|
| Triângulos main | 43 936 | **49 064** | ≤ 60 000 |
| Triângulos mobile | 21 128 | **24 280** | ≤ 25 000 |
| Bytes main | 3 970 924 | **4 132 288** | — |
| Bytes mobile | 1 686 664 | **1 784 072** | — |
| Altura (bounds Y) | 1.04243 m | **1.04243 m** | silhueta preservada |
| Largura × profundidade | 2.48669 × 1.08427 | **2.48669 × 1.08427** | inalterada |

Silhueta externa preservada (bounds idênticos); o acréscimo de triângulos vem das camadas internas
novas, dentro dos alvos.

## Validação (tudo verde nesta rodada)

- Khronos glTF-Validator 2.0.0-dev.3.10: `sofa.glb` e `sofa-mobile.glb` = **0 erros, 0 warnings, 56
  infos**. Os infos (mais que os 38 antigos) são `UNUSED_OBJECT (TEXCOORD_0)` / `UNUSED_MESH_TANGENT`
  nas malhas ilustrativas sem textura recém-adicionadas (espuma/manta/percintas/trilhos/mounts).
- `npm test`: 13/13.
- `build.py --ignore-local-config --production --no-source-entries` + `check_site.py --production`:
  OK — o `check_site` confirma que os sha256 em `INTEGRATION.json` batem com os bytes reais.
- Visualizador WebGL real (ambos os variantes): `createSofaViewer` OK, `getSelection` retorna
  `revision:'1.2.0'`, 0 erros de console. Capturas `after_feat003_*`.

## Contratos preservados

API pública do viewer, formato da seleção, semântica de `setProgress`, consistência
LAYER_STAGES/contract/manifest (as camadas em si são reautoradas no FEAT-004), os 6 grupos públicos,
metros/eixos/origem, IDs de tecido/cor, e o contrato de orçamento. Revisão `1.2.0` propagada em
`data/sofa-pilot.json`, `viewer/contract.json`, `viewer/sofa-viewer.js` IDENTITY, `manifest.json`,
`CREDITS.json`, `INTEGRATION.json` e no `extras.revision` do nó `sofa_root` do próprio GLB.
