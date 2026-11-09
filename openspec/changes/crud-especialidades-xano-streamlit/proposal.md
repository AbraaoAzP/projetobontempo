## Why

A tela atual de Especialidades permite cadastrar e listar registros no SQLite, enquanto a arquitetura aprovada prevê o Xano como backend e o serviço local ainda não oferece consulta individual, edição ou exclusão. Migrar este módulo agora completa o primeiro escopo ADMIN FIRST sem remover a persistência SQLite de que Consultas ainda depende.

## What Changes

- Migrar o gerenciamento de Especialidades para a API HTTP do Xano: listar, consultar por identificador, cadastrar, editar e excluir, com validações, confirmação de exclusão e erros explícitos.
- Reutilizar e preparar o cliente/serviços HTTP tipados existentes, sem criar um segundo transporte por página e sem fallback para SQLite quando a integração estiver indisponível.
- Validar nome obrigatório, trim e duplicidade contra o catálogo carregado; apresentar erros do Xano sem presumir unicidade concorrente ou proteção referencial ainda não confirmadas.
- Não copiar registros SQLite para o Xano nesta Change. Consultas continuará usando seu catálogo local e, temporariamente, não verá as alterações feitas no catálogo Xano; a convergência depende de Change posterior para Consultas.
- Integrar as rotas existentes informadas pelo usuário: GET/POST `/especialidade` e GET/PATCH/DELETE `/especialidade/{especialidade_id}`. Uma leitura real somente GET respondeu HTTP 200 com uma lista vazia.
- Habilitar a integração real, sem autenticação nesta etapa, com flags externas de opt-out. A indicação `Public` não será tratada como prova de autorização segura; não alterar a configuração de segurança do Xano.
- Antes de qualquer validação remota por POST, PATCH ou DELETE, apresentar o plano e obter autorização; usar somente registro fictício criado especificamente para esse teste e preservar registros preexistentes.
- Manter o SQLite e sua inicialização enquanto Consultas depender dele. Não alterar `frontend/app.py`, Dashboard, Consultas, Prontuários ou outras Changes.
- Não modificar nem publicar XanoScript, não alterar dados remotos sem a autorização indicada, não fazer push Git.

**Fora do escopo:** login, separação de perfis Admin/Médico, vínculo de Especialidades com Profissionais, migração de Consultas, reconciliação automática de dados SQLite, remoção global do SQLite e publicação ou escrita no Xano nesta etapa.

## Capabilities

### New Capabilities

- `especialidades`: operações completas de gerenciamento do catálogo, validação, integridade e integração pelo Streamlit com APIs Xano confirmadas.

### Modified Capabilities

- `interface-web`: ampliar a interface Streamlit com a página funcional de Especialidades e seus estados de carregamento, vazio, sucesso, configuração pendente e erro.

## Impact

- Frontend: `frontend/pages/3_Especialidades.py`; evolução do serviço em `frontend/services/`; testes automatizados e documentação de configuração do frontend.
- SQLite: `frontend/services/database.py` continua atendendo Consultas e seus relacionamentos; sua inicialização e o banco local serão preservados nesta mudança.
- Xano: usar o grupo existente informado pelo usuário; nenhum script ou configuração de segurança do Xano é alterado por esta Change.
- Dependências: reutilizar `requests` e os padrões de testes simulados já disponíveis; nenhuma dependência nova é prevista.
- A Change `modelar-especialidades-consultas-xano` fornece contexto conceitual para o catálogo, mas também inclui Consultas e não implementa APIs nem CRUD. Esta Change separa a migração da interface e do serviço de Especialidades.
