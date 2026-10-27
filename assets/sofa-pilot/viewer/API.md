# Integração do visualizador

O módulo `sofa-viewer.js` é independente da página de demonstração. Copie a pasta do pacote mantendo os caminhos relativos e sirva por HTTP. Abra `viewer/index.html` para testar; a raiz do pacote pode ser servida com `npm start`. Não é necessário instalar dependências para usar os módulos incluídos em `viewer/vendor`.

```html
<script type="importmap">
{"imports":{"three":"./stanza-sofa-pilot/viewer/vendor/three/three.module.min.js"}}
</script>
<div id="sofa" style="width:100%;height:480px">
  <img src="./stanza-sofa-pilot/previews/poster.jpg"
       alt="Sofá orgânico visto em três quartos"
       style="width:100%;height:100%;object-fit:contain">
</div>
<script type="module">
import {createSofaViewer} from './stanza-sofa-pilot/viewer/sofa-viewer.js';
const viewer=await createSofaViewer(document.querySelector('#sofa'),{
  onFinish:selection=>console.log(selection)
});
await viewer.setFinish({fabricId:'linen',colorId:'oliva'}); // corpo do sofá; almofadas não mudam
viewer.setView('photo');
console.log(viewer.getSelection());
// Ao remover a seção: viewer.dispose();
</script>
```

Inclua controles e mensagens de erro adequados à sua página (o site usa `assets/sofa-experience.js` como exemplo de botões, teclado, seletores e fallback). O elemento hospedeiro precisa ter altura e largura diferentes de zero. Preserve o import map antes do primeiro módulo. Se a página já usa Three.js, utilize uma única versão 0.180.0 para evitar instâncias incompatíveis.

## Contrato público (revisão 2.0.0 — somente exterior)

A partir da 2.0.0 (EXT-001) o GLB contém apenas o exterior visível: grupos `upholstery` (corpo), `cushions` (cinco almofadas decorativas) e `legs` (pés). Os grupos internos `padding`, `frame` e `suspension`, a câmera `layers`, a abertura em camadas e o adaptador de rolagem `scroll.js` (GSAP) foram removidos. **Mudança incompatível**: quem dependia da abertura deve remover esses controles.

| Função | Comportamento |
|---|---|
| `createSofaViewer(element, options?)` | Retorna `Promise<viewer>` quando GLB e acabamento inicial estão prontos. Falhas rejeitam a Promise e restauram o poster. |
| `setFinish({fabricId, colorId})` | Retorna `Promise<selection>`. Aceita os dois identificadores ou uma alteração parcial. A última solicitação vence. Altera **somente** os materiais da região `body` (`fabric_main`, `fabric_seam`); almofadas decorativas e pés mantêm o acabamento fixo. Preserva a câmera. |
| `setView(viewId)` | Aplica a câmera documentada. IDs: `threequarter`, `front`, `side`, `detail`, `photo` (ângulo aproximado de SOFA-2.jpg). |
| `setProgress(number)` | **Obsoleto desde 2.0.0.** Mantido por compatibilidade: valida o número e não faz nada além de manter a peça montada (chama `onProgress(0,'Peça montada')`). `LAYER_STAGES` exporta um único estágio montado. |
| `getSelection()` | Retorna uma cópia com somente `modelId`, `revision`, `fabricId` e `colorId`. Não envia dados. |
| `dispose()` | Idempotente. Cancela render pendente, eventos e observação de tamanho; libera geometria, materiais, texturas, bitmaps, sombras e contexto WebGL. Remove o canvas e restaura os filhos originais. |

`getSelection()` retorna, por exemplo:

```json
{"modelId":"stanza-organic-01","revision":"2.0.0","fabricId":"boucle","colorId":"areia"}
```

Tecidos: `linen`, `boucle`, `velvet`. Cores: `areia`, `oliva`, `terracota`, `grafite`. São estudos visuais. Não correspondem a catálogo, disponibilidade ou amostra física homologada.

Opções: `variant:'main'|'mobile'` força uma versão; sem opção usa móvel até 760 px e principal nas demais larguras, decidida uma vez na criação. `baseUrl` aponta à raiz do pacote; por padrão é inferido do caminho do módulo. `modelUrl` permite outro caminho compatível com o mesmo contrato de grupos e materiais; `modelUrls:{main,mobile}` escolhe o arquivo de cada variante (usado pelo registro `data/models-3d.json`). `fabricId` e `colorId` escolhem acabamento inicial; um acabamento não padrão poderá carregar mapas adicionais. `onStatus(message)` e `onFinish(selection)` são callbacks opcionais (`onProgress` só existe por compatibilidade). `preserveDrawingBuffer:true` serve apenas a capturas especiais e fica desativado por padrão.

Extensões pequenas: `zoom(factor)` requer fator positivo (.85 aproxima, 1.18 afasta); `rotate(radians)` gira a câmera em torno do produto. `inspect()` retorna diagnósticos de variante, renderizações, grupos, malhas, `construction`, `materialRegions` (nome, região `body`/`decorative`/`exterior-structure`, `stanzaFabric`), materiais de corpo, mapas, descarte e limites, sem fazer parte do contrato de orçamento.

## Carga e materiais

O GLB inicial já contém bouclé areia. Nesse estado a base color embutida recebe multiplicador branco, evitando tingimento duplicado. As outras escolhas carregam os três mapas neutros da família sob demanda e os reutilizam. Voltar a bouclé areia restaura os mapas embutidos. `fabric_main` e `fabric_seam` são os bindings estáveis do corpo.

Regiões de material (extras `stanza_region` no GLB, com nomes como reserva):

| Região | Materiais | Comportamento |
|---|---|---|
| `body` | `fabric_main`, `fabric_seam` | `MeshPhysicalMaterial` com `userData.stanzaFabric=true`; únicos alterados por `setFinish` |
| `decorative` | `cushion_light_boucle`, `cushion_light_seam` (almofadas 02–04), `cushion_olive_weave`, `cushion_olive_seam`, `cushion_olive_reverse` (01 e 05) | `MeshPhysicalMaterial` fixo (sheen próprio), `stanzaFabric=false`; nunca recolorido |
| `exterior-structure` | `legs_dark` | material original do GLB, fixo |

A conversão é feita por instância de material (cache), nunca por malha, e a classificação vem da região do material: uma instância de corpo não pode ser compartilhada com uma almofada.

Base color usa sRGB, normal e roughness são dados sem conversão sRGB. UVs do modelo definem a escala física, com repetição de 140 mm. Veludo usa sheen de `MeshPhysicalMaterial`, mantendo metallic-roughness como base compatível. A versão móvel reduz geometria e mapas embutidos; ao personalizar, usa os mesmos mapas externos até 2K para preservar a definição do acabamento.

Não existe giro automático ou laço de render contínuo. A cena renderiza ao carregar, redimensionar ou receber interação. Mouse/trackpad não captura a roda de rolagem; no toque, a rolagem vertical permanece nativa. Setas giram/inclinam, + e − aproximam/afastam, Home restaura três quartos. O canvas é focável. As mudanças de vista são diretas, sem animações contínuas.

## Rolagem opcional (removida)

O adaptador `scroll.js` e a cópia do GSAP foram removidos na 2.0.0, junto com a abertura em camadas que eles acionavam.

`contract.json` contém os mesmos IDs, câmeras, dimensões estimadas, regiões de material e o estágio montado único exportados pelo módulo, além da lista `DEPRECATED`.

## Dependências e regeneração

Three.js 0.180.0 está fixado em `package-lock.json` do pacote original. Para reconstruir a cópia local: `npm ci` e `npm run vendor`. A primeira visualização usa módulos Three minificados. Não há CDN ou decodificador Draco/KTX2. `npm run check` verifica a sintaxe dos módulos próprios. Os resultados de execução e validação do ativo ficam em `validation/`.
