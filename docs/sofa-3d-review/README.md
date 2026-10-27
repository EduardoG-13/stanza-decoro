# Revisão do estudo 3D do sofá orgânico (stanza-organic-01)

Esta pasta reúne, de forma **versionada e visível no PR**, o material de revisão do aprimoramento
do sofá 3D (branch `work/sofa-3d-inspection`). Os caminhos internos do sandbox (`.agents/`,
`/projects/sandbox/.kiro/`) **não** são revisáveis pelo usuário; por isso as imagens e relatórios
essenciais ficam aqui, com caminhos relativos ao repositório, e aparecem renderizados no PR.

> A `main` permanece intacta. Nada foi mesclado nem publicado no site oficial. Este é um estudo
> ilustrativo; dimensões e construção interna são estimadas, não desenhos de fabricação.

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

![Abertura em camadas com a nova geometria](images/feat002rev2_layers_stages.jpg)

![DIAGNÓSTICO: cores por almofada e cortes (não é render de aceitação)](images/feat002rev2_diagnostics_main.jpg)

### Almofadas (FEAT-002, 1ª versão) — SUPERADA pela rev2 (mantida como histórico)

![Almofadas antes/depois, detalhe (desktop)](images/cushions_before_after_detail_main.png)

![Almofadas antes/depois, detalhe (mobile)](images/cushions_before_after_detail_mobile.png)

![Almofadas antes/depois, perspectiva](images/cushions_before_after_threequarter_main.png)

### Interior por componentes (FEAT-003) — manta, espuma, percintas, armação

![Estrutura antes/depois (camadas em p.7)](images/structure_before_after_layers_main.png)

![Percintas tensionadas e armação de madeira (close)](images/structure_webbing_frame_closeup_main.png)

### Abertura em camadas (FEAT-004)

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

- [Gate de fidelidade do gerador (pré-FEAT-002)](gate-comparison_feat002.md)
- [FEAT-002 rev2 — almofadas reassentadas, métrica corrigida (revisão 1.3.0)](feat002-rev2-cushions.md)
- [FEAT-002 — almofadas: contato suave](feat002-before-after.md) — **superado** pela rev2
- [FEAT-003 — interior por componentes](feat003-before-after.md)
- [FEAT-004 — abertura em camadas reversível](feat004-before-after.md)
- [FEAT-005 — tecidos, cores e iluminação](feat005-before-after.md)
- [FEAT-006 — exportação final, métricas e validação](feat006-final.md)
- [Proposta separada: cor independente por almofada (extensão futura)](proposal-per-cushion-color.md)
- Relatórios frescos do Khronos glTF-Validator: [`validation/`](validation/)

## Rótulos de honestidade

Nos relatórios: **CONFIRMADO** = demonstrado por execução/medição direta; **HIPÓTESE** = plausível,
não comprovado; **LIMITAÇÃO** = o ambiente não permitiu verificar. O WebGL aqui roda por SwiftShader
(software), fiel ao contrato, mas não é GPU real nem Safari/Firefox/celular físico.
