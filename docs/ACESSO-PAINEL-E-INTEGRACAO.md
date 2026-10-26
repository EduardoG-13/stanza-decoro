# Acesso aos orçamentos e integração com a oficina

## Onde está cada parte

- Site público: https://stanzadecoro.com.br, hospedado no Netlify e publicado pela main deste repositório.
- Formulário e atendimento privado: Firebase Hosting, site stanza-atendimento-820e4 no projeto Google/Firebase cadastro-820e4.
- Sistema interno: Stanza Gestão, em https://gestao.stanzadecoro.com.br, no projeto Netlify existente ordem-servico.
- Por orientação do usuário, o site público não oferece botão para o painel. O botão “Área da equipe” foi avaliado apenas em prévia e retirado antes da publicação. O redirecionamento público /pedidos-site também foi retirado.
- O acesso fica em Atendimento → Orçamentos do site no aplicativo interno, com login. Todo administrador ativo tem acesso; secretárias precisam de pedidos_site explícito. Contas inativas, arquivadas ou com login pendente e os demais cargos continuam bloqueados. A hospedagem Firebase anterior continua separada; o endereço web.app é um endereço padrão do Google, não um sistema dependente deste computador.

Os dados e fotos do formulário são registrados pelas funções isoladas no backend do projeto cadastro-820e4. As fotos ficam privadas. A publicação do site principal não publica a oficina inteira nem muda os acessos.

## O que já funciona

Receber projeto e fotos, gerar protocolo, avisar no Gmail, consultar por protocolo e situação, abrir fotos com acesso autorizado, atualizar atendimento e registrar histórico. O cadastro de Pedro usa stanzadecoro@gmail.com.

## Incorporação ao Stanza Gestão

1. A atualização do aplicativo parte da main dce186e, preservando as atualizações mais recentes da oficina. Só foram incorporados os módulos de interface necessários da branch antiga codex/pedidos-site.
2. A aba nativa “Orçamentos do site” reutiliza os mesmos endpoints, dados e fotos. Por decisão da empresa, todos os administradores ativos têm acesso, mesmo em cadastros antigos sem lista de permissões. Secretárias precisam de pedidos_site explícito. Não existe uma segunda cópia de cada pedido.
3. Acrescentar uma ação explícita de revisão/conversão para orçamento comercial. Localizar ou confirmar o cliente, mapear peças e informações e manter vínculo com o identificador e protocolo de origem. Repetir a ação deve abrir o registro já criado, sem duplicação.
4. Só após revisão e aprovação comercial, encaminhar o orçamento para a ordem de serviço/produção pelo fluxo existente. Receber formulário não equivale a aprovar preço, prazo ou fabricar.
5. Validar permissões, repetição da conversão e compatibilidade com a oficina atual em ambiente de teste antes de publicar essa integração.

A interface integrada é a primeira etapa. A conversão em orçamento comercial/cliente/OS continua posterior, com revisão e prevenção de duplicações. Login e autorização no servidor são a proteção dos dados; retirar um link público não substitui esses controles. O subdomínio reutiliza a hospedagem existente, sem migração de banco.

## Conferência final em 26/10/2026

Login real do titular confirmado no novo domínio, com consulta da lista, busca ST-26-0002 e abertura do detalhe. O menu foi agrupado em sete entradas, com somente um grupo aberto por vez. Configurações não oferece mais geração de demonstração. O servidor recusa a criação com failed-precondition; a auditoria encontrou zero registros com os marcadores de demonstração e preservou os 72 registros não marcados.

O projeto Firebase passou a se chamar Stanza Gestao, mantendo o ID cadastro-820e4. O aplicativo usa Stanza Gestão. O repositório interno agora é EduardoG-13/stanza-gestao, com histórico e visibilidade preservados.

As regras de rotas são emitidas também em dist/_redirects a partir de netlify.toml, para acompanhar os arquivos pré-compilados. O endereço público /pedidos-site retorna 404 sem redirecionamento. Referência técnica: https://docs.netlify.com/manage/routing/redirects/overview/.

O kit brand inclui manual da marca, guia de estilos prático em seis páginas, versão HTML, texto editável, tokens CSS e modelos de e-mail. Ele orienta novas personalizações; não representa um redesenho completo das telas legadas da gestão.
