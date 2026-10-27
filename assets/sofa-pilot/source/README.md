# Fonte editavel original do piloto Stanza

Esta branch disponibiliza a fonte original para diagnostico e planejamento. Ela
nao remodela o sofa, nao altera os GLBs, o visualizador, as paginas ou os materiais
publicados e nao deve ser mesclada na main ou implantada automaticamente.

## Procedencia e conteudo

Os arquivos foram copiados sem alteracoes do pacote local `stanza-sofa-pilot`,
criado em 25/10/2026. Os dois GLBs desse pacote foram comparados por SHA-256 com
os GLBs do site na base `4e448e61697b9d9ddc7058f8cdc20f4e8f25b976`: ambos coincidem.
Todos os arquivos copiados tambem foram comparados por SHA-256 com os originais.

- `sofa.blend`: fonte editavel original, nao uma reimportacao do GLB.
- `build_sofa.py`: gerador original de geometria e exportacao, com API do Blender.
- `generate_materials.py`: gerador original das texturas, com NumPy e Pillow.
- `render_export.py`: render de apoio do GLB exportado, usando Blender.
- `embedded-boucle-*.jpg` e `mobile-boucle/`: mapas auxiliares originais.

Aplicam-se os avisos e limites de `../LICENSE-assets.txt` e `../CREDITS.json`.
Nao sao medidas comerciais nem comprovacao da construcao real da Stanza.

## Instrucoes para revisar o diagnostico

1. Busque `origin/codex/sofa-editable-source` e inspecione estes arquivos antes de
   propor importacao dos GLBs ou reconstruir o sofa. Nao faca merge na main.
2. O gerador original indica Blender 5.2. Verifique a versao e a disponibilidade
   real de Blender, NumPy, Pillow e demais dependencias no seu ambiente.
3. Observe que o fonte Blender usa X largura, -Y frente e Z vertical; o exportador
   converte para as convencoes glTF. Nao confunda estes eixos no diagnostico.
4. Abra a fonte sem salvar sobre ela e registre qualquer recurso externo ausente.
   Nao alegue abertura ou validacao sem conseguir executar a ferramenta.
5. Atualize o diagnostico e o plano, inclusive a estrategia de contato das
   almofadas e das camadas, e aguarde aprovacao expressa antes da implementacao.

## Limites desta entrega

Os geradores foram preservados como fontes historicas; nao foram executados ou
revalidados nesta entrega. `build_sofa.py` salva `sofa.blend` e exporta os GLBs;
`render_export.py` gera uma imagem. Nao os execute sobre a base de trabalho antes
da aprovacao, pois podem sobrescrever arquivos existentes. `generate_materials.py`
tambem grava mapas. Use uma copia de trabalho isolada quando houver autorizacao.

Os antigos validadores, empacotadores, `vendor/gltf-validator`, `validation/` e a
demo independente nao foram restaurados. A presenca destes fontes nao acrescenta
scripts npm ao site nem comprova novas capturas, testes 3D ou aprovacao visual.
O fluxo do site continua sendo o da raiz: `npm test` e os scripts Python existentes.
