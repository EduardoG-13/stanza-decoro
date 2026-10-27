# Stanza Decoro — site e atendimento

Desenvolvimento: `codex/site-v2`. Publicação: `main`, ligada ao projeto Netlify `stanzadecoro` e ao domínio https://stanzadecoro.com.br. Revisão de 26/10/2026. A versão original está preservada em um marcador fixo.

## Abrir a prévia

No Windows, abra **ABRIR-PREVIA.cmd**. O atalho prepara o site e abre http://127.0.0.1:8935/index.html. A configuração temporária do emulador é ignorada, sem ser apagada.

```powershell
python scripts/build.py --ignore-local-config
python scripts/check_site.py
npm test
```

A prévia local usa `noindex`. O Netlify gera `dist/` com `--production`, habilita a indexação e verifica os arquivos antes de publicar. O formulário e a consulta privada têm publicação separada em https://stanza-atendimento-820e4.web.app.

## O que esta versão contém

- Direção editorial, cores da marca, navegação e contrastes revisados.
- Página “A Stanza”, fabricação e reforma com orientações específicas.
- Guia de tecidos e acabamentos com fotos reais, ligado à principal e às fichas.
- 14 referências de catálogo com informações visíveis da peça e decisões para o projeto.
- 48 fotos de portfólio, busca e ampliação com teclado.
- Duas novas fotos reais de serviços, sem metadados de localização.
- Sofá azul com fundo ajustado aprovado visualmente pelo usuário; original acessível na ficha.
- Rotação 3D decorativa do exterior do sofá na página inicial, somente enquanto visível e respeitando movimento reduzido. Sem abertura de camadas ou estrutura interna desde a revisão 2.0.0. Fila de modelos 3D: `docs/sofa-3d-review/QUEUE.md`. Pipeline dos modelos da coleção (registro `data/models-3d.json`, `assets/models-3d/`, `scripts/models3d/`): `docs/sofa-3d-review/models3d-pipeline.md`; estudo EXT-002 em `/explorar-sofa.html?modelo=stanza-straight-01`.
- Orçamento HTTPS separado, com fotos privadas e protocolo curto. Na prévia, a referência segue ao formulário sem transportar dados pessoais pela URL.

O formulário tem botão de fotos personalizado, cidades por UF, telefone formatado ao digitar e referências com foto e nome. Depois do registro, o WhatsApp recebe o resumo e o protocolo pelo link, sem copiar e colar. Veja [a revisão do orçamento](docs/ORCAMENTO-UX-2026-10-26.md).

Empreendimentos e integração com cliente/OS continuam para etapas posteriores.

A revisão de acesso identifica a conta conectada e explica a falta de autorização. Consulte [o diagnóstico e a revisão do guia](docs/ACESSO-E-ACABAMENTOS-2026-10-26.md).

## Estado do recebimento

As funções de recebimento, consulta, atualização, limpeza e aviso por e-mail estão publicadas em um módulo separado. Os testes locais validam fotos, repetição, permissões, protocolo, conflitos e limpeza.

O envio real foi confirmado com uma foto e protocolo ST-26-0001. O registro e a foto ficaram privados, com acesso anônimo recusado. A ativação incluiu habilitar a API pública do App Check e configurar sua identidade oficial. Veja [a validação do recebimento](docs/RECEBIMENTO-VALIDADO-2026-10-26.md).

Pedro está ativo, após definir a senha diretamente. O Gmail foi configurado e o processador de avisos está ativo a cada cinco minutos. O aviso ST-26-0002 foi aceito pelo servidor na primeira tentativa e o titular confirmou o recebimento. Veja [Gmail e acesso do proprietário](docs/GMAIL-ATIVO-2026-10-26.md). Senhas não pertencem ao repositório.

## Identidade e comunicação

O [kit de marca](brand/README.md) inclui manual em PDF e Markdown, cores e fontes, modelos de e-mail e assinatura para inserir no Gmail. O logo original preto e dourado foi preservado. `data/brand.json` concentra a referência de identidade e contatos.

O aviso interno possui HTML com logo incorporado e versão em texto. Confirmação ao cliente e acompanhamento são modelos editáveis; não ativam novos envios automáticos. A assinatura não é instalada automaticamente na conta do Gmail.

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

Os HTML da raiz são gerados. `dist/`, `dist-producao/`, `.quote-build/` e `dist-formulario/` não são versionados. O build separado não altera as páginas da prévia. `netlify.toml` define o build oficial, redirecionamentos e cabeçalhos.

## Histórico e revisão

Consulte [como voltar a uma versão anterior](docs/VERSOES-E-RETORNO.md) e [a revisão individual das imagens](docs/CURADORIA-2026-10-26.md).

Celular físico, Safari e Firefox continuam pendentes. Medidas, materiais e disponibilidade comercial são confirmados no atendimento; as imagens do catálogo são referências para encomenda.
