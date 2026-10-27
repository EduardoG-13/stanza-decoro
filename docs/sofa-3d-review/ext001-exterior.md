# EXT-001 — Sofá orgânico claro: exterior realista (revisão 2.0.0)

**Mudança de escopo.** A construção interna e a abertura em camadas foram abandonadas. A prioridade
agora é um exterior realista e refinado. Antes = `c29e2d9` (1.3.0); depois = esta revisão (2.0.0,
mudança incompatível). A `main` (`4e448e6`) não foi tocada. Todas as imagens são capturas do
visualizador real (`createSofaViewer`) feitas sobre um build `dist/` congelado. Câmera e luz são as
mesmas em cada comparação. A renderização é WebGL2 por SwiftShader em Chrome headless.

## 1. O que mudou

**Gerador** (`assets/sofa-pilot/source/build_sofa.py`, a fonte de verdade). Um único passe regenera
`sofa.blend`, `sofa.glb` e `sofa-mobile.glb`.
- `EXTERIOR_ONLY = True` passa a exportar só os grupos `upholstery`, `cushions` e `legs`. O código da
  construção interna continua no arquivo, desativado e comentado, para o histórico ficar legível.
- **Almofadas maiores e mais cheias.** Medidas de borda a borda, de 01 a 05: ≈50×50, 48×51, 47×50,
  40×43 e 41×37 cm. Antes eram ≈40×40, 38×44, 42×46, 35×40 e 33×32 cm. O perfil de enchimento passou
  de `^.55` para `^.45`, com loft de 0,082 a 0,095.
- **Empilhamento relido na foto.** 01 (oliva) fica no canto do braço e 04 contra o encosto. 02 fica à
  frente de 01, 03 (a mais alta) à frente de 02 e 04, e 05 (oliva pequena) à frente de 04, antes da
  chaise. As inclinações no plano reproduzem a leitura “em losango” da foto.
- As posições (y, z) foram resolvidas de novo com o mesmo solver de contato da rev2: cerca de 10 mm
  no assento e 8 a 12 mm no apoio. A deformação local continua sendo feita por `settle_contacts()`.
- **Encosto** elevado, com topo passando de 0,92 para 1,025 m. Na foto ele sobe claramente acima das
  almofadas. O braço baixo foi mantido.
- **Base rebaixada** (de z 0,086 para 0,052). Os pés agora são curtos, com cerca de 5 cm aparentes, e
  foram levados a ~80 % do contorno para aparecerem sob o corpo, como na foto. Os blocos ocultos de
  fixação dos pés foram removidos.
- **Materiais por região** (`stanza_region` nos extras do glTF), conforme a tabela do §2.
- **Mapas novos** em `source/generate_cushion_materials.py`: algoritmo procedural próprio, CC0,
  gravado apenas em `materials/cushions/`. São a trama de cesto oliva (basecolor sRGB + normal OpenGL
  +Y em dados lineares; 512 px no main e 256 px no mobile), a base clara cinza-bege e o avesso creme.
  A foto foi só observada (escala da trama, cores médias) e nunca amostrada. `generate_materials.py`
  não foi executado. Um mapa de roughness da trama foi descartado: custava 160 kB e não trazia ganho
  visível, então a trama usa fator constante 0,92.

**Visualizador** (`viewer/sofa-viewer.js`)
- A conversão de materiais é feita por instância (cache) e classificada pela região do material:
  primeiro os extras do GLB, depois a tabela de nomes. Nunca é feita por malha.
- Só a região `body` recebe `MeshPhysicalMaterial` com `userData.stanzaFabric=true`, e
  `embeddedFinishes` só registra materiais do corpo.
- Os materiais `decorative` viram `MeshPhysicalMaterial` fixos, com sheen próprio. Eles nunca são
  tocados por `setFinish`, inclusive na volta a bouclé-areia. Não há `material.color` aplicado à cena
  inteira.
- `setProgress` foi mantido como no-op obsoleto (valida o número e mantém a peça montada).
  `LAYER_STAGES` agora tem um único estágio montado. A câmera `layers` saiu e entrou a câmera `photo`.
- `inspect()` passou a informar `construction`, `meshes` e `materialRegions`. A nova opção
  `modelUrls:{main,mobile}` permite escolher o arquivo de cada variante.
- Foram removidos `viewer/scroll.js` e `viewer/vendor/gsap/`: só serviam à abertura.

**Site**
- `pages/explore.html`:
  - removido o fieldset “Por dentro do sofá” (controle deslizante, botões Separar/Estrutura e legenda
    de camadas);
  - textos revistos (tecido e cor valem só para o corpo);
  - nova vista “Como na foto”;
  - `data-model-id` no palco.
- `assets/sofa-experience.js`:
  - sem chamadas de progresso;
  - lê `data/models-3d.json` (injetado pelo `build.py`) e carrega só o modelo pedido (`data-model-id`
    ou `?modelo=` registrado), sob demanda.
- `home-opening.js`: só rotação decorativa (sem `cameraNarrative`). CSS sem regras de camadas. A
  descrição da página no `build.py` e o README foram revistos.
- `build.py`:
  - valida o registro;
  - copia `assets/sofa-pilot` de forma limpa (arquivos removidos não ficam no `dist`).
- Novo `data/models-3d.json`: fundação do registro de modelos.
- Novo [QUEUE.md](QUEUE.md): fila EXT-001…054 e regra de regiões.

**Metadados 2.0.0** (gerados a partir dos bytes reais). Foram atualizados `data/sofa-pilot.json`,
`contract.json` (com `MATERIAL_REGIONS` e `DEPRECATED`), `IDENTITY`/`DIMENSIONS` do módulo,
`API.md`, `manifest.json`, `CREDITS.json`, `INTEGRATION.json` (sha256 reais, `geometryChanged:true`),
`materials.json`, `LICENSE-assets.txt` e os extras de `sofa_root`. O poster foi recapturado no WebGL.
`tests/layer-stages.test.mjs` foi substituído por `tests/exterior-model.test.mjs`.

## 2. Malha → material → região

| Malha (nó GLB) | Material | Região | Personalizável |
|---|---|---|---|
| `seat_cover`, `back_cover` | `fabric_main` | corpo (`body`) | sim (tecido + cor) |
| `seat_panel_seam` | `fabric_seam` | corpo (`body`) | sim |
| `cushion_01_cover`, `cushion_05_cover` (frente + faixa da borda) | `cushion_olive_weave` | decoração fixa | não |
| `cushion_01_cover`, `cushion_05_cover` (face traseira) | `cushion_olive_reverse` | decoração fixa | não |
| `cushion_01_welt`, `cushion_05_welt` | `cushion_olive_seam` | decoração fixa | não |
| `cushion_02/03/04_cover` | `cushion_light_boucle` | decoração fixa | não |
| `cushion_02/03/04_welt` | `cushion_light_seam` | decoração fixa | não |
| `foot_1…4` | `legs_dark` | estrutura externa aparente | não |

As almofadas claras e o avesso **reutilizam a mesma imagem** de normal e roughness do bouclé do
corpo. Não há bytes duplicados: são 7 imagens por GLB.

## 3. Componentes removidos dos GLBs

- Grupos `padding`, `frame` e `suspension`.
- Objetos `seat_foam`, `back_foam`, `seat_batting`, `back_batting`, `perimeter_support`,
  `front_rail`, `rear_rail`, `side_rail_0/1`, `cross_support_0/1`, `rear_support`,
  `suspension_band_0…9` e `foot_mount_1…4`.
- Materiais `padding_illustrative`, `batting_illustrative`, `frame_illustrative` e
  `suspension_illustrative`.

Isso é confirmado pelo teste `GLBs are exterior-only` e pelo `inspect().meshes` no navegador:
19 malhas, nenhuma interna.

## 4. Medições

| | antes 1.3.0 main | **2.0.0 main** | antes 1.3.0 mobile | **2.0.0 mobile** | alvo |
|---|---|---|---|---|---|
| triângulos | 49 064 | **36 176** | 24 280 | **15 872** | 60k / 25k |
| bytes GLB | 4 132 752 | **4 037 196** | 1 794 808 | **1 560 496** | — |
| bytes iniciais (GLB + poster + módulos) | 5 082 685 | **4 988 005** | 2 744 737 | **2 511 301** | 5 MB |
| limites L × A × P (m) | 2,487 × 0,993 × 1,084 | **2,487 × 1,106 × 1,084** | — | 2,486 × 1,106 × 1,084 | — |

- A altura passou de 0,993 para 1,106 m por causa do topo da almofada 03 (o encosto fica em 1,026 m).
- O main voltou a ficar abaixo de 5 MB iniciais. Na 1.3.0 ficava 1,7 % acima.
- O maior mapa continua sendo a normal de bouclé de 1024 px, compartilhada.
- sha256 `sofa.glb` = `02fdb59ec8a52467a10840642546baa669127d28ed79251bd4d644997938d580`
- sha256 `sofa-mobile.glb` = `57d6a53a098e9ce91fa35ddaaaa9d6fc4f5f33de159bc4e8583713d36972c16e`

**Ajuste das almofadas.** Os números estão em
[`validation/ext001/cushion-fit-main.json`](validation/ext001/cushion-fit-main.json) e
[`-mobile`](validation/ext001/cushion-fit-mobile.json). O método é a distância assinada contra cascas
externas únicas, o mesmo da rev2.
- Penetração máxima no assento: 1,1 a 1,7 mm.
- Penetração no encosto/braço: no máximo 1,6 mm (compressão permitida de 1,2 mm).
- Pares 01-02, 02-03 e 04-05: 1,0 a 1,8 mm, com área de contato de 56 a 143 cm².
- Nenhum vivo dentro de uma almofada vizinha.
- 03 e 05 apoiam-se nas vizinhas e não tocam o encosto, como na foto.

## 5. Validação

- `npm test`: **22/22** (9 novos testes do modelo exterior em `tests/exterior-model.test.mjs`, que substituem os 6 de camadas, mais 13 de orçamento; antes: 19).
- `build.py --ignore-local-config --production --no-source-entries`: OK, 26 páginas.
- `check_site.py --production`: OK (sha256 do `INTEGRATION.json` confere).
- glTF-Validator 2.0.0-dev.3.10: **0 erros, 0 avisos, 4 infos** (`UNUSED_OBJECT`, TEXCOORD dos pés)
  nos dois GLBs: [`validation/ext001/`](validation/ext001/).

Comportamento no build congelado, nas duas variantes
([`behaviour.json`](validation/ext001/behaviour.json),
[`colour-fixity.json`](validation/ext001/colour-fixity.json)):
- **Almofadas fixas.** No ângulo da foto, com máscaras por almofada, a diferença média de pixel
  contra o inicial é ≤ 0,003 (p99 = 0) em oliva, terracota, grafite, linen-oliva e velvet-terracota.
  Já a imagem inteira muda 14 a 28 níveis em média.
- **Retorno a bouclé-areia:** idêntico pixel a pixel ao estado inicial (diferença máxima 0).
- **`inspect().materialRegions`:** 5 materiais `decorative` com `stanzaFabric=false`, `fabric_main`
  e `fabric_seam` `body` com `stanzaFabric=true`, `legs_dark` `exterior-structure`. As
  cores/mapas decorativos ficam idênticos antes e depois das trocas.
- **Troca rápida (6 eventos de rádio):** a última vence (Bouclé · Terracota), e o link de orçamento
  sai com `tecido=boucle&cor=terracota`. Pela API, três `setFinish` simultâneos terminam em
  boucle-grafite.
- **Falha de textura:** a normal do linen foi abortada uma vez. Aparece a mensagem de erro, a seleção
  anterior é mantida, e a nova tentativa funciona (Trama plana · Areia).
- **Resize:** canvas de 800×500 para 600×420.
- **Dispose:** idempotente; o canvas é removido e o poster restaurado. Depois do dispose, `setFinish`
  rejeita e `setView` lança erro.
- **`setProgress(.2…1)`:** grupos e câmera inalterados; `NaN` gera `TypeError`.
- **Home:**
  - rotação em ~20 renders/s (≤ 30 fps);
  - `offscreen` com 0 renders/s ao rolar para fora, e volta a `running`;
  - `prefers-reduced-motion` mantém o poster, sem GLB baixado;
  - a página de produto não baixa GLB antes do clique e depois baixa só a variante certa.
- **Console: 0 erros**, exceto o `net::ERR_FAILED` do mapa abortado de propósito no teste de falha.

## 6. Avaliação visual honesta e limitações

- **Tamanho e encaixe das almofadas.** Agora elas leem como na foto: grandes, cheias e alternadas em
  profundidade, com o topo da 03 passando o encosto. Não atravessam nada e o contato é suave.
- **Vivos.** Ficam visíveis, mas finos: são um tubo de 1,5 mm. Nas claras quase desaparecem a
  distância.
- **Composição.** É próxima, mas não idêntica. Na foto, as claras 02 e 03 têm cantos mais pontudos e
  em “losango” mais marcado, e a 04 aparece mais à direita entre 03 e 05. Aqui a 04 fica parcialmente
  escondida atrás de 03 e 05.
- **Cores fixas.** Comprovadas por pixel. A trama oliva é original e mais contrastada (o creme
  aparece mais) do que a trama real. O avesso creme só aparece em vistas laterais e traseiras.
- **Corpo.**
  - Areia é mais quente/bege que o cinza claro da foto. Isso foi mantido de propósito: é a cor de
    estudo do contrato.
  - A trama de bouclé é sutil a distância (o corpo lê quase liso), como antes.
  - O encosto ficou mais alto, mas a espessura e o volume superior ainda são um pouco menores que na
    foto.
- **Referência.** Há um único ângulo: costas, lado oposto e parte de baixo são inferidos. Medidas
  estimadas.
- **Ambiente de teste.** SwiftShader headless; não houve teste em GPU real, Safari, Firefox ou celular
  físico.
- **Versão do Blender.** `bpy` 5.0.1 em vez do Blender 5.2. Builds repetidos diferem só por ruído de
  ULP nas tangentes exportadas dos pés: o JSON é idêntico e a diferença máxima é 6e-8.

## 7. Índice de imagens (`images/`, prefixo `ext001_`)

| Imagem | Mostra |
|---|---|
| [ext001_photo_angle_vs_reference.jpg](images/ext001_photo_angle_vs_reference.jpg) | SOFA-2.jpg × depois (main, mobile) × antes, no ângulo da foto |
| [ext001_body_colours_cushions_fixed_main.jpg](images/ext001_body_colours_cushions_fixed_main.jpg) | main: bouclé areia/oliva/terracota/grafite, linen-oliva, velvet-terracota e retorno; almofadas fixas |
| [ext001_body_colours_cushions_fixed_mobile.jpg](images/ext001_body_colours_cushions_fixed_mobile.jpg) | o mesmo no mobile |
| [ext001_views_before_after_main.jpg](images/ext001_views_before_after_main.jpg) | frente, três quartos esquerda/direita, lateral: depois × antes |
| [ext001_views_before_after_mobile.jpg](images/ext001_views_before_after_mobile.jpg) | mobile: frente, três quartos, close: depois × antes |
| [ext001_cushion_contacts_main.jpg](images/ext001_cushion_contacts_main.jpg) | closes de pares, encosto/braço e assento em corpo claro (areia) e escuro (grafite) |
| [ext001_cushion_contacts_mobile.jpg](images/ext001_cushion_contacts_mobile.jpg) | closes no mobile, claro e escuro |
| [ext001_diagnostic_layout.jpg](images/ext001_diagnostic_layout.jpg) | DIAGNÓSTICO (cores por almofada, não é render de aceitação): disposição de topo e no ângulo da foto, depois × antes |
| [ext001_behaviour_contexts.jpg](images/ext001_behaviour_contexts.jpg) | página de produto (inicial, falha → nova tentativa, troca rápida em main e mobile) e home (dois quadros da rotação) |
