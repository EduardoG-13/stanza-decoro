# Fila de modelos 3D (EXT-001 … EXT-054)

Arquivo persistente da fila. Infraestrutura comum dos modelos novos: [models3d-pipeline.md](models3d-pipeline.md). Os códigos EXT são itens da fila, **não** IDs de catálogo; a coluna
“Relação” aponta o item de `data/catalog.json` / `data/portfolio.json` correspondente. Modelos com
ativos reais entram também no registro `data/models-3d.json`, lido pelo configurador.

Estados: **pendente** · **em execução** · **tecnicamente validado – revisão visual pendente** ·
**bloqueado** · **registrado — fora da produção** (itens que não viram modelo 3D nesta fila).

## Regra de classificação das regiões de material

Toda peça nova separa seus materiais por região **na fonte** (propriedade `stanza_region`, exportada
nos extras do glTF) e o visualizador obedece a essa marcação:

| Região | O que entra | Comportamento no configurador |
|---|---|---|
| **corpo personalizável** (`body`) | Estofado principal da peça (assento, encosto, braços, base estofada) e seus vivos/costuras do mesmo tecido | Único alvo de tecido + cor (`setFinish`); nomes estáveis `fabric_main`/`fabric_seam` |
| **decoração fixa** (`decorative`) | Almofadas soltas, mantas, estampas ou tecidos diferentes do corpo que aparecem na foto | Acabamento fixo de referência; nunca recolorido, mesmo que comece igual ao corpo |
| **contrastes fixos** (`contrast`) | Vivos/frisos de outra cor, tachas, botões de capitonê, bordados, lambrequim contrastante | Fixos; só viram opção quando houver decisão explícita de produto |
| **estrutura externa aparente** (`exterior-structure`) | Pés, bases, molduras e madeira/metal visíveis por fora | Fixos (material próprio). Nada interno: sem armação oculta, espuma, manta ou percintas |

Em caso de dúvida, o material fica **fixo** e a dúvida é registrada em “Limitações” do item.



## A. Mobiliário

### EXT-001 — Sofá orgânico claro

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`sofas/SOFA-2.jpg`](../../sofas/SOFA-2.jpg)
- **Relação:** catálogo `sofa-organico`; portfólio `projeto-2`
- **Arquivos:** `assets/sofa-pilot/source/build_sofa.py` (fonte de verdade), `source/generate_cushion_materials.py`, `source/generate_embedded_areia.py`, `models/sofa.glb`, `models/sofa-mobile.glb`, `source/sofa.blend`, `materials/cushions/`, `viewer/sofa-viewer.js`; registro `data/models-3d.json` (`stanza-organic-01`)
- **Revisão:** 2.1.0 (somente exterior; EXT-001 r2 — refino de fidelidade à foto sobre a 2.0.0)
- **Opções reais:** corpo — tecidos `boucle`/`linen`/`velvet` × cores `areia`/`oliva`/`terracota`/`grafite`. Almofadas (3 bouclé claras, 2 trama oliva com avesso creme) e pés: fixos.
- **Evidências:** [ext001-r2-refinement.md](ext001-r2-refinement.md) (2.1.0), imagens `images/ext001r2_*.jpg`, validação `validation/ext001-r2/`; histórico 2.0.0 em [ext001-exterior.md](ext001-exterior.md), `images/ext001_*.jpg`, `validation/ext001/`
- **Limitações:** um único ângulo de referência (costas e lado oposto inferidos); medidas estimadas; tecido do corpo e cor `areia` (`#b6b0a8`) são estimativas visuais; almofadas claras mais brancas e trama oliva mais clara/menos contrastada que na foto à distância; validação só em navegador headless (SwiftShader).
- **Próxima ação:** revisão visual pela Stanza nas imagens de comparação da 2.1.0; ajustes finos de tom das almofadas e contraste da trama (ver §4 do relatório r2) antes de marcar como aprovado.

### EXT-002 — Sofá cinza de linhas retas

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`sofas/SOFA-5.jpg`](../../sofas/SOFA-5.jpg)
- **Relação:** catálogo `sofa-reto`; portfólio `projeto-5` (única peça com esta foto; IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-straight-01/` — `source/build.py` (fonte de verdade, usa `assets/models-3d/lib/stanza3d.py`), `source/stanza-straight-01.blend`, `models/stanza-straight-01.glb`, `models/stanza-straight-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas `assets/models-3d/materials/boucle-mescla/` e `wood-wenge/`; registro `data/models-3d.json` (`stanza-straight-01`)
- **Revisão:** 1.0.0 (somente exterior) · principal 49 384 tri / 4,15 MB · móvel 21 996 tri / 1,22 MB
- **Opções reais:** corpo (braços, base, encosto, almofadas de assento e encosto) — tecidos `boucle-mescla` (inicial, novo), `boucle`, `linen`, `velvet` × cores `gelo` (inicial, nova), `areia`, `grafite`, `oliva`, `terracota`. Duas almofadas decorativas (bouclé) e plinto de madeira escura: fixos.
- **Evidências:** [ext002-sofa-reto.md](ext002-sofa-reto.md), imagens `images/ext002_*.jpg`, validação `validation/ext002/` (glTF-Validator 0/0/0/0, comportamento 73/73, máscaras 0 px nas decorativas, contatos, regressão EXT-001 0 px)
- **Prévia:** `/explorar-sofa.html?modelo=stanza-straight-01`; produto `/modelos/sofa-reto.html` com "Ver em 3D"
- **Limitações:** um único ângulo (costas, lateral externa direita e topo inferidos); medidas estimadas com assento fixado em 0,44 m e profundidade pouco determinada (0,75–0,95 m → 0,86 m); bouclé mescla e `gelo` (`#babcc0`) são estimativas visuais; decorativas menos cheias/caídas que na foto; contato móvel até 5 mm oculto sob a decorativa esquerda; validação só headless.
- **Próxima ação:** revisão visual pela Stanza das comparações (ângulo da foto, cores, close-ups); se aprovado, marcar `approved`; ajustes prováveis: enchimento das decorativas e abaulado dos encostos.

### EXT-003 — Sofá modular cinza

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-3.jpg`](../../sofas/SOFA-3.jpg)
- **Relação:** catálogo `sofa-modular`; portfólio `projeto-3`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-004 — Sofá claro de dois assentos

- **Estado:** pendente
- **Fontes:** [`acervo/sofa-dois-assentos.webp`](../../acervo/sofa-dois-assentos.webp)
- **Relação:** catálogo `sofa-dois-assentos`; portfólio `projeto-47`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-005 — Sofá cinza com vivo claro

- **Estado:** pendente
- **Fontes:** [`acervo/sofa-com-vivo.webp`](../../acervo/sofa-com-vivo.webp)
- **Relação:** catálogo `sofa-com-vivo`; portfólio `projeto-48`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Vivo claro = contraste fixo.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-006 — Sofá azul com tachas aparentes

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-6.jpg`](../../sofas/SOFA-6.jpg), [`acervo/sofa-azul-fundo-claro.png`](../../acervo/sofa-azul-fundo-claro.png)
- **Relação:** catálogo `sofa-contorno-marcado` (fonte `sofa-azul-fundo-claro.png`, galeria `SOFA-6.jpg`); portfólio `projeto-6`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Mesma peça nas duas fotos; SOFA-6 é a referência de forma. Tachas = contraste fixo.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-007 — Sofá verde de braços curvos

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-9.png`](../../sofas/SOFA-9.png), [`sofas/SOFA-9.2.png`](../../sofas/SOFA-9.2.png)
- **Relação:** catálogo `sofa-curvo`; portfólio `projeto-9`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Dois ângulos da mesma peça (único item com segundo ângulo confirmado).
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-008 — Sofá em L com encosto marcado

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-4.jpg`](../../sofas/SOFA-4.jpg)
- **Relação:** catálogo `sofa-chaise` (“Sofá em L”); portfólio `projeto-4`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-009 — Sofá de canto bordô

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-1.jpg`](../../sofas/SOFA-1.jpg)
- **Relação:** portfólio `projeto-1` (sem item de catálogo)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-010 — Banco de canto marrom

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-8.jpg`](../../sofas/SOFA-8.jpg)
- **Relação:** catálogo `banco-canto`; portfólio `projeto-8`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-011 — Assentos sob medida para varanda

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-7.jpg`](../../sofas/SOFA-7.jpg)
- **Relação:** portfólio `projeto-7` (sem item de catálogo)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-012 — Sofá de canto em uma sala

- **Estado:** pendente
- **Fontes:** [`sofas/SOFA-10.jpg`](../../sofas/SOFA-10.jpg)
- **Relação:** catálogo `sofa-retratil`; portfólio `projeto-10`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** O catálogo diz “retrátil”; modelar só o exterior observado, sem mecanismo inventado.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-013 — Poltrona azul de braços retos

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-20.jpg`](../../poltronas/poltronas-20.jpg)
- **Relação:** portfólio `projeto-33` (sem item de catálogo)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-014 — Poltronas azuis e puff capitonê

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-11.jpg`](../../poltronas/poltronas-11.jpg)
- **Relação:** catálogo `poltrona-bracos`; portfólio `projeto-24`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Duas poltronas idênticas = uma geometria com instâncias. O puff é o EXT-034.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-015 — Poltrona marrom de encosto curvo

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-12.jpg`](../../poltronas/poltronas-12.jpg)
- **Relação:** portfólio `projeto-25`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-016 — Poltrona caramelo com encosto marcado

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-15.jpg`](../../poltronas/poltronas-15.jpg)
- **Relação:** portfólio `projeto-28`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-017 — Poltrona com puff verde-acinzentado

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-10.jpg`](../../poltronas/poltronas-10.jpg)
- **Relação:** portfólio `projeto-23`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** O puff é o EXT-033.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-018 — Poltrona e puff bege

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-21.jpg`](../../poltronas/poltronas-21.jpg)
- **Relação:** portfólio `projeto-34`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** O puff é o EXT-035.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-019 — Poltrona de volumes arredondados

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-13.jpg`](../../poltronas/poltronas-13.jpg)
- **Relação:** portfólio `projeto-26`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-020 — Poltronas de estrutura aparente

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-23.jpg`](../../poltronas/poltronas-23.jpg)
- **Relação:** portfólio `projeto-36`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Estrutura aparente = região “estrutura externa aparente”.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-021 — Poltrona de estampa geométrica

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-16.jpg`](../../poltronas/poltronas-16.jpg)
- **Relação:** portfólio `projeto-29`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Estampa = decoração fixa até haver regra de personalização.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-022 — Poltrona com madeira entalhada

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-17.jpg`](../../poltronas/poltronas-17.jpg)
- **Relação:** portfólio `projeto-30`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-023 — Poltrona vermelha com madeira aparente

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-22.jpg`](../../poltronas/poltronas-22.jpg)
- **Relação:** portfólio `projeto-35`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-024 — Cadeira clara com almofadas

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-19.jpg`](../../poltronas/poltronas-19.jpg)
- **Relação:** portfólio `projeto-32`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-025 — Cadeira cinza com estrutura dourada

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-14.jpg`](../../poltronas/poltronas-14.jpg)
- **Relação:** portfólio `projeto-27`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-026 — Cadeira com assento amarelo

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-18.jpg`](../../poltronas/poltronas-18.jpg)
- **Relação:** portfólio `projeto-31`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-027 — Puff retangular verde

- **Estado:** pendente
- **Fontes:** [`pufs/pufs-7.jpg`](../../pufs/pufs-7.jpg)
- **Relação:** portfólio `projeto-11`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-028 — Puffs hexagonais

- **Estado:** pendente
- **Fontes:** [`pufs/pufs-8.jpg`](../../pufs/pufs-8.jpg)
- **Relação:** portfólio `projeto-12`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-029 — Puffs quadrados em conjunto

- **Estado:** pendente
- **Fontes:** [`pufs/pufs-9.jpg`](../../pufs/pufs-9.jpg)
- **Relação:** portfólio `projeto-13`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Possível família com 030/031: inspecionar; não fundir só por serem quadrados.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-030 — Puffs para uma sala de TV

- **Estado:** pendente
- **Fontes:** [`pufs/pufs-10.jpg`](../../pufs/pufs-10.jpg)
- **Relação:** catálogo `puff-quadrado`; portfólio `projeto-14`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Ver nota do EXT-029.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-031 — Puffs vermelhos

- **Estado:** pendente
- **Fontes:** [`pufs/pufs-11.jpg`](../../pufs/pufs-11.jpg)
- **Relação:** portfólio `projeto-15`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Ver nota do EXT-029.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-032 — Puffs com estampas variadas

- **Estado:** pendente
- **Fontes:** [`pufs/pufs-12.jpg`](../../pufs/pufs-12.jpg)
- **Relação:** portfólio `projeto-16`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-033 — Puff coordenado da poltrona verde-acinzentada

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-10.jpg`](../../poltronas/poltronas-10.jpg)
- **Relação:** portfólio `projeto-23` (mesma foto do EXT-017)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Peça própria; não duplicar a poltrona.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-034 — Puff azul/turquesa capitonê

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-11.jpg`](../../poltronas/poltronas-11.jpg)
- **Relação:** catálogo `poltrona-bracos` / portfólio `projeto-24` (mesma foto do EXT-014)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Peça própria; capitonê observado na foto.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-035 — Puff bege com estrutura escura aparente

- **Estado:** pendente
- **Fontes:** [`poltronas/poltronas-21.jpg`](../../poltronas/poltronas-21.jpg)
- **Relação:** portfólio `projeto-34` (mesma foto do EXT-018)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-036 — Cabeceira azul de contorno curvo

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-2.jpg`](../../cabeceiras/cabeceiras-2.jpg)
- **Relação:** catálogo `cabeceira-capitone` (nome exibido “Cabeceira de contorno”); portfólio `projeto-17`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** O id legado diz capitonê, mas a foto mostra contorno curvo + tachas: não inventar capitonê.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-037 — Cabeceira de painéis verticais

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-3.jpg`](../../cabeceiras/cabeceiras-3.jpg)
- **Relação:** portfólio `projeto-18`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-038 — Cabeceira marrom em painéis

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-4.jpg`](../../cabeceiras/cabeceiras-4.jpg)
- **Relação:** portfólio `projeto-19`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-039 — Cabeceira de canto para duas camas

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-5.jpg`](../../cabeceiras/cabeceiras-5.jpg)
- **Relação:** portfólio `projeto-20`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-040 — Cabeceira com painéis horizontais

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-6.jpg`](../../cabeceiras/cabeceiras-6.jpg)
- **Relação:** catálogo `cabeceira-paineis`; portfólio `projeto-21`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-041 — Cabeceira e recamier no quarto

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-7.jpg`](../../cabeceiras/cabeceiras-7.jpg)
- **Relação:** portfólio `projeto-22`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** 041 = cabeceira, 042 = recamier, mesma foto. Sem quarto, colchão ou roupa de cama.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-042 — Recamier do quarto com cabeceira ornamentada

- **Estado:** pendente
- **Fontes:** [`cabeceiras/cabeceiras-7.jpg`](../../cabeceiras/cabeceiras-7.jpg)
- **Relação:** portfólio `projeto-22` (mesma foto do EXT-041)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Ver EXT-041.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.


## B. Complementar

### EXT-043 — Capas para cadeiras

- **Estado:** pendente
- **Fontes:** [`capas/capas-1.jpg`](../../capas/capas-1.jpg)
- **Relação:** portfólio `projeto-37`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-044 — Capas para sofás

- **Estado:** pendente
- **Fontes:** [`capas/capas-2.jpg`](../../capas/capas-2.jpg)
- **Relação:** portfólio `projeto-38`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-045 — Capa para poltrona

- **Estado:** pendente
- **Fontes:** [`capas/capas-3.jpg`](../../capas/capas-3.jpg)
- **Relação:** portfólio `projeto-39`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-046 — Capas para poltronas e puffs

- **Estado:** pendente
- **Fontes:** [`capas/capas-4.jpg`](../../capas/capas-4.jpg)
- **Relação:** portfólio `projeto-40`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-047 — Cortina clara para janela ampla

- **Estado:** pendente
- **Fontes:** [`cortinas/cortinas-1.jpg`](../../cortinas/cortinas-1.jpg)
- **Relação:** portfólio `projeto-41`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-048 — Cortina clara de quarto até o piso

- **Estado:** pendente
- **Fontes:** [`cortinas/cortinas-4.jpg`](../../cortinas/cortinas-4.jpg)
- **Relação:** não registrada em catalog.json nem portfolio.json
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** Não é produto publicado; não anunciar como tal.
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-049 — Cortinas em ambiente comercial

- **Estado:** pendente
- **Fontes:** [`cortinas/cortinas-5.jpg`](../../cortinas/cortinas-5.jpg)
- **Relação:** portfólio `projeto-44`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-050 — Cortina listrada com lambrequim

- **Estado:** pendente
- **Fontes:** [`cortinas/cortinas-6.jpg`](../../cortinas/cortinas-6.jpg)
- **Relação:** catálogo `cortina-com-lambrequim`; portfólio `projeto-45`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.

### EXT-051 — Cortina do teto ao piso

- **Estado:** pendente
- **Fontes:** [`cortinas/cortinas-7.jpg`](../../cortinas/cortinas-7.jpg)
- **Relação:** catálogo `cortina-clara` (nome “Cortina do teto ao piso”)
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** ler a foto, definir regiões e proporções, gerar fonte paramétrica e GLBs, registrar em `data/models-3d.json`.


## C. Registrado, fora da produção

### EXT-052 — Tecido no teto de restaurante

- **Estado:** registrado — fora da produção
- **Fontes:** [`cortinas/cortinas-2.PNG`](../../cortinas/cortinas-2.PNG)
- **Relação:** portfólio `projeto-42`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** nenhuma nesta fila (registro apenas).

### EXT-053 — Tecido claro no teto

- **Estado:** registrado — fora da produção
- **Fontes:** [`cortinas/cortinas-3.jpg`](../../cortinas/cortinas-3.jpg)
- **Relação:** portfólio `projeto-43`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** nenhuma nesta fila (registro apenas).

### EXT-054 — Tecido suspenso entre vigas

- **Estado:** registrado — fora da produção
- **Fontes:** [`cortinas/cortinas-8.jpg`](../../cortinas/cortinas-8.jpg)
- **Relação:** portfólio `projeto-46`
- **Arquivos:** —
- **Revisão:** —
- **Opções reais:** a definir (aplicar a regra de regiões acima)
- **Evidências:** —
- **Limitações:** —
- **Próxima ação:** nenhuma nesta fila (registro apenas).
