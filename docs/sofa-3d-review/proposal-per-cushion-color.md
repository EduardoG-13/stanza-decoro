# Proposta separada (extensão futura): cor independente por almofada / por região

> **Superado (EXT-001 / 2.0.0):** as almofadas passaram a ter materiais decorativos fixos próprios, separados do corpo, conforme a foto. Ver [ext001-exterior.md](ext001-exterior.md).

> **Status: proposta — NÃO implementada nesta entrega.** O usuário pediu explicitamente que
> controles independentes por almofada fiquem como **proposta separada, sem atrasar esta entrega**.
> A personalização **global** existente foi mantida intacta. Nenhuma opção nova de orçamento, nem um
> formato de payload incompatível, foi introduzido agora. O contrato de redirecionamento de orçamento
> permanece `/orcamento.html?referencia=sofa-organico&estudo=&tecido=&cor=`.

## Motivação

A foto de referência (`sofas/SOFA-2.jpg`) mostra **cinco almofadas soltas: três claras e duas de
trama oliva**. O estudo atual aplica um **único** acabamento (tecido + cor) a toda a peça. Reproduzir
a composição da foto (duas almofadas oliva entre três claras) exigiria **cor por almofada** — hoje
fora de escopo.

## Por que não entra agora (impacto no contrato)

O contrato público de seleção é um único par `{fabricId, colorId}`:

```
selection = { modelId:'stanza-organic-01', revision, fabricId, colorId }
quote redirect: /orcamento.html?referencia=sofa-organico&estudo=<modelId>&tecido=<fabricId>&cor=<colorId>
```

`setFinish` muta **todos** os materiais marcados `userData.stanzaFabric` de uma vez. Introduzir cor
por almofada quebraria/estenderia:

1. **O formato da seleção** (passaria a precisar de uma lista de cores por região).
2. **O payload de orçamento** (`tecido`/`cor` únicos → múltiplos), que o backend de intake
   (fora de escopo, não deve ser tocado) e `tests/quote-redirect.test.mjs` assumem como únicos.
3. **O binding de materiais**: hoje `fabric_main`/`fabric_seam` são **compartilhados** por corpo e
   almofadas (compartilhamento intencional). Cor por almofada exigiria clonar materiais por almofada.

Fazer isso agora atrasaria a entrega e arriscaria o contrato preservado. Por isso fica proposto.

## Esboço técnico (quando/se for aprovado como trabalho próprio)

Caminho não-destrutivo, aditivo e retrocompatível:

1. **Geometria/binding:** no `build_sofa.py`, dar a cada `cushion_0N_cover`/`_welt` um material
   **clonado** próprio (ex. `fabric_cushion_1..5`) ainda derivado de `fabric_main`, mantendo
   `userData.stanzaFabric` e preservando o compartilhamento do corpo. Clonar **apenas** onde a
   independência real é necessária (as 5 almofadas), não a cena inteira.
2. **API aditiva:** uma sobrecarga opcional `setFinish({ fabricId, colorId, cushions:[{index,colorId}] })`
   que, quando ausente, se comporta **exatamente** como hoje (global). Default = global → nenhum
   consumidor existente muda.
3. **Seleção estendida (retrocompatível):** `selection` ganha um campo opcional `cushionColors`
   (ausente no modo global). O `getSelection()` só o inclui quando usado.
4. **Orçamento:** manter `tecido`/`cor` como o acabamento **base/global**; anexar as exceções por
   almofada num parâmetro **novo e opcional** (ex. `almofadas=1:oliva,4:oliva`) **somente** após
   alinhar com o backend de intake e atualizar `quote-redirect` e seus testes. **Não** alterar o
   formato atual até esse alinhamento.
5. **UI:** um seletor por almofada no configurador (`sofa-experience.js`), atrás de um toggle
   "cores por almofada", sem alterar o fluxo global padrão.
6. **Camadas/estado:** nenhuma interação com `setProgress`; cores são ortogonais ao explodido.

## Esforço/risco estimado (indicativo, não comprometido)

- Geometria + clones de material: baixo/médio (edição paramétrica + re-export + re-hash).
- API/seleção aditiva: baixo (default preserva tudo).
- Orçamento: **médio/alto** por depender do backend de intake (fora de escopo aqui) e de novos testes.
- UI do configurador: baixo/médio.

## Decisão

Entregar **agora** a personalização **global** verificada (12 combinações × 2 variantes, abaixo e no
relatório FEAT-005). Cor por almofada fica **registrada aqui** como extensão futura, a ser priorizada
pela Stanza, sem bloquear nem atrasar esta entrega e sem mudar o contrato de orçamento.
