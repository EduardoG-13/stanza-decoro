# Revisão do orçamento — 26/10/2026

## Comportamento

O formulário HTTPS registra dados e fotos no atendimento privado antes de oferecer a continuação no WhatsApp. O link leva o resumo completo e o protocolo preenchidos. A pessoa confirma a mensagem no WhatsApp; as fotos já recebidas ficam no painel e não são anexadas pelo link.

Na conferência, a ação principal é enviar o projeto. Após o recibo válido, aparecem a confirmação e o botão de WhatsApp. Em falha, a página mantém o mesmo envio para tentar novamente e oferece ajuda pelo WhatsApp, sem afirmar que houve registro. Copiar e colar deixou de fazer parte do fluxo.

O painel em /pedidos-site exige conta ativa e permissão explícita. O cadastro solicitado de Pedro permanece inativo até a definição da senha pelo titular. Avisos de Gmail continuam adiados. O registro do formulário independe do Gmail.

## Campos e fotos

- Estado antecede cidade. A lista do IBGE é distribuída em 27 arquivos locais, carregando somente a UF selecionada. A consulta atual retornou 5.571 municípios. Trocar a UF limpa a cidade anterior; a digitação manual permanece disponível caso a lista não carregue ou a localidade não conste.
- O telefone recebe parênteses, espaço e hífen durante a digitação. Aceita fixo e celular com DDD e colagem com +55; não descarta excesso de dígitos silenciosamente.
- O botão Selecionar fotos usa as cores da Stanza, ícone vetorial, foco de teclado e contagem atualizada ao selecionar ou remover.
- Referências do catálogo e do portfólio mostram foto, nome e tipo corretos no formulário. Trocar a referência conserva as informações já preenchidas e as fotos.
- As fichas mostram a proporção natural das fotos. O sofá verde mantém o arquivo e o fundo originais.

Fonte e atualização: [API oficial de localidades do IBGE](https://servicodados.ibge.gov.br/api/docs/localidades). O comando python scripts/update_cities.py atualiza a cópia; compilação e uso normal não consultam o IBGE nem enviam contatos a esse serviço.

## Evidência e limites

- 13 testes automatizados do site: campos, montagem de mensagem, repetição/recibo e encaminhamento seguro.
- Verificação das 24 páginas e das associações de 14 referências de catálogo e 48 do portfólio. As 49 miniaturas somam 776 KB; a maior tem 29 KB e a página carrega somente a selecionada.
- Navegador: digitação, colagem com +55 e exclusão junto aos parênteses; SP com 645 cidades e RJ com 92, removendo a cidade anterior; seleção/remoção de foto pelo botão personalizado; larguras de 320 e 390 pixels sem transbordamento horizontal.
- Simulação local de interface: uma identidade, uma foto e uma conclusão. Antes do recibo, WhatsApp oculto; depois, resumo e protocolo no link. A simulação não criou pedido em produção e não comprova armazenamento remoto.
- Falha de conexão simulada: recebimento não confirmado, botão de nova tentativa e ajuda pelo WhatsApp com resumo; nenhuma confirmação falsa.
- O recebimento real com foto já foi validado na etapa anterior como ST-26-0001, encerrado como teste. Consulte RECEBIMENTO-VALIDADO-2026-10-26.md. Esta revisão não altera o backend nem suas permissões.
- Mensagem real no aplicativo WhatsApp, celular físico, Safari, Firefox e login do titular continuam fora desta validação.

O site principal permanece em revisão local e noindex. A publicação desta revisão abrange somente o endereço separado de orçamento, privacidade e atendimento.
