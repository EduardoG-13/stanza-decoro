# Gmail e acesso do proprietário — 26/10/2026

## Estado confirmado

O titular definiu diretamente a senha do painel e a senha de app do Gmail na configuração privada. Pedro, stanzadecoro@gmail.com, está ativo no Auth e no cadastro de funcionário, com a permissão pedidos_site. Nenhum outro usuário recebeu acesso adicional.

O segredo PEDIDOS_SITE_SMTP foi guardado no Secret Manager. A configuração SMTP foi verificada pelo próprio formulário privado; o valor do segredo não foi consultado pelos diagnósticos, exibido na conversa ou incluído no Git.

A função enviarAvisosPedidosSite foi publicada isoladamente no codebase stanza-atendimento, em southamerica-east1, com a flag de e-mail true e o segredo vinculado. O agendador está habilitado em UTC, com intervalo de cinco minutos. As outras 45 funções conservaram suas datas de atualização e revisões; somente a função de avisos foi acrescentada.

## Envio real

Havia um único aviso pendente: ST-26-0002, com zero tentativas. Foi solicitado um processamento pelo agendador existente, sem criar outro pedido.

O aviso passou a aceito_pelo_servidor, com uma tentativa, em 2026-10-26T14:03:26.898Z. Uma conferência posterior encontrou o mesmo estado e a mesma contagem. O orçamento continua novo e preservado.

O destino é somente stanzadecoro@gmail.com. O aviso contém o resumo e um link autenticado para o pedido. As fotos permanecem privadas, sem anexos ou links públicos no e-mail.

Aceitação SMTP, por si só, não comprova chegada à caixa de entrada. Após essa verificação, o titular confirmou na conversa que recebeu o e-mail ST-26-0002 e pediu uma apresentação mais bem cuidada. A caixa de e-mail não foi acessada pelo agente.

## Validação e limites

- Pacote do backend recompilado com --com-email e entrada/flag conferidas.
- Consulta real da fila e índice correspondente funcionando.
- Função ACTIVE, segredo vinculado e agendador ENABLED confirmados por API.
- Aviso real aceito em uma tentativa, sem novo pedido.
- As outras 45 funções foram comparadas antes/depois e não mudaram.
- Nenhuma regra do banco, módulo da oficina ou página principal foi implantada nesta ativação.
- A chegada à caixa foi confirmada pelo titular. O login real de Pedro pela interface permanece uma verificação independente.
- Os 18 testes locais do módulo foram concluídos em etapa anterior; não representam teste da entrega ao Gmail.

## Próximas etapas

Abrir o pedido no painel com o acesso de Pedro e conferir a experiência em celular real. A publicação do site principal na main foi autorizada pelo usuário. CMS, conversão em cliente/OS, empreendimentos e aprimoramento 3D seguem separados.

## Revisão da identidade

O kit `brand/` documenta logo, paleta, tipografia, fotografia e linguagem. O aviso passa a ter HTML com logo incorporado por CID, resumo organizado, botão autenticado e contatos; a versão em texto permanece disponível. Fotos de clientes continuam privadas no painel. Modelos de confirmação e acompanhamento são bases editáveis, sem novo envio automático ao cliente.
