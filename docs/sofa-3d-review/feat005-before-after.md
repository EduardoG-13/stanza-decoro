# FEAT-005 — Tecidos, cores e iluminação: personalização RENDERIZADA verificada

Foco: **confirmar** que a personalização global existente muda de fato o resultado RENDERIZADO (não
só o seletor), nas 12 combinações × 2 variantes, com resposta de luz distinta por tecido e sem duplo
tingimento no retorno a bouclé+areia. Personalização **global preservada**; cor por almofada fica em
[proposta separada](proposal-per-cushion-color.md). **Sem mudança de geometria e sem rodar
`generate_materials.py`** (README proíbe; `numpy==2.5.2` indisponível): mapas existentes reutilizados.

![Grade 12 combinações (tecido × cor) renderizadas](images/customization_grid_main.png)

![Resposta de luz por tecido (mesma cor oliva)](images/fabric_light_response_main.png)

![Retorno a bouclé+areia sem duplo tingimento](images/customization_areia_return_main.png)

## Tabela malha → binding verificada no visualizador real — CONFIRMADO

`inspect().fabricMaterials` dirigido pela API pública, para cada combinação:

| Combinação | materiais tingidos | cor aplicada | esperado | veredito |
|---|---|---|---|---|
| boucle-areia | fabric_main, fabric_seam | `#ffffff` (embutido) | `#ffffff` | OK |
| boucle-oliva/terracota/grafite | fabric_main, fabric_seam | `#72765a` / `#ae6952` / `#494b4b` | idem | OK |
| linen-{4 cores} | fabric_main, fabric_seam | cor correspondente | idem | OK |
| velvet-{4 cores} | fabric_main, fabric_seam | cor correspondente | idem | OK |

- Só `fabric_main`/`fabric_seam` (marcados `userData.stanzaFabric`) mudam. Os materiais
  ilustrativos (`padding_illustrative`, **`batting_illustrative`** novo, `frame_illustrative`,
  `legs_dark`, `suspension_illustrative`) **não** recebem tint — confirmado por não aparecerem na
  lista de `fabricMaterials` e por não terem `userData.stanzaFabric`.
- `fabric_main`/`fabric_seam` cobrem **corpo + almofadas + vivos (welts)** (as almofadas usam o mesmo
  `cloth`/`cloth.copy()`), então a troca atinge a peça inteira — refuta visualmente a hipótese
  antiga "cor só nas almofadas" (ver grade: o corpo inteiro muda de cor).

## Resposta de luz distinta por tecido — CONFIRMADO

Mesma cor (oliva), câmera e luz constantes; parâmetros PBR por tecido (preservados do upstream):

| Tecido | roughness | normalScale | sheen | sheenRoughness | leitura |
|---|---|---|---|---|---|
| boucle | 1 | 0.9 | 0.2 | 0.9 | relevo de laçadas visível |
| linen | 1 | 0.78 | 0.12 | 0.85 | trama plana mais lisa |
| velvet | 1 | 0.38 | 0.72 | 0.55 | brilho suave a luz rasante, **sem glow branco** |

- Base color em **sRGB**; normal/roughness como **dado linear** (`NoColorSpace`); `flipY=false`;
  `repeat (1,1)` com a escala física de ~0,14 m carregada pelas UVs (`TILE=.14`). Sem trama esticada,
  sem brilho plástico, sem aspecto metálico (`metalness=0` em todas).
- **Veludo com contenção:** `sheenColor` é a cor do acabamento interpolada 35% para o branco; nas
  capturas velvet-grafite/oliva o sheen aparece como realce suave nas superfícies superiores **sem
  apagar a cor** (grafite continua escuro, oliva continua verde). Não é um glow branco.

## "Quase branco" tratado sem duplo tingimento — CONFIRMADO

- bouclé+areia usa o **base color embutido já tingido** multiplicado por **`#ffffff`** (intencional,
  para não tingir duas vezes). O JPEG embutido permanece byte-idêntico desde a 1.0.0.
- A impressão de alta chave no areia vem do **base ~0.92 + ambiente claro** (exposição 0.9,
  `environmentIntensity` 0.35), não de bug nem de binding. É o comportamento de projeto já
  verificado em I.5; **não** foi introduzido nenhum tint extra para "corrigir" o branco (isso seria
  duplo tingimento). As cores escuras (grafite/terracota/oliva) mostram que a cadeia de cor funciona.
- **Retorno a bouclé+areia** restaura os mapas embutidos e volta a cor a `#ffffff` (confirmado:
  `texturesLoaded` inclui `boucle:embedded-areia` e as cores voltam a `ffffff/ffffff`). Sem
  escurecimento acumulado.

## Compartilhamento de material preservado — CONFIRMADO

`fabric_seam` é `cloth.copy()` de `fabric_main`; ambos compartilhados por corpo e almofadas
(compartilhamento intencional). Nenhum `material.color` foi aplicado indiscriminadamente à cena. Cor
independente por região exigiria clonar materiais e estender o contrato de orçamento → fica na
[proposta separada](proposal-per-cushion-color.md), sem tocar no backend/intake nem no payload atual.

## Contratos preservados

IDs de tecido (`boucle/linen/velvet`) e cor (`areia/oliva/terracota/grafite`) inalterados; forma da
seleção e redirecionamento de orçamento inalterados (`npm test` 19/19, incluindo quote-redirect);
política "última requisição vence" e "falha de textura mantém a última combinação válida" intactas
(não alteradas). Nenhuma textura regenerada.

## Conclusão honesta

A personalização global **já estava bem autorada** e foi **verificada como renderizada** (não só o
seletor). Não foram feitas alterações destrutivas de material que pudessem regredir as 12
combinações; a entrega deste feature é a **verificação rendida** + a **proposta separada** de cor por
almofada. **LIMITAÇÃO:** WebGL por SwiftShader (software); fiel ao contrato, não substitui GPU
real/Safari/Firefox/celular físico.
