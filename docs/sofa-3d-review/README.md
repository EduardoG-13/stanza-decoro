# Revisão dos estudos 3D (stanza-organic-01, stanza-straight-01, stanza-modular-01, stanza-two-seat-01, stanza-piped-01, stanza-armchair-01 e fila)

Esta pasta reúne, de forma **versionada e visível no PR**, o material de revisão do aprimoramento
do sofá 3D (branch `work/sofa-3d-inspection`). Os caminhos internos do sandbox (`.agents/`,
`/projects/sandbox/.kiro/`) **não** são revisáveis pelo usuário; por isso as imagens e relatórios
essenciais ficam aqui, com caminhos relativos ao repositório, e aparecem renderizados no PR.

> A `main` permanece intacta. Nada foi mesclado nem publicado no site oficial. Este é um estudo
> visual; dimensões são estimadas, não desenhos de fabricação.

## Coleção — pipeline models3d e EXT-002

Infraestrutura multi-modelo (biblioteca Blender, biblioteca de acabamentos, registro, visualizador
único, scripts de captura/validação): [models3d-pipeline.md](models3d-pipeline.md).

**EXT-002 — Sofá cinza de linhas retas** (`stanza-straight-01` 1.0.0, catálogo `sofa-reto`):
[ext002-sofa-reto.md](ext002-sofa-reto.md) · prévia `/explorar-sofa.html?modelo=stanza-straight-01`.

![EXT-002: foto × render](images/ext002_photo_vs_render.jpg)

![EXT-002: cores do corpo com decoração fixa](images/ext002_body_colours.jpg)

**EXT-003 — Sofá modular cinza** (`stanza-modular-01` 1.0.0, catálogo `sofa-modular`):
[ext003-sofa-modular.md](ext003-sofa-modular.md) · prévia `/explorar-sofa.html?modelo=stanza-modular-01`.

![EXT-003: foto × render](images/ext003_photo_vs_render.jpg)

**EXT-004 — Sofá claro de dois assentos** (`stanza-two-seat-01` 1.0.0, catálogo `sofa-dois-assentos`):
[ext004-sofa-dois-assentos.md](ext004-sofa-dois-assentos.md) · prévia `/explorar-sofa.html?modelo=stanza-two-seat-01`.

![EXT-004: foto × render](images/ext004_photo_vs_render.jpg)

**EXT-005 — Sofá cinza com vivo claro** (`stanza-piped-01` 1.1.0, catálogo `sofa-com-vivo`; vivo = contraste fixo):
[ext005-sofa-com-vivo.md](ext005-sofa-com-vivo.md) · almofadas cheias 1.1.0: [cushions-fix-2026-10.md](cushions-fix-2026-10.md) · prévia `/explorar-sofa.html?modelo=stanza-piped-01`.

![EXT-005 1.1.0: foto × antes × depois e perfil](images/cushfix_ext005_photo_side.jpg)

**EXT-014 — Poltrona azul com braços** (`stanza-armchair-01` 1.0.0, catálogo `poltrona-bracos`; uma poltrona, puff EXT-034 fora do escopo):
[ext014-poltrona-bracos.md](ext014-poltrona-bracos.md) · prévia `/explorar-sofa.html?modelo=stanza-armchair-01`.

![EXT-014: foto × render](images/ext014_photo_vs_render.jpg)

## EXT-001 r2, revisão 2.1.0 (refino de fidelidade à foto)

Encosto alto e espesso de topo arredondado, almofadas cheias com cantos em ponta, trama oliva fina,
corpo bouclé cinza-bege legível. Relatório: [ext001-r2-refinement.md](ext001-r2-refinement.md).

![Ângulo da foto 2.1.0: referência × depois × antes](images/ext001r2_photo_angle_vs_reference.jpg)

![Texturas: foto × depois × antes](images/ext001r2_textures_before_after.jpg)

![Cores do corpo com almofadas fixas (2.1.0)](images/ext001r2_body_colours_cushions_fixed.jpg)

## Anterior — EXT-001, revisão 2.0.0 (somente exterior)

**Mudança de escopo:** a construção interna e a abertura em camadas foram abandonadas; a prioridade
é um exterior realista. Relatório: [ext001-exterior.md](ext001-exterior.md). Fila de todos os
modelos: [QUEUE.md](QUEUE.md) (EXT-001 … EXT-054, com a regra de regiões de material).

![Ângulo da foto: referência × depois × antes](images/ext001_photo_angle_vs_reference.jpg)

![Só o corpo muda de cor/tecido; almofadas fixas (main)](images/ext001_body_colours_cushions_fixed_main.jpg)

![Contatos das almofadas (main)](images/ext001_cushion_contacts_main.jpg)

![Vistas antes × depois (main)](images/ext001_views_before_after_main.jpg)

As seções abaixo são **histórico** (revisões 1.x). As partes sobre interior e camadas (FEAT-003,
FEAT-004 e as imagens de camadas/estrutura) estão **superadas pela mudança de escopo** e são mantidas
apenas como registro.

## Histórico (revisões 1.x)

## Imagens de comparação (antes/depois)

As imagens abaixo são compostas lado a lado (antes | depois), rotuladas, geradas com Pillow a partir
de capturas **reais do visualizador WebGL** (`createSofaViewer`, Chrome for Testing / SwiftShader),
e reduzidas para manter o repositório leve. Não são renders de Blender.

### Almofadas (FEAT-002 rev2, revisão 1.3.0) — reassentamento real

Relatório: [feat002-rev2-cushions.md](feat002-rev2-cushions.md). Métrica corrigida (penetração assinada real contra as cascas
externas) em [`validation/feat002-rev2/`](validation/feat002-rev2/).

![Vistas globais antes/depois](images/feat002rev2_global_main.jpg)

![Pares vizinhos 01-02 / 02-03 / 03-04 / 04-05](images/feat002rev2_pairs_main.jpg)

![Cada almofada contra encosto/braço (de cima)](images/feat002rev2_backrest_main.jpg)

![Cada almofada contra encosto/vizinha (lateral)](images/feat002rev2_backrest_side_main.jpg)

![Borda inferior sobre o assento](images/feat002rev2_seat_main.jpg)

![Mobile: vistas-chave](images/feat002rev2_mobile.jpg)

![Mobile: close-ups](images/feat002rev2_mobile_closeups.jpg)

![Veludo-grafite](images/feat002rev2_velvet_grafite_main.jpg)

![SUPERADO — abertura em camadas (removida na 2.0.0)](images/feat002rev2_layers_stages.jpg)

![DIAGNÓSTICO: cores por almofada e cortes (não é render de aceitação)](images/feat002rev2_diagnostics_main.jpg)

### Almofadas (FEAT-002, 1ª versão) — SUPERADA pela rev2 (mantida como histórico)

![Almofadas antes/depois, detalhe (desktop)](images/cushions_before_after_detail_main.png)

![Almofadas antes/depois, detalhe (mobile)](images/cushions_before_after_detail_mobile.png)

![Almofadas antes/depois, perspectiva](images/cushions_before_after_threequarter_main.png)

### Interior por componentes (FEAT-003) — SUPERADO pela mudança de escopo (2.0.0)

![Estrutura antes/depois (camadas em p.7)](images/structure_before_after_layers_main.png)

![Percintas tensionadas e armação de madeira (close)](images/structure_webbing_frame_closeup_main.png)

### Abertura em camadas (FEAT-004) — SUPERADO pela mudança de escopo (2.0.0)

![Sequência de abertura: montada → tecido → manta → espuma → percintas → madeira](images/layers_sequence_main.png)

![Reversibilidade: p0 e p1 idênticos (deriva = 0)](images/layers_reversibility_main.png)

### Personalização verificada (FEAT-005) — 12 combinações

![Grade 12 combinações (tecido × cor) renderizadas](images/customization_grid_main.png)

![Resposta de luz por tecido (mesma cor oliva)](images/fabric_light_response_main.png)

![Retorno a bouclé+areia com os mapas embutidos (sem duplo tingimento)](images/customization_areia_return_main.png)

### Enquadramento final nos dois consumidores (FEAT-006)

![Configurador e hero (desktop)](images/final_framing_consumers.png)

![Configurador e hero (mobile)](images/final_framing_consumers_mobile.png)

## Relatórios

- [EXT-001 r2 — refino de fidelidade à foto, revisão 2.1.0](ext001-r2-refinement.md) — **atual**
- [EXT-001 — exterior realista, revisão 2.0.0](ext001-exterior.md) — base da 2.1.0
- [Fila de modelos 3D EXT-001 … EXT-054](QUEUE.md)

- [Gate de fidelidade do gerador (pré-FEAT-002)](gate-comparison_feat002.md)
- [FEAT-002 rev2 — almofadas reassentadas, métrica corrigida (revisão 1.3.0)](feat002-rev2-cushions.md) — superado pela 2.0.0
- [FEAT-002 — almofadas: contato suave](feat002-before-after.md) — **superado** pela rev2
- [FEAT-003 — interior por componentes](feat003-before-after.md) — **superado** (escopo mudou na 2.0.0)
- [FEAT-004 — abertura em camadas reversível](feat004-before-after.md) — **superado** (escopo mudou na 2.0.0)
- [FEAT-005 — tecidos, cores e iluminação](feat005-before-after.md) — parcialmente superado (personalização só no corpo)
- [FEAT-006 — exportação final, métricas e validação](feat006-final.md) — **superado** pela 2.0.0
- [Proposta separada: cor independente por almofada](proposal-per-cushion-color.md) — superada (almofadas com materiais fixos próprios)
- Relatórios do Khronos glTF-Validator: atuais em [`validation/ext001/`](validation/ext001/); históricos em [`validation/`](validation/)

## Rótulos de honestidade

Nos relatórios: **CONFIRMADO** = demonstrado por execução/medição direta; **HIPÓTESE** = plausível,
não comprovado; **LIMITAÇÃO** = o ambiente não permitiu verificar. O WebGL aqui roda por SwiftShader
(software), fiel ao contrato, mas não é GPU real nem Safari/Firefox/celular físico.
