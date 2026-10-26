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
  onFinish:selection=>console.log(selection),
  onProgress:(progress,label)=>console.log(progress,label)
});
await viewer.setFinish({fabricId:'linen',colorId:'oliva'});
viewer.setProgress(.5);
viewer.setView('threequarter');
console.log(viewer.getSelection());
// Ao remover a seção: viewer.dispose();
</script>
```

Inclua controles e mensagens de erro adequados à sua página. A demonstração em `demo.js` exemplifica os botões, teclado, seletores e fallback. O elemento hospedeiro precisa ter altura e largura diferentes de zero. Preserve o import map antes do primeiro módulo. Se a página já usa Three.js, utilize uma única versão 0.180.0 para evitar instâncias incompatíveis.

## Contrato público

| Função | Comportamento |
|---|---|
| `createSofaViewer(element, options?)` | Retorna `Promise<viewer>` quando GLB e acabamento inicial estão prontos. Falhas rejeitam a Promise e restauram o poster. |
| `setProgress(number)` | Limita um número finito a 0…1. Calcula deslocamentos a partir das posições originais, sem acumular erros. 0 e 1 montam a mesma peça; .5 separa e .7 revela a estrutura. |
| `setFinish({fabricId, colorId})` | Retorna `Promise<selection>`. Aceita os dois identificadores ou uma alteração parcial. A última solicitação vence. Preserva câmeras e camadas. |
| `setView(viewId)` | Aplica a câmera documentada. IDs: `threequarter`, `front`, `side`, `detail`, `layers`. |
| `getSelection()` | Retorna uma cópia com somente `modelId`, `revision`, `fabricId` e `colorId`. Não envia dados. |
| `dispose()` | Idempotente. Cancela render pendente, eventos e observação de tamanho; libera geometria, materiais, texturas, bitmaps, sombras e contexto WebGL. Remove o canvas e restaura os filhos originais. |

`getSelection()` retorna, por exemplo:

```json
{"modelId":"stanza-organic-01","revision":"1.0.0","fabricId":"boucle","colorId":"areia"}
```

Tecidos: `linen`, `boucle`, `velvet`. Cores: `areia`, `oliva`, `terracota`, `grafite`. São estudos visuais. Não correspondem a catálogo, disponibilidade ou amostra física homologada.

Opções: `variant:'main'|'mobile'` força uma versão; sem opção usa móvel até 760 px e principal nas demais larguras, decidida uma vez na criação. `baseUrl` aponta à raiz do pacote; por padrão é inferido do caminho do módulo. `modelUrl` permite outro caminho compatível com o mesmo contrato de grupos e materiais. `fabricId` e `colorId` escolhem acabamento inicial; um acabamento não padrão poderá carregar mapas adicionais. `cameraNarrative:false` mantém câmera livre quando o progresso muda. `onStatus(message)`, `onFinish(selection)` e `onProgress(progress,label)` são callbacks opcionais. `preserveDrawingBuffer:true` serve apenas a capturas especiais e fica desativado por padrão.

Extensões pequenas: `zoom(factor)` requer fator positivo (.85 aproxima, 1.18 afasta); `rotate(radians)` gira a câmera em torno do produto. `inspect()` retorna diagnósticos de variante, renderizações, grupos, materiais, mapas, descarte e limites, sem fazer parte do contrato de orçamento.

## Carga e materiais

O GLB inicial já contém bouclé areia. Nesse estado a base color embutida recebe multiplicador branco, evitando tingimento duplicado. As outras escolhas carregam os três mapas neutros da família sob demanda e os reutilizam. Voltar a bouclé areia restaura os mapas embutidos. `fabric_main` e `fabric_seam` são os bindings estáveis; os demais materiais conservam seus acabamentos.

Base color usa sRGB, normal e roughness são dados sem conversão sRGB. UVs do modelo definem a escala física, com repetição de 140 mm. Veludo usa sheen de `MeshPhysicalMaterial`, mantendo metallic-roughness como base compatível. A versão móvel reduz geometria e mapas embutidos; ao personalizar, usa os mesmos mapas externos até 2K para preservar a definição do acabamento.

Não existe giro automático ou laço de render contínuo. A cena renderiza ao carregar, redimensionar ou receber interação. Mouse/trackpad não captura a roda de rolagem; no toque, a rolagem vertical permanece nativa. Setas giram/inclinam, + e − aproximam/afastam, Home restaura três quartos. O canvas é focável. As mudanças de vista e camadas são diretas, sem animações contínuas.

## Rolagem opcional

```js
import {attachScrollSequence} from './stanza-sofa-pilot/viewer/scroll.js';
const scroll=attachScrollSequence({
  viewer,
  trigger:document.querySelector('#area-de-sequencia'),
  onError:error=>console.error(error)
});
await scroll.setEnabled(true);
// Ao remover a seção, descarte primeiro o adaptador:
scroll.dispose();
viewer.dispose();
```

O adaptador carrega GSAP 3.13.0/ScrollTrigger apenas ao ser ativado. Usa `viewer.setProgress`, sem lógica duplicada de geometria. Não fixa a página, não altera a posição de rolagem e não usa snapping. A preferência `prefers-reduced-motion` desativa o acompanhamento por rolagem. O controle deslizante e os botões continuam funcionando. `scroll.dispose()` remove a instância do ScrollTrigger e seus eventos locais sem desligar outras animações que a página possa ter.

`contract.json` contém os mesmos IDs, câmeras, dimensões estimadas e deslocamentos em metros exportados pelo módulo. Os deslocamentos são locais, somados às transformações originais dos grupos, e a interpolação entre etapas usa smoothstep. As camadas representam um princípio ilustrativo, sem especificação de fabricação.

## Dependências e regeneração

Three.js 0.180.0 e GSAP 3.13.0 estão fixados em `package-lock.json`. Para reconstruir a cópia local: `npm ci` e `npm run vendor`. A primeira visualização usa módulos Three minificados; arquivos GSAP estão separados para carga opcional. Não há CDN ou decodificador Draco/KTX2. `npm run check` verifica a sintaxe dos módulos próprios. Os resultados de execução e validação do ativo ficam em `validation/`.
