# Conteúdo mais direto, letras maiores e cortinas no catálogo

## Critério visual

Retirar rótulos que apenas decoram ou repetem o título: “01 / Estudo de forma”, numerações soltas, frases pequenas sobre cada modelo e chamadas em caixa alta acima de quase todas as seções. Conservar nomes, navegação, filtros, informações do projeto, orientação de envio, contato e avisos que ajudam na decisão.

Texto de apoio usa pelo menos 14 px na base de 16 px; corpo e campos, em geral 16 px; descrições de cartões e links, 15 px. As regras responsivas não encolhem as letras para forçar conteúdo a caber. O cabeçalho foi ajustado em 320 px mantendo controles legíveis. Essa regra orienta a aplicação do guia de estilos existente no site público.

Títulos identificam o conteúdo da página com mais clareza. As fichas mostram o nome da peça diretamente. A legenda de foto com fundo ajustado e a imagem original foram mantidas; legendas genéricas repetindo “acervo Stanza” foram retiradas. Fotografias e arquivos do modelo 3D não foram alterados. O JavaScript da abertura apenas deixou de escrever a legenda removida.

## Catálogo e projetos

Catálogo: modelos de referência para começar uma encomenda e pedir orçamento. São 16 referências, com filtro de cortinas e duas fichas: Cortina do teto ao piso e Cortina com lambrequim.

Projetos: 48 fotografias de peças e ambientes do acervo. Mostram o trabalho em contexto. A mesma peça pode aparecer nas duas áreas; cada uma atende a uma tarefa diferente. As introduções explicam a diferença e apontam para a outra área.

As novas fichas usam fotografias originais existentes no repositório, inspecionadas visualmente. Não foram inventadas composição do tecido, medidas, isolamento de luz ou preços. Instalação e materiais ficam sujeitos à avaliação.

## Orçamento

O formulário identifica Cortina como tipo de peça e recebe nome e foto da referência selecionada. O domínio do recebimento foi atualizado antes da interface, sem alterar outras funções. A associação das referências foi verificada no pacote HTTPS; miniaturas permanecem leves e sem metadados de localização.

## Verificação

- 28 páginas do site conferidas: links, arquivos, IDs, contatos, dimensões, rotas e indexação.
- 13 testes do site e 17 de domínio/integração do atendimento aprovados.
- Associação das 16 referências de catálogo e 48 de projetos ao nome, tipo e miniatura conferida.
- Navegação em 390 px pelas páginas inicial, catálogo, projetos, empresa, fabricação, reforma, materiais, privacidade, simulador e fichas; leitura computada sem os rótulos decorativos, sem textos principais/de apoio abaixo de 14 px e sem transbordamento horizontal nessas páginas.
- Cabeçalho da página inicial conferido em 320 px, sem quebra da ação de orçamento para outra linha. Formulário de cortina conferido em 390 px, com tipo Cortina e referência correta, sem envio real.

Publicação do site acompanha a main. O formulário fica no Firebase Hosting separado, site stanza-atendimento-820e4. Alterações de enumeração do recebimento são publicadas seletivamente pelo checkout stanza-oficina; não publicar a oficina inteira. A branch codex/site-v2 e os marcos anteriores foram preservados.
