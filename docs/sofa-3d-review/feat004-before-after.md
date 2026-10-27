# FEAT-004 — Abertura em camadas legível e reversível (tecido → manta → espuma → percintas → madeira)

> **SUPERADO (mudança de escopo, EXT-001 / revisão 2.0.0).** A abertura em camadas foi removida do visualizador e das páginas; `setProgress` é um no-op obsoleto. Mantido apenas como histórico; ver [ext001-exterior.md](ext001-exterior.md).

Reautoria do contrato de `setProgress`/`LAYER_STAGES` no visualizador, mantendo os 6 grupos públicos
e a semântica (0 e 1 = montada idêntica; ~.5 = separada; ~.7 = estrutura exposta). Depende do
FEAT-003: a etapa de "manta" só é legível porque agora existe a camada de manta distinta da espuma
dentro do grupo `padding`.

![Sequência de abertura (p0 → p.2 → p.35 → p.5 → p.7)](images/layers_sequence_main.png)

![Reversibilidade: p0 e p1 idênticos (deriva medida = 0)](images/layers_reversibility_main.png)

## Sequência autorada (na ordem de construção)

| progress | rótulo | o que fica legível |
|---|---|---|
| 0 | Peça montada | peça fechada |
| .2 | Almofadas e revestimento se soltam | tecido (upholstery) + almofadas sobem juntos |
| .35 | Manta exposta sob o tecido | tecido alto; a **manta** aparece sob ele, ainda sobre a espuma |
| .5 | Revestimento e manta separados da espuma | **separada**: tecido + manta erguidos, núcleo de espuma ainda assentado |
| .7 | Estrutura exposta · percintas e madeira | **estrutura**: espuma sobe; **percintas** e **armação de madeira** ficam legíveis; pés com a estrutura |
| 1 | Retorno à peça montada | idêntica à 0 |

As almofadas, por serem a camada solta do topo, sobem com o tecido (não têm etapa própria). Os pés
permanecem com a armação (madeira), coerente com o FEAT-003 (pés fazem parte do frame).

## Como a manta separa da espuma sem criar um 7º grupo — CONFIRMADO

O build aninha espuma e manta dentro do **mesmo** grupo público `padding`. Para separar a manta fina
do núcleo de espuma **sem** introduzir um novo grupo público, cada etapa carrega, além dos
`offsets` dos 6 grupos, um `subOffsets` opcional indexado pelos nós internos do padding
(`seat_batting`/`back_batting`/`seat_foam`/`back_foam`). O `setProgress` aplica esses offsets em
espaço LOCAL do padding, recomputados a cada chamada a partir das posições originais (padrão
`originalPositions`, **sem acúmulo de delta**). Assets anteriores à 1.2.0 (sem esses nós) simplesmente
movem o `padding` inteiro — degradação graciosa.

## Verificações — CONFIRMADO

- **Sem deriva:** no visualizador real, snapshot das posições dos grupos em p0, depois um ciclo
  `.5 → .7 → .35 → 1`, e comparação com p1: **deriva máxima = 0** em main e mobile.
- **Consistência das três representações:** teste `tests/layer-stages.test.mjs` afirma
  `LAYER_STAGES (módulo) == contract.json.LAYER_STAGES == manifest.json.layerSequence.stages`, além
  de checar que 0 e 1 têm todos os offsets zero e idênticos, que .5 ergue o tecido com a espuma ainda
  assentada e que .7 ergue a espuma para expor a estrutura. Também replica a matemática de
  `setProgress` (sem THREE) e prova que p0 e p1 devolvem as posições-base (sem deriva).
- **Tecido não atravessa o corpo como bloco rígido:** o tecido sobe e afasta progressivamente
  (translação suave para cima/frente), expondo a camada seguinte a cada etapa; é uma construção
  ilustrativa, sem inventar zíperes ou desmontagem real que a foto não documenta.
- **Sem expansão por rolagem:** `grep` confirma que nenhuma página importa `viewer/scroll.js` (as
  únicas ocorrências são a documentação em API.md e `scroll-behavior` no CSS). A rolagem vertical
  permanece livre.
- `npm test`: 19/19 (13 originais + 6 novos de comportamento 3D). Build + `check_site --production`:
  OK. Visualizador real: `createSofaViewer` OK ambos os variantes, 0 erros de console.

## Arquivos alterados

- `assets/sofa-pilot/viewer/sofa-viewer.js`: `LAYER_STAGES` reautorado (6 etapas, com `subOffsets`);
  `setProgress` aplica `subOffsets` aos nós de padding; captura das posições originais dos sub-nós.
- `assets/sofa-pilot/viewer/contract.json`: `LAYER_STAGES` idêntico (gerado da mesma fonte canônica).
- `assets/sofa-pilot/manifest.json`: `layerSequence.stages` idêntico + `order`/`note` atualizados.
- `pages/explore.html`: legenda das camadas atualizada para a ordem de construção; HTML raiz
  regenerado via `build.py` (não editado à mão).
- `tests/layer-stages.test.mjs`: novo (consistência + não-deriva). Declara explicitamente que não
  substitui a inspeção visual.

A geometria (GLBs/.blend) **não** mudou neste feature; é um feature de visualizador/contrato.
