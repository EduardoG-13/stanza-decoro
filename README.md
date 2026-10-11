# Stanza Decoro — nova versão local

Implementação iniciada em 11 de outubro de 2026, na branch `codex/site-v2`, a partir da base `4711ea9`. Esta cópia está na pasta da tarefa; o clone original e o sistema da oficina foram preservados.

## Primeira entrega

Página principal editorial com logo real, preto/dourado e verde oliva; páginas de fabricação e reforma; catálogo com oito referências e fichas próprias; portfólio com as 46 imagens existentes, filtros por família; orçamento com validação, prévia local de fotos, revisão e continuação no WhatsApp; contatos e página de privacidade.

Empreendimentos não aparecem na principal nem no menu público. O portal separado e o catálogo 3D fiel permanecem nas etapas próprias dos planos. Não foram adicionados parceiros, depoimentos, preços ou medidas fictícios.

## Abrir a prévia

Com Python e Pillow disponíveis:

No Windows, abra `ABRIR-PREVIA.cmd` na pasta do projeto. Ele prepara os arquivos e abre o navegador. Mantenha a janela aberta enquanto utiliza a prévia; feche ou pressione Ctrl+C para encerrar.

Também é possível iniciar pela linha de comando:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar-previa.ps1
```

Abra `http://127.0.0.1:8935/index.html`. O servidor atende apenas neste computador. Se a porta estiver ocupada, use `-Port 8936` e ajuste o endereço. Mantenha a janela aberta enquanto navega.

Para preparar e conferir sem iniciar servidor:

```powershell
python scripts/build.py
python scripts/check_site.py
node --check assets/app.js
```

O pacote publicável fica em `dist/`. Não foi publicado. A configuração `production: false` mantém a prévia fora da indexação; alterá-la faz parte da preparação do lançamento, após a revisão dos critérios.

## Onde editar

| Arquivo/pasta | Conteúdo |
|---|---|
| `site.config.json` | Marca, contato, domínio, modo de prévia e aviso de agenda com vigência |
| `data/catalog.json` | Referências, descrição, família e foto de origem |
| `data/portfolio.json` | Acervo preservado de 46 referências |
| `pages/` | Conteúdo das páginas |
| `templates/layout.html` | Cabeçalho, rodapé e metadados comuns |
| `assets/site.css` | Identidade, componentes e regras responsivas |
| `assets/app.js` | Menu, filtros e preparação do orçamento |
| `scripts/build.py` | Páginas completas e cópias web das fotografias |

O build também atualiza os HTML na raiz, mantendo a forma de entrada do repositório estático. Edite as fontes acima e gere novamente; não edite os HTML gerados isoladamente. As fotos originais permanecem nas pastas do acervo. Cópias WebP e a pasta `dist/` são geradas e ignoradas pelo Git.

## Orçamento nesta etapa

O formulário prepara um resumo local. A pessoa copia esse resumo, abre o WhatsApp com uma mensagem inicial e anexa as fotos na conversa. A URL de WhatsApp não inclui dados pessoais do formulário. Nenhum protocolo ou confirmação de registro é inventado.

O registro durável, arquivos privados, caixa de pedidos da secretária/dono e notificação automática por e-mail serão implementados no servidor na fase C. Não usar este formulário como prova de recebimento ou de envio automático. A interface e a privacidade devem ser atualizadas junto da ativação desse fluxo.

## Conferências e limites

Sintaxe, geração das páginas, arquivos locais, links, manifesto, identificação dos campos, preservação do acervo e ausência de empreendimento na principal podem ser conferidos pelos scripts. Revisão visual e interação em navegador ainda são necessárias: a ferramenta de navegador não iniciou nesta execução.

Antes da publicação, confirmar individualmente o direito de uso das imagens, revisar fichas com a Stanza, verificar celular/teclado, implementar ou manter explicitamente o canal manual escolhido e conferir a disponibilidade vigente. Reutilização do acervo atual não comprova autoria ou autorização de cada fotografia.

O plano de execução e seus critérios permanecem em `../outputs/planos/00-MAPA-DA-EXECUCAO.md`.
