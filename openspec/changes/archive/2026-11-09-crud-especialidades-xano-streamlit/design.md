# Design: CRUD de Especialidades no Xano existente

## Contexto

O usuário confirmou em 2026-11-09 o grupo Xano existente e autorizou integrar
seus endpoints públicos ao Streamlit, usando somente dados fictícios. A página
de Especialidades deixa de usar o catálogo SQLite. Consultas continua
dependendo do serviço, schema, inicialização e dados SQLite, que permanecem
intocados.

## Contrato informado

| Operação | Método e rota | Entrada conhecida |
|---|---|---|
| Listar | `GET /especialidade` | Nenhuma |
| Consultar | `GET /especialidade/{especialidade_id}` | ID inteiro positivo |
| Cadastrar | `POST /especialidade` | `{ "nome": string }` |
| Atualizar | `PATCH /especialidade/{especialidade_id}` | `{ "nome": string }` |
| Excluir | `DELETE /especialidade/{especialidade_id}` | ID inteiro positivo |

Base URL: `https://x8ki-letl-twmt.n7.xano.io/api:Cv9TB_MS`. O usuário informou
os campos de tabela `id` (inteiro), `created_at` (timestamp) e `nome` (texto).
A leitura real autorizada de `GET /especialidade` respondeu HTTP 200 com uma
lista vazia. A forma das respostas de registro e das operações de escrita ainda
precisa de validação controlada.

## Decisões

### Integrar o grupo existente sem modificar Xano

Usar somente as rotas fornecidas pelo usuário. Não criar, alterar, publicar ou
validar scripts Xano nesta Change; os XanoScripts locais existentes permanecem
intocados. Os endpoints indicados como `Public` serão chamados sem exigir login
ou perfis nesta etapa. Isso não comprova a segurança do backend; a política de
segurança do Xano não será modificada.

### Validar e apresentar respostas reais

Usar `frontend/services/xano.py` como único cliente HTTP. Validar a lista e os
registros em JSON, exigindo `id` inteiro positivo e `nome` textual não vazio.
Enviar somente `nome` nas gravações e não expor `created_at` na interface. Uma
resposta incompatível, erro HTTP ou falha de transporte deve aparecer como erro,
nunca como lista vazia ou sucesso.

O nome é obrigatório e passa por trim. A tela impede duplicidade após
normalização sem distinção de caixa contra o catálogo carregado; essa
verificação de frontend não garante unicidade concorrente. Se o Xano rejeitar
uma gravação, a interface apresenta o erro sem sucesso fictício.

### Exigir confirmação na exclusão

DELETE só é enviado para o ID exibido após confirmação explícita. A API pode
rejeitar exclusões por referência; nesse caso, a interface comunica o erro e
preserva o estado. Nenhum mecanismo de cascata é implementado pelo frontend.

### Habilitar a integração com possibilidade de bloqueio

As flags `XANO_ESPECIALIDADES_API_ENABLED` e
`XANO_ESPECIALIDADES_WRITE_ENABLED` ficam habilitadas por padrão conforme
autorização do usuário e podem ser definidas como `false`. A base URL permanece
sobrescrevível por `XANO_ESPECIALIDADES_BASE_URL`. Nenhuma credencial é incluída
no código.

### Separar testes locais e escritas remotas

Testes automatizados usam mocks e não enviam mutações ao Xano. Para uma
validação real, apresentar primeiro ao usuário um plano com POST, PATCH e
DELETE, usando apenas uma especialidade sintética criada para o teste; aguardar
autorização antes de executar qualquer uma dessas chamadas. Não alterar nem
excluir registros preexistentes.

## Fora de escopo e preservação

- Não alterar `frontend/app.py`, Dashboard, Consultas, Prontuários ou outras
  Changes.
- Não modificar autenticação, perfis, políticas de segurança ou configurações
  do Xano.
- Não publicar scripts, executar push, sincronizar ou migrar dados.
- Manter SQLite para Consultas e não copiá-lo para o catálogo Xano.

## Riscos

- A designação `Public` permite acesso sem autenticação e não comprova
  autorização efetiva; limitar a interface ao uso acadêmico com dados
  fictícios.
- O GET observado retornou catálogo vazio; o contrato do registro não pôde ser
  confirmado até uma especialidade existir.
- A unicidade concorrente e integridade referencial dependem do Xano e não são
  garantidas por validação no navegador.
- Consultas continuará usando um catálogo SQLite separado até uma Change
  própria.

## Verificação

1. Validar rotas e parsing com transporte mockado.
2. Cobrir com `AppTest` estados de leitura, validação, criação, edição,
   confirmação de exclusão e erros; mocks impedem mutações remotas nos testes.
3. Executar um GET real sem registrar valores de registros.
4. Apresentar plano e aguardar autorização antes de validar POST, PATCH ou
   DELETE reais com registro exclusivamente fictício.
5. Executar testes, validar OpenSpec strict, revisar o diff e preparar commit
   seletivo; arquivar somente após completar as validações autorizadas.
