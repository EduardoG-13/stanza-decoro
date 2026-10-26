# Acesso aos orçamentos e integração com a oficina

## Onde está cada parte

- Site público: https://stanzadecoro.com.br, hospedado no Netlify e publicado pela main deste repositório.
- Formulário e atendimento privado: Firebase Hosting, site stanza-atendimento-820e4 no projeto Google/Firebase cadastro-820e4.
- Sistema interno: Stanza Gestão, em https://gestao.stanzadecoro.com.br, no projeto Netlify existente ordem-servico.
- Por orientação do usuário, o site público não oferece botão para o painel. O botão “Área da equipe” foi avaliado apenas em prévia e retirado antes da publicação. O redirecionamento público /pedidos-site também foi retirado.
- O acesso fica na aba “Orçamentos do site” do aplicativo interno, com login e autorização explícita. A hospedagem Firebase anterior continua separada; o endereço web.app é um endereço padrão do Google, não um sistema dependente deste computador.

Os dados e fotos do formulário são registrados pelas funções isoladas no backend do projeto cadastro-820e4. As fotos ficam privadas. A publicação do site principal não publica a oficina inteira nem muda os acessos.

## O que já funciona

Receber projeto e fotos, gerar protocolo, avisar no Gmail, consultar por protocolo e situação, abrir fotos com acesso autorizado, atualizar atendimento e registrar histórico. O cadastro de Pedro usa stanzadecoro@gmail.com.

## Incorporação ao Stanza Gestão

1. A atualização do aplicativo parte da main dce186e, preservando as atualizações mais recentes da oficina. Só foram incorporados os módulos de interface necessários da branch antiga codex/pedidos-site.
2. A aba nativa “Orçamentos do site” reutiliza os mesmos endpoints, dados e fotos para contas ativas de administrador/secretária com a permissão explícita pedidos_site. Não existe uma segunda cópia de cada pedido e não foram concedidos novos acessos.
3. Acrescentar uma ação explícita de revisão/conversão para orçamento comercial. Localizar ou confirmar o cliente, mapear peças e informações e manter vínculo com o identificador e protocolo de origem. Repetir a ação deve abrir o registro já criado, sem duplicação.
4. Só após revisão e aprovação comercial, encaminhar o orçamento para a ordem de serviço/produção pelo fluxo existente. Receber formulário não equivale a aprovar preço, prazo ou fabricar.
5. Validar permissões, repetição da conversão e compatibilidade com a oficina atual em ambiente de teste antes de publicar essa integração.

A interface integrada é a primeira etapa. A conversão em orçamento comercial/cliente/OS continua posterior, com revisão e prevenção de duplicações. Login e autorização no servidor são a proteção dos dados; retirar um link público não substitui esses controles. O subdomínio reutiliza a hospedagem existente, sem migração de banco.
