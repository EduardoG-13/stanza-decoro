# Versões preservadas da Stanza

26/10/2026.

## Pontos de retorno

| Identificação | O que preserva |
|---|---|
| `main` / `4711ea9` | Site original encontrado no repositório |
| `backup/site-original-2026-10-26` | Marcador fixo da versão original, independente de mudanças futuras na main |
| `checkpoint/site-v2-antes-curadoria-2026-10-26` / `1a83eda` | Nova abertura antes desta rodada de fotos e do formulário HTTPS |
| `codex/site-v2` | Continuação da versão nova, com commits de cada etapa |

A branch nova pode receber ajustes sem modificar a main. Os marcadores anteriores não devem ser movidos ou apagados.

## Ver a versão original

No GitHub, abra o marcador `backup/site-original-2026-10-26` ou o commit `4711ea9`. É possível baixar o ZIP dessa versão sem modificar o trabalho atual.

Para gerar uma cópia ZIP pelo Git:

```powershell
git archive --format=zip --output=../stanza-original.zip backup/site-original-2026-10-26
```

## Quando a nova versão for aprovada

Revisar as mudanças da branch, concluir as pendências comerciais e de envio e fazer o merge na main com um commit de merge. A main não foi atualizada nesta etapa.

Depois de um merge, uma eventual volta deve usar um novo commit de reversão. Isso conserva os registros e permite reaplicar melhorias depois. Não usar reset forçado ou reescrita de histórico como procedimento de retorno.

## Site e dados são preservados separadamente

Voltar o visual do site não apaga pedidos, fotos privadas ou usuários do atendimento. O formulário HTTPS e suas funções têm publicação própria; mudanças de código não devem apagar os dados recebidos.

O backend complementar está na branch `codex/pedidos-site` de `fabric-service-tracker`. Essa cópia é anterior a atualizações recentes da oficina. Publicações desta funcionalidade usam somente `firebase.atendimento.json`; não substituir a oficina inteira por esta cópia.
