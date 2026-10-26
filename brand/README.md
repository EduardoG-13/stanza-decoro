# Kit de marca Stanza Decoro

Abra index.html para consultar o manual e os modelos. O PDF e o Markdown têm o mesmo objetivo: orientar a aplicação da identidade existente.

O aviso de orçamento corresponde ao modelo do backend. O logo automático usa CID e acompanha a mensagem. Os dados da prévia são fictícios; nenhum pedido ou e-mail é criado ao abrir os arquivos.

Confirmação ao cliente e acompanhamento são modelos editáveis. Revise os campos entre colchetes antes de usar. Não existe disparo automático desses modelos nesta entrega.

## Assinatura no Gmail

Abra assinatura-email.html no navegador, selecione apenas a assinatura renderizada e copie. No Gmail, abra Configurações > Ver todas as configurações > Geral > Assinatura, crie uma assinatura da Stanza e cole. Confira os links e a imagem, escolha quando usar e salve. Isso é feito pelo titular; a entrega dos arquivos não altera a assinatura da conta.

A imagem da assinatura usa o endereço HTTPS do logo no domínio oficial. O logo do aviso automático usa imagem incorporada e não depende desse carregamento externo.

## Atualizar com consistência

A referência canônica é data/brand.json, no repositório do site. O backend conserva uma cópia em functions/assets/stanza-brand.json. Nome, contatos, cores e versão devem ser atualizados juntos. O desenho do logo original não é substituído por este kit.

Para regenerar os modelos, compile primeiro o backend separado com --com-email e execute node scripts/gerar-modelos-marca.mjs no site. O script usa o renderizador real do aviso. A geração do PDF está em scripts/gerar-manual-marca.py e requer reportlab e as fontes do ambiente de autoria; não faz parte do build da Netlify.
