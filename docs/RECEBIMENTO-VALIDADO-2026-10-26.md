# Recebimento validado — 26/10/2026

> Atualização posterior nesta data: Pedro foi ativado pelo titular e os avisos do Gmail estão ativos. O ST-26-0002 foi aceito pelo servidor SMTP em uma tentativa; a chegada à caixa ainda depende de confirmação. Consulte [o estado atual](GMAIL-ATIVO-2026-10-26.md). Os registros abaixo descrevem a etapa original.


O formulário de orçamento está em https://stanza-atendimento-820e4.web.app/orcamento.html. O site principal segue em revisão local.

## Prova de funcionamento

Um envio real, identificado como **Teste técnico Stanza — desconsiderar**, levou os dados do projeto e uma foto até o servidor e recebeu o protocolo **ST-26-0001**.

A conferência posterior encontrou exatamente um registro desse teste e uma foto JPEG de **1600 × 1200**, sem EXIF/GPS e sem token público de download. Os acessos anônimos ao pedido e à foto retornaram **403**. O link de WhatsApp levou o protocolo correto para o número da Stanza.

O registro técnico foi encerrado com histórico, marcado como teste e conservado com a foto. O aviso de e-mail desse teste foi cancelado. Não representa uma solicitação de serviço e não deve disparar uma mensagem futura.

## Proteção e acesso

A ativação precisou habilitar a API pública do Firebase App Check e configurar sua identidade oficial de serviço. A chave de reCAPTCHA está limitada aos dois endereços HTTPS do formulário, com limiar de 0,5. O recebimento exige atestado válido e a origem própria.

A consulta requer login, conta ativa, cargo de administrador ou secretária e a permissão **explícita** pedidos_site. Cargo sem lista de permissões, conta arquivada e login pendente são recusados nos testes. Somente o novo cadastro solicitado para Pedro recebeu essa permissão nesta implantação.

O login real de Pedro na interface privada aguarda definição da senha pelo titular. A verificação sem autenticação e os testes locais não substituem essa etapa.

## Limites da validação

- 8 testes do site aprovados.
- 18 testes locais do recebimento aprovados, em projeto demo exclusivo.
- Um envio real com foto confirmado, com inspeção do registro e da privacidade.
- Navegação e enquadramento conferidos no navegador em tela padrão e larguras de 320 e 390 pixels.
- Celular físico, Safari e Firefox ainda não testados.
- Avisos de Gmail adiados pelo usuário; não foi validado envio ou recebimento de e-mail.
- Conversão em cliente/OS e empreendimentos permanecem em etapas futuras.

As outras 39 funções do projeto e as regras publicadas foram preservadas. O módulo de atendimento e sua página HTTPS têm implantação própria.
