# Stanza Decoro — versão em revisão

Branch: `codex/site-v2`. Revisão de 26/10/2026. A `main` permanece na versão original.

## Abrir a prévia

No Windows, abra **ABRIR-PREVIA.cmd**. O atalho prepara o site e abre http://127.0.0.1:8935/index.html. A configuração temporária do emulador é ignorada, sem ser apagada.

```powershell
python scripts/build.py --ignore-local-config
python scripts/check_site.py
npm test
```

A página principal continua local e com `noindex`. O formulário e a consulta privada têm publicação separada em https://stanza-atendimento-820e4.web.app.

## O que esta versão contém

- Direção editorial, cores da marca, navegação e contrastes revisados.
- Página “A Stanza”, fabricação e reforma com orientações específicas.
- Guia de tecidos e acabamentos com fotos reais, ligado à principal e às fichas.
- 14 referências de catálogo com informações visíveis da peça e decisões para o projeto.
- 48 fotos de portfólio, busca e ampliação com teclado.
- Duas novas fotos reais de serviços, sem metadados de localização.
- Sofá azul com fundo ajustado aprovado visualmente pelo usuário; original acessível na ficha.
- Abertura 3D com movimento somente enquanto visível e preferência por movimento reduzido. O modelo continua ilustrativo e ainda precisa de revisão.
- Orçamento HTTPS separado, com fotos privadas e protocolo curto. Na prévia, a referência segue ao formulário sem transportar dados pessoais pela URL.

O formulário tem botão de fotos personalizado, cidades por UF, telefone formatado ao digitar e referências com foto e nome. Depois do registro, o WhatsApp recebe o resumo e o protocolo pelo link, sem copiar e colar. Veja [a revisão do orçamento](docs/ORCAMENTO-UX-2026-10-26.md).

Empreendimentos e integração com cliente/OS continuam para etapas posteriores.

A revisão de acesso identifica a conta conectada e explica a falta de autorização. Consulte [o diagnóstico e a revisão do guia](docs/ACESSO-E-ACABAMENTOS-2026-10-26.md).

## Estado do recebimento

As funções de recebimento, consulta, atualização, limpeza e aviso por e-mail estão publicadas em um módulo separado. Os testes locais validam fotos, repetição, permissões, protocolo, conflitos e limpeza.

O envio real foi confirmado com uma foto e protocolo ST-26-0001. O registro e a foto ficaram privados, com acesso anônimo recusado. A ativação incluiu habilitar a API pública do App Check e configurar sua identidade oficial. Veja [a validação do recebimento](docs/RECEBIMENTO-VALIDADO-2026-10-26.md).

Pedro está ativo, após definir a senha diretamente. O Gmail foi configurado e o processador de avisos está ativo a cada cinco minutos. O aviso ST-26-0002 foi aceito pelo servidor na primeira tentativa; a chegada à caixa ainda aguarda confirmação do titular. Veja [Gmail e acesso do proprietário](docs/GMAIL-ATIVO-2026-10-26.md). Senhas não pertencem ao repositório.

## Fontes e geração

- `pages/` e `templates/layout.html`: conteúdo e estrutura.
- `data/catalog.json` e `data/portfolio.json`: peças e fotos.
- `assets/site.css` e `assets/app.js`: visual e interações.
- `assets/quote-redirect.js`: encaminhamento de referências ao formulário HTTPS.
- `assets/quote-fields.js` e `assets/quote-message.js`: campos e mensagem preenchida no WhatsApp.
- `data/cities-br.json`: lista pública do IBGE; atualização explícita com `scripts/update_cities.py`.
- `data/quote-host.json`: configuração pública do formulário, sem senha ou segredo.
- `scripts/build_quote_host.py`: pacote limitado a orçamento, privacidade e consulta privada.
- `firebase.formulario.json`: publicação somente no endereço separado.
- `assets/sofa-pilot/`: piloto recebido, com GLBs preservados e licenças.

Os HTML da raiz são gerados. `dist/`, `.quote-build/` e `dist-formulario/` não são versionados. O build separado não altera as páginas da prévia.

## Histórico e revisão

Consulte [como voltar a uma versão anterior](docs/VERSOES-E-RETORNO.md) e [a revisão individual das imagens](docs/CURADORIA-2026-10-26.md).

Celular físico, Safari e Firefox continuam pendentes. A confirmação de medidas, materiais, autorização das fotos e disponibilidade comercial cabe à Stanza antes do lançamento.
