# Stanza Decoro — prévia local

Cópia de trabalho na branch codex/site-v2. Os repositórios originais da empresa permanecem preservados. Revisão atual: 25 de outubro de 2026, direção Ateliê editorial.

## Abrir e revisar

No Windows, abra **ABRIR-PREVIA.cmd** nesta pasta. O atalho prepara o site e abre o navegador em http://127.0.0.1:8935/index.html. Mantenha a janela aberta enquanto navega. Se necessário, execute iniciar-previa.ps1 com -Port 8936.

A prévia simples usa a configuração padrão manual, ignorando a configuração temporária de emulador sem apagá-la. Para a demonstração integrada da oficina, use o atalho próprio em ../stanza-oficina.

Para preparar sem abrir servidor:

```powershell
python scripts/build.py --ignore-local-config
python scripts/check_site.py
node --check assets/app.js
node --check assets/home-opening.js
node --check assets/sofa-experience.js
npm test
```

O pacote fica em dist/. Production=false conserva noindex. Nada foi publicado.

## Experiência atual

- Principal editorial, fabricação e reforma, contatos reais e privacidade.
- Onze referências de catálogo, com fichas próprias e busca combinada com famílias.
- Acervo de 46 fotos: descrições revisadas, busca e galeria ampliada com teclado.
- Orçamento com contexto da peça, fotos locais, revisão e continuação no WhatsApp.
- Sofá 3D na abertura: giro automático enquanto está visível; pausa ao sair da tela, ocultar a aba ou reduzir movimentos. Sem controle de expansão por rolagem.
- Personalização em explorar-sofa.html: três tecidos e quatro cores de estudo, câmeras e camadas por controles manuais. A combinação segue ao orçamento como estudo.
- Entrada discreta de conteúdo, com movimento reduzido respeitado. Preferência adicional no rodapé vale para a página atual.

Empreendimentos continuam separados da principal. As fotos originais não foram retocadas ou substituídas por imagens geradas. O ensaio de troca de fundo foi rejeitado na comparação.

## Organização

| Fonte | Responsabilidade |
|---|---|
| site.config.json | Contatos, domínio, agenda e modo de orçamento |
| data/catalog.json e data/portfolio.json | Referências e fotografias |
| data/sofa-pilot.json | Identificadores e nomes permitidos de tecidos e cores |
| pages/ e templates/layout.html | Conteúdo e navegação compartilhada |
| assets/site.css e assets/app.js | Aparência e interações comuns |
| assets/home-opening.js | Cena decorativa, enquadramento e ciclo de movimento |
| assets/sofa-experience.js e .css | Interface de personalização |
| assets/sofa-pilot/ | Modelos, texturas, módulo de visualização e licenças |
| scripts/build.py | Geração dos HTML e cópias WebP |
| scripts/check_site.py | Integridade do pacote, contatos, formulários e hashes dos GLBs |

Edite as fontes e gere novamente. Os HTML na raiz são também atualizados pelo build. As cópias WebP e dist/ são geradas; fotografias originais e arquivos do piloto enviado são conservados.

Os dois GLBs são idênticos aos do pacote recebido. O módulo de visualização ganhou somente opções de cor de fundo/piso para composição no site; a animação e a interface ficam nos adaptadores. INTEGRATION.json separa essa integração dos relatórios originais do piloto. A fonte Blender editável continua no pacote entregue pela outra tarefa.

## Orçamento e limites

O modo padrão prepara um resumo no navegador; fotos são anexadas pela pessoa no WhatsApp. A URL não carrega os dados pessoais do formulário. Isso não confirma recebimento automático.

O registro privado com protocolo foi preparado em ../stanza-oficina. A pesquisa por protocolo foi validada em emulador isolado. E-mail real e conversão em cliente/OS continuam pendentes.

O 3D é ilustrativo: almofadas, proporções e interior ainda precisam de revisão. Não representa tecido em estoque, medida real ou fabricação homologada. Celular físico, Safari e Firefox ainda precisam de conferência.

Relatório atual: ../outputs/IMPLEMENTACAO-STANZA-ETAPA3.md. Próxima revisão do ativo: ../outputs/REVISAO-3D-CAMADAS-E-REFERENCIAS.md.
