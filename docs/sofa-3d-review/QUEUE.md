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

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`sofas/SOFA-3.jpg`](../../sofas/SOFA-3.jpg)
- **Relação:** catálogo `sofa-modular`; portfólio `projeto-3` (única peça com esta foto; IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-modular-01/` — `source/build.py` (fonte de verdade), `source/stanza-modular-01.blend`, `models/stanza-modular-01.glb`, `models/stanza-modular-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas `assets/models-3d/materials/sarja/` e `decor-losango/`; registro `data/models-3d.json` (`stanza-modular-01`)
- **Revisão:** 1.0.0 (somente exterior) · principal 51 448 tri / 3,17 MB · móvel 24 092 tri / 1,11 MB
- **Opções reais:** corpo (braços, 3 blocos de assento, 3 blocos de encosto) — tecidos `sarja` (inicial, novo), `linen`, `boucle`, `velvet` × cores `grafite-quente` (inicial, nova), `grafite`, `gelo`, `areia`, `oliva`, `terracota`. Sete almofadas decorativas (4 lisas azuis, 3 estampadas): fixas. Sem contraste nem estrutura visível.
- **Evidências:** [ext003-sofa-modular.md](ext003-sofa-modular.md), imagens `images/ext003_*.jpg`, validação `validation/ext003/` (glTF-Validator 0/0/0/0, comportamento 74/74, máscaras 0 px nas decorativas, contatos)
- **Prévia:** `/explorar-sofa.html?modelo=stanza-modular-01`; produto `/modelos/sofa-modular.html` com "Ver em 3D"
- **Limitações:** vista única (costas e lateral esquerda inferidas); escala com assento fixado em 0,40 m (peça resulta 4,24 × 1,17 m); espessura do encosto assumida; sarja e `grafite-quente` (`#545050`) são estimativas visuais; estampa das almofadas é releitura procedural; rolagem de 3° da foto não reproduzida; validação só headless.
- **Próxima ação:** revisão visual pela Stanza; ajustes prováveis: caimento/sobreposição das almofadas e tom do tecido sob a luz da foto.

### EXT-004 — Sofá claro de dois assentos

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`acervo/sofa-dois-assentos.webp`](../../acervo/sofa-dois-assentos.webp)
- **Relação:** catálogo `sofa-dois-assentos`; portfólio `projeto-47` (a mesma foto ilustra a página "Sobre"; mesma peça, sem entrada nova; IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-two-seat-01/` — `source/build.py`, `source/stanza-two-seat-01.blend`, `models/stanza-two-seat-01.glb`, `models/stanza-two-seat-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas `assets/models-3d/materials/linho-rustico/` e `decor-quadrados/`; registro `data/models-3d.json` (`stanza-two-seat-01`)
- **Revisão:** 1.0.0 (somente exterior) · principal 39 188 tri / 3,72 MB · móvel 15 976 tri / 0,95 MB
- **Opções reais:** corpo (braços, base, encosto, almofadas de assento e encosto) — tecidos `linho-rustico` (inicial, novo), `linen`, `boucle`, `velvet` × cores `cru` (inicial, nova), `gelo`, `areia`, `grafite`, `oliva`, `terracota`. Almofada lombar estampada: fixa. Sem contraste nem estrutura visível.
- **Evidências:** [ext004-sofa-dois-assentos.md](ext004-sofa-dois-assentos.md), imagens `images/ext004_*.jpg`, validação `validation/ext004/` (glTF-Validator 0/0/0/0, comportamento 75/75, máscaras 0 px, contatos)
- **Prévia:** `/explorar-sofa.html?modelo=stanza-two-seat-01`; produto `/modelos/sofa-dois-assentos.html` com "Ver em 3D"
- **Limitações:** vista única; assento fixado em 0,45 m; profundidade apoiada num ponto; `linho-rustico`/`cru` (`#e2ddd2`) estimados; desenho da lombar é releitura procedural; validação só headless.
- **Próxima ação:** revisão visual pela Stanza; ajustes prováveis: caimento da lombar e enchimento do topo das almofadas de encosto.

### EXT-005 — Sofá cinza com vivo claro

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`acervo/sofa-com-vivo.webp`](../../acervo/sofa-com-vivo.webp)
- **Relação:** catálogo `sofa-com-vivo`; portfólio `projeto-48` (a mesma foto ilustra a página de tecidos e um card da home; mesma peça, sem entrada nova; IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-piped-01/` — `source/build.py`, `source/stanza-piped-01.blend`, `models/stanza-piped-01.glb`, `models/stanza-piped-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas `assets/models-3d/materials/sarja/` (tinta `cinza-malva`); registro `data/models-3d.json` (`stanza-piped-01`)
- **Revisão:** 1.1.0 (somente exterior; almofadas cheias com compressão local nos contatos) · principal 67 752 tri / 3,58 MB · móvel 29 232 tri / 1,21 MB
- **Opções reais:** corpo (braços, base, encosto, almofadas de assento e encosto) — tecidos `sarja` (inicial), `linen`, `velvet`, `boucle` × cores `cinza-malva` (inicial, nova), `grafite`, `gelo`, `areia`, `oliva`, `terracota`. Vivo claro (`piping_light`, região `contrast`): fixo. Sem decorativas nem estrutura visível.
- **Evidências:** 1.1.0: [cushions-fix-2026-10.md](cushions-fix-2026-10.md), imagens `images/cushfix_ext005_*.jpg`, validação `validation/cushfix/ext005/` (glTF-Validator 0/0/0/0, comportamento 76/76, vivo 0 px com corpo claro/escuro, contatos das almofadas ≤ 3,8 mm main / 4,6 mm mobile, vivos 0 mm em outras peças); 1.0.0: [ext005-sofa-com-vivo.md](ext005-sofa-com-vivo.md), `images/ext005_*.jpg`, `validation/ext005/`
- **Prévia:** `/explorar-sofa.html?modelo=stanza-piped-01`; produto `/modelos/sofa-com-vivo.html` com "Ver em 3D"
- **Limitações:** vista única grande-angular com rolagem; assento fixado em 0,45 m e profundidade restrita a 1,0 m (largura 3,46 m é a mais incerta do lote); `cinza-malva` (`#8a8286`) estimado sob sol forte; encostos rígidos com coroa (caimento real mais mole); sem pés confirmados; validação só headless.
- **Próxima ação:** revisão visual pela Stanza; confirmar largura/profundidade reais e se há pés rebaixados; ajustes prováveis: caimento dos encostos.

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

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`sofas/SOFA-9.png`](../../sofas/SOFA-9.png), [`sofas/SOFA-9.2.png`](../../sofas/SOFA-9.2.png) (mesmo ponto de vista: SOFA-9.2 = SOFA-9 recortada)
- **Relação:** catálogo `sofa-curvo`; portfólio `projeto-9` (IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-curved-arm-01/` — `source/build.py` (fonte de verdade), `source/stanza-curved-arm-01.blend`, `models/stanza-curved-arm-01.glb`, `models/stanza-curved-arm-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas velvet e wood-wenge por referência; registro `data/models-3d.json` (`stanza-curved-arm-01`)
- **Revisão:** 1.0.0 (somente exterior) · principal 57 852 tri / 2,81 MB · móvel 21 456 tri / 1,01 MB
- **Opções reais:** corpo (casco, braços curvos, encosto, colchão matelassê) — tecidos `velvet` (inicial), `linen`, `boucle`, `sarja` × cores `musgo` (inicial, nova), `oliva`, `grafite`, `gelo`, `areia`, `terracota`. Seis almofadas soltas = decoração fixa; pés/travessa de madeira = estrutura fixa; sem contraste.
- **Evidências:** [ext007-sofa-curvo.md](ext007-sofa-curvo.md), imagens `images/ext007_*.jpg`, validação `validation/ext007/` (glTF-Validator 0/0/0/0, comportamento 79/79, máscaras, contatos)
- **Prévia:** `/explorar-sofa.html?modelo=stanza-curved-arm-01`; produto `/modelos/sofa-curvo.html` com "Ver em 3D"
- **Limitações:** um só ponto de vista real; profundidade assumida 0,95 m; `musgo` (`#6b6534`) e veludo estimados; madeira em wood-wenge (foto mais avermelhada); pés recuados ~7 cm; matelassê e almofadas menos estufados que na foto; colchão sobre os braços tratado como corpo (dúvida registrada); validação só headless.
- **Próxima ação:** revisão visual pela Stanza; se aprovado, marcar `approved`.

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

- **Estado:** tecnicamente validado – revisão visual pendente (poltrona); puff = EXT-034, **pendente / fora do escopo**
- **Fontes:** [`poltronas/poltronas-11.jpg`](../../poltronas/poltronas-11.jpg)
- **Relação:** catálogo `poltrona-bracos`; portfólio `projeto-24` (mesma foto; IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-armchair-01/` — `source/build.py` (fonte de verdade), `source/stanza-armchair-01.blend`, `models/stanza-armchair-01.glb`, `models/stanza-armchair-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas `assets/sofa-pilot/materials/velvet/` (por referência); registro `data/models-3d.json` (`stanza-armchair-01`)
- **Revisão:** 1.0.0 (somente exterior; UMA poltrona — a foto mostra duas idênticas) · principal 41 776 tri / 2,01 MB · móvel 16 080 tri / 0,63 MB
- **Opções reais:** corpo (concha braços+encosto, base tambor, almofada de assento com vivos do próprio tecido) — tecidos `velvet` (inicial), `linen`, `boucle`, `sarja` × cores `petroleo` (inicial, nova), `grafite`, `gelo`, `areia`, `oliva`, `terracota`. Sem decorativas, contrastes ou estrutura visível.
- **Evidências:** [ext014-poltrona-bracos.md](ext014-poltrona-bracos.md), imagens `images/ext014_*.jpg`, validação `validation/ext014/` (glTF-Validator 0/0/0/0, comportamento 77/77, máscaras, contatos)
- **Prévia:** `/explorar-sofa.html?modelo=stanza-armchair-01`; produto `/modelos/poltrona-bracos.html` com "Ver em 3D"
- **Limitações:** um único ângulo; medidas estimadas com assento 0,44 m; veludo e `petroleo` (`#0e5668`) são estimativas visuais (foto subexposta); base giratória oculta não modelada; abas do topo do encosto e interior do encosto mais plano da foto só aproximados; validação só headless. O puff capitonê (EXT-034) continua pendente.
- **Próxima ação:** revisão visual pela Stanza; se aprovado, marcar `approved`. Puff: EXT-034.

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

- **Estado:** tecnicamente validado – revisão visual pendente
- **Fontes:** [`cabeceiras/cabeceiras-6.jpg`](../../cabeceiras/cabeceiras-6.jpg)
- **Relação:** catálogo `cabeceira-paineis`; portfólio `projeto-21` (mesma foto; IDs preservados)
- **Arquivos:** `assets/models-3d/stanza-headboard-panels-01/` — `source/build.py` (fonte de verdade), `source/stanza-headboard-panels-01.blend`, `models/stanza-headboard-panels-01.glb`, `models/stanza-headboard-panels-01-mobile.glb`, `previews/poster.jpg`, `manifest.json`; mapas `assets/sofa-pilot/materials/velvet/` (por referência); registro `data/models-3d.json` (`stanza-headboard-panels-01`, câmeras photo/front/side/detail próprias)
- **Revisão:** 1.0.0 (somente exterior; só a composição estofada de parede: cabeceira central de 3 painéis, 4 faixas verticais, 4 painéis laterais) · principal 42 928 tri / 2,09 MB · móvel 17 136 tri / 0,69 MB
- **Opções reais:** corpo (todos os painéis) — tecidos `velvet` (inicial), `linen`, `sarja`, `boucle` × cores `areia` (inicial, reutilizada), `cru`, `gelo`, `grafite`, `oliva`, `terracota`. Sem decorativas, contrastes ou estrutura visível.
- **Evidências:** [ext040-cabeceira-paineis.md](ext040-cabeceira-paineis.md), imagens `images/ext040_*.jpg`, validação `validation/ext040/` (glTF-Validator 0/0/0/0, comportamento 78/78, máscaras, contatos)
- **Prévia:** `/explorar-sofa.html?modelo=stanza-headboard-panels-01`; produto `/modelos/cabeceira-paineis.html` com "Ver em 3D"
- **Limitações:** um único ângulo; escala pela cabeceira central fixada em 1,60 m (queen, premissa); composição tratada como simétrica, painéis laterais de 0,60 m estimados; recortes de interruptores não modelados; canais um pouco mais abertos que na foto; sem parede no visualizador; validação só headless.
- **Próxima ação:** revisão visual pela Stanza; se aprovado, marcar `approved`.

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
