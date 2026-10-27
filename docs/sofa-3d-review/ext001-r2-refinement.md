# EXT-001 r2 — refino de fidelidade à foto (revisão 2.1.0)

**Antes** = `d582518` (2.0.0). **Depois** = esta revisão (2.1.0, compatível na API). A `main`
(`4e448e6`) não foi tocada. Todas as imagens vêm do visualizador real (`createSofaViewer`).
- O "depois" foi capturado sobre um build `dist/` congelado.
- O "antes" foi capturado sobre a árvore de `d582518`.
- Em cada comparação, câmera e luz são as mesmas.
- O render é WebGL2 por SwiftShader em Chrome headless.

Os cinco pontos que a comparação com `sofas/SOFA-2.jpg` apontou foram tratados na fonte
(`source/build_sofa.py`, `source/generate_cushion_materials.py` e o novo
`source/generate_embedded_areia.py`). `sofa.blend`, `sofa.glb` e `sofa-mobile.glb` foram regenerados
num único passe.

## 1. O que mudou

**Encosto (ponto 1).** Na foto o encosto é uma placa alta e espessa, com frente plana e topo
arredondado.
- O topo subiu de 1,025 m para **1,13 m**, e a altura cheia se mantém de x −0,76 a 0,48.
- A meia espessura passou de 0,122 m para **0,135 m**.
- A seção agora é um retângulo com topo boleado (`slab_section()`, raio de ~85 % da meia espessura,
  com reamostragem por comprimento de arco). Antes era um "squircle", que lia fino e pontudo.
- O braço esquerdo baixo foi mantido (0,645 → 0,685 m), assim como o fim arredondado antes da chaise,
  que passou de x 0,62 para 0,70.
- O pé do braço fica 16 % mais fino, para não expor a face inferior sobre o rolo do assento.
- As UVs do encosto seguem a distância real na superfície. As tampas das pontas usam projeção
  plana, e a costura UV do laço fica na face de baixo, escondida. Na 2.0.0 apareciam estrias de
  textura na ponta do braço.
- Onde o vivo do assento passava rente ao braço mais grosso, ele foi recolhido 5 mm para dentro do
  braço. Antes ele "furava" a superfície em pontos.

**Almofadas (ponto 2)** (`pillow_shape()`).
- **Enchimento cheio e abaulado:** `0,45·f^0,35 + 0,55·f^0,85`, com loft de 0,10 a 0,135 m (antes
  0,082 a 0,095).
- **Bordas côncavas e cantos pontudos:** a costura é puxada para dentro entre os cantos (−7,5 %). Na
  2.0.0 ela era empurrada para fora, o que dava um quadrado arredondado.
- **"Orelhas" finas:** o enchimento cai 35 % perto de cada canto.
- **Rugas suaves:** dobras radiais rasas (≤ 4 mm) a partir dos cantos.
- **Malha:** 22×22 por face no main (antes 20) e 14×14 no mobile (antes 12).
- **Composição relida na foto:**
  - todas em leque (giro de 22 a 35° no plano);
  - 01 oliva grande no canto do braço;
  - 02, 03 (a mais alta) e 04 claras;
  - 05 oliva menor, mais à direita;
  - a 04 agora aparece entre 03 e 05.
- **Ajuste:** as posições (y, z) foram resolvidas de novo pelo mesmo solver de contato da rev2,
  com assento a 10 mm, apoio a 12 mm e vizinhas a 18–22 mm. A deformação local continua sendo feita
  por `settle_contacts()`.

**Trama oliva (ponto 3)** (`generate_cushion_materials.py`, algoritmo próprio, CC0). A sarja 2/2 de
14 mm, que lia como listras diagonais, foi trocada por uma **trama de cesto**:
- um xadrez de unidades de **~11,7 mm**, com 12 unidades por repetição de 0,14 m, o que dá **~43
  unidades** numa almofada de 50 cm;
- cada unidade é um par de cordões oliva torcidos com fio creme;
- os pontos creme oblíquos invertem a inclinação de uma unidade para a outra (chevron fino).

Os mapas têm estes tamanhos e intensidades:
- basecolor de 512 px e normal de 256 px no main; 256 e 128 px no mobile;
- relevo de ~2 mm e intensidade da normal de 0,8 (antes 1,0);
- todos são potências de 2 (o validador não acusa NPOT).

**Corpo bouclé (ponto 4).**
- A **cor visual de `areia`** passou de `#d8c9b2` (creme quente) para **`#b6b0a8`**, um cinza-bege
  quente claro. O ID `areia` continua o mesmo. É uma **estimativa visual** a partir da foto, não uma
  cor medida nem comercial.
- A base embutida inicial foi regenerada por `generate_embedded_areia.py`: base neutra × tinta, em
  sRGB, na mesma regra de `generate_materials.embedded_variants()`. `generate_materials.py` **não**
  foi executado.
- `COLORS.areia` do visualizador e do `contract.json` usa a mesma tinta. Um teste exige que as três
  coincidam.
- **Escala do bouclé:** uma unidade UV do corpo (e das almofadas claras) passou a valer
  `BODY_TILE = BODY_UV_METERS = 0,30 m`. Os laços ficam com ~4 mm e leem na distância normal.
- Linho e veludo recebem `texture.repeat = 0,30/0,14` no visualizador e mantêm a repetição física
  de 0,14 m (`FABRICS[id].repeatMeters`).
- **Sem brilho plástico:** a normal do bouclé subiu de 0,9 para **1,8**, o sheen caiu de 0,2 para
  **0,12** e a rugosidade de sheen ficou em 0,95, iguais no GLB e no módulo. Nas almofadas claras, a
  normal vai a 1,6 e o sheen a 0,15.

**Assento e pés (ponto 5).** O volume do assento foi conferido e mantido: é grosso, com rolo frontal
e um único vivo. Os pés continuam curtos, escuros e redondos, apenas visíveis.

**Câmera `photo`.** Foi reajustada à foto: `[-0,15; 1,35; 2,45] → [-0,05; 0,55; 0]`. Antes era
`[0,4; 1,13; 3,05] → [-0,05; 0,5; 0]`.

**Metadados 2.1.0.** São gerados a partir dos bytes reais e foram atualizados em:
- registro `data/models-3d.json`, `data/sofa-pilot.json` e páginas-fonte;
- `contract.json` (com `BODY_UV_METERS` e `repeatMeters`);
- `IDENTITY` e `DIMENSIONS` do módulo, `API.md` e `source/README.md`;
- `manifest.json`, `CREDITS.json` e `INTEGRATION.json`;
- `materials.json` (com `embeddedInitialBody`);
- extras dos GLBs e testes.

O poster foi recapturado no visualizador real.

## 2. Medições

| | antes 2.0.0 main | **2.1.0 main** | antes 2.0.0 mobile | **2.1.0 mobile** | alvo |
|---|---|---|---|---|---|
| triângulos | 36 176 | **38 256** | 15 872 | **17 312** | 60k / 25k |
| bytes GLB | 4 037 196 | **3 988 860** | 1 560 496 | **1 568 440** | — |
| bytes iniciais (GLB + poster + módulos) | 4 988 005 | **4 938 496** | 2 511 301 | **2 518 072** | 5 MB |
| L × A × P (m) | 2,487 × 1,106 × 1,084 | **2,503 × 1,132 × 1,098** | — | idem | — |

- **Altura total:** 1,132 m, dada pelo topo do encosto. Na 2.0.0 era o topo da almofada 03 que
  ficava acima do encosto.
- **Topos das almofadas** (z, m): 01 = 1,038, 02 = 1,065, **03 = 1,071** (a mais alta), 04 = 0,941
  e 05 = 0,955. Elas ficam 6 a 19 cm abaixo do topo do encosto, e só a 03 se aproxima dele, como na
  foto.
- sha256 `sofa.glb` = `cd718e87992672ddb3ebb8b0255989c9d332d5d6cdaf2f544deae6e71bc2fa14`
- sha256 `sofa-mobile.glb` = `cbb877780aa873dfde3b586e80e4d6514fe6d85e2220170cc0c3405f8ccac37b`

**Ajuste das almofadas.** Distância assinada contra cascas externas únicas, pelo mesmo método da
rev2. Dados em [`validation/ext001-r2/cushion-fit-main.json`](validation/ext001-r2/cushion-fit-main.json)
e [`-mobile`](validation/ext001-r2/cushion-fit-mobile.json).
- **Assento:** penetração máxima de 1,1 a 1,2 mm.
- **Encosto/braço:** no máximo 1,2 mm, que é a compressão permitida. A 01 e a 04 apoiam no encosto;
  a 02, a 03 e a 05 apoiam nas vizinhas e ficam a 9 mm ou mais do encosto.
- **Pares de vizinhas:**

  | Par | main | mobile | Área de contato |
  |---|---|---|---|
  | 01-02 | 1,6 mm | 2,2 mm | 151–169 cm² |
  | 02-03 | 1,5 mm | 2,4 mm | 148–233 cm² |
  | 04-05 | 1,3 mm | 1,8 mm | 58–72 cm² |

  No mobile o valor é maior porque a malha é mais grossa.
- **Vivos:** nenhum entra em superfície vizinha (0 em todos os pares).
- **Atravessamento:** nenhum vértice atravessa além da faixa de compressão suave.

## 3. Validação (build congelado)

- `npm test`: **25/25**. Entraram três testes novos:
  - areia embutida = base neutra × `COLORS.areia`, sem dupla tinta;
  - escala UV do corpo e `repeatMeters`;
  - imagens em potência de 2, com orçamento de 5 MB.
- `build.py --ignore-local-config --production`: OK, 26 páginas. `check_site.py --production`: OK
  (sha256 do `INTEGRATION.json` confere).
- glTF-Validator 2.0.0-dev.3.10: **0 erros, 0 avisos, 4 infos** (`UNUSED_OBJECT`, TEXCOORD dos pés)
  nos dois GLBs, em [`validation/ext001-r2/`](validation/ext001-r2/).
- **Almofadas fixas.** Medido com máscaras por almofada no ângulo da foto, nas duas variantes
  ([`colour-fixity.json`](validation/ext001-r2/colour-fixity.json)):
  - a diferença média contra o inicial é **0,0** (p99 = 0) em bouclé oliva, terracota e grafite,
    trama plana oliva e veludo terracota;
  - a imagem inteira muda 19 a 47 níveis em média.
- **Retorno a bouclé areia:** idêntico pixel a pixel ao estado inicial (diferença 0).
- **Caminho externo vs. embutido:** neutro × `#b6b0a8` em linear fica a ≤ 1,4 % da base embutida, por
  canal.
- **Comportamento** ([`behaviour.json`](validation/ext001-r2/behaviour.json)):
  - **troca rápida:** a última vence (Bouclé · Terracota) e o orçamento sai com
    `tecido=boucle&cor=terracota`; três `setFinish` simultâneos terminam em grafite;
  - **falha → nova tentativa:** a mensagem aparece, a seleção é mantida e a nova tentativa resulta em
    Trama plana · Areia;
  - **resize:** canvas de 800×500 para 600×420;
  - **dispose:** idempotente;
  - **regiões:** `materialRegions` traz 5 materiais decorativos com `stanzaFabric=false`, e eles ficam
    inalterados;
  - **home:** gira a ~20 renders/s e cai a 0 fora da tela; movimento reduzido mantém o poster;
  - **console: 0 erros**, exceto o `net::ERR_FAILED` do mapa abortado de propósito.

## 4. Avaliação visual honesta

**Agora bate com a foto:**
- O encosto lê como uma placa alta e espessa de topo arredondado, que sobe claramente acima das
  almofadas e vai do braço baixo até o fim arredondado antes da chaise.
- As almofadas são cheias, de centro abaulado, com cantos em ponta e em leque. A 03 é a mais alta,
  e a 04 aparece entre 03 e 05.
- O corpo deixou o creme plástico: é cinza-bege, com textura bouclé visível à distância.
- A trama oliva virou uma trama fina de muitas unidades, sem listras diagonais.

**Ainda difere:**
- **Almofadas claras:**
  - estão mais claras e brancas que na foto sob a luz do visualizador;
  - o bouclé delas lê como pequenos anéis em close, enquanto na foto os nós são mais grossos;
  - na foto elas "assentam" mais (base mais larga e caída). Aqui ficam um pouco mais rígidas e
    verticais.
- **Trama oliva:** à distância lê como verde-oliva médio, mais claro e menos contrastado que a
  trama marrom-oliva da foto, onde os pontos creme saltam mais. Em close o desenho é próximo, mas
  mais regular que a trama manual da foto.
- **Encosto:** na foto o topo é quase reto até a ponta esquerda. Aqui ele desce em curva para o
  braço um pouco antes (perfil de "asa"), e o braço sobressai levemente da borda do assento pelo
  lado de fora.
- **Luz:** a luz do visualizador é mais clara e frontal que a da foto. Os tons se comparam por
  relação entre as peças, não por valor absoluto.
- **Mobile:** a ponta do braço mostra leve serrilhado de textura em close, por ter menos anéis.

## 5. Limitações

- Há um único ângulo de referência: costas, lado oposto e parte de baixo são inferidos. As medidas
  são estimadas.
- Cor `areia` e escalas de textura são estimativas visuais, não medição nem catálogo.
- A validação foi feita só em SwiftShader headless: não houve GPU real, Safari, Firefox ou celular
  físico.
- `bpy` 5.0.1 foi usado no lugar do Blender 5.2.

## 6. Imagens (`images/`, prefixo `ext001r2_`, ~1,4 MB no total)

| Imagem | Mostra |
|---|---|
| [ext001r2_photo_angle_vs_reference.jpg](images/ext001r2_photo_angle_vs_reference.jpg) | SOFA-2.jpg × depois (main, mobile) × antes, na câmera `photo` 2.1.0 |
| [ext001r2_views_before_after.jpg](images/ext001r2_views_before_after.jpg) | frente, três quartos direita/esquerda, lateral: depois main, depois mobile, antes main |
| [ext001r2_cushion_closeups.jpg](images/ext001r2_cushion_closeups.jpg) | closes esquerda/centro/direita com corpo claro (areia) e escuro (grafite), depois × antes |
| [ext001r2_body_colours_cushions_fixed.jpg](images/ext001r2_body_colours_cushions_fixed.jpg) | grade de cores do corpo com almofadas fixas, main e mobile, com retorno e máscara de diagnóstico |
| [ext001r2_textures_before_after.jpg](images/ext001r2_textures_before_after.jpg) | trama oliva, almofada bouclé clara e bouclé do corpo: recorte da foto × depois × antes, na mesma câmera |
