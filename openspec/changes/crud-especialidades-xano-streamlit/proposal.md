## Why

A tela atual de Especialidades permite cadastrar e listar registros no SQLite, enquanto a arquitetura aprovada prevê o Xano como backend e o serviço local ainda não oferece consulta individual, edição ou exclusão. Migrar este módulo agora completa o primeiro escopo ADMIN FIRST sem remover a persistência SQLite de que Consultas ainda depende.

## What Changes

- Migrar o gerenciamento de Especialidades para a API HTTP do Xano: listar, consultar por identificador, cadastrar, editar e excluir, com validações, confirmação de exclusão e erros explícitos.
- Reutilizar e preparar o cliente/serviços HTTP tipados existentes, sem criar um segundo transporte por página e sem fallback para SQLite quando a integração estiver indisponível.
- Preservar a regra de nome não vazio e unicidade após trim e normalização sem distinção de caixa; impedir exclusão em cascata e tratar referências existentes conforme contrato confirmado.
- Não copiar registros SQLite para o Xano nesta Change. Consultas continuará usando seu catálogo local e, temporariamente, não verá as alterações feitas no catálogo Xano; a convergência depende de Change posterior para Consultas.
- Confirmar, por inventário somente de leitura autorizado, os campos, métodos, rotas, parâmetros, formatos de resposta, validações e controles de acesso de Especialidades antes de implementar chamadas ou contratos XanoScript. Os arquivos locais atuais não contêm esse contrato.
- Como o inventário não encontrou tabelas relacionais para profissionais e consultas, o endpoint DELETE local será preparado em modo bloqueado e não removerá registros até que essas relações e a proteção referencial estejam implementadas e verificadas.
- Manter o SQLite e sua inicialização enquanto Consultas depender dele. Não alterar `frontend/app.py`, não migrar dados automaticamente e não remover o arquivo de dados.
- Manter a integração real desabilitada até a confirmação dos contratos, da configuração externa e da autorização para o ambiente de destino. Não alterar `v1 live`, não executar escritas remotas nem publicar XanoScript sem autorização explícita.

**Fora do escopo:** login, separação de perfis Admin/Médico, vínculo de Especialidades com Profissionais, migração de Consultas, reconciliação automática de dados SQLite, remoção global do SQLite e publicação ou escrita no Xano nesta etapa.

## Capabilities

### New Capabilities

- `especialidades`: operações completas de gerenciamento do catálogo, validação, integridade e integração pelo Streamlit com APIs Xano confirmadas.

### Modified Capabilities

- `interface-web`: ampliar a interface Streamlit com a página funcional de Especialidades e seus estados de carregamento, vazio, sucesso, configuração pendente e erro.

## Impact

- Frontend: `frontend/pages/3_Especialidades.py`; evolução do serviço em `frontend/services/`; testes automatizados e documentação de configuração do frontend.
- SQLite: `frontend/services/database.py` continua atendendo Consultas e seus relacionamentos; sua inicialização e o banco local serão preservados nesta mudança.
- Xano local: atualmente há schemas e APIs versionados para Pacientes, Profissionais e autenticação, mas não foram encontrados schema ou endpoints de Especialidades. Qualquer contrato local novo depende da confirmação do destino e da autorização explícita.
- Dependências: reutilizar `requests` e os padrões de testes simulados já disponíveis; nenhuma dependência nova é prevista.
- A Change `modelar-especialidades-consultas-xano` fornece contexto conceitual para o catálogo, mas também inclui Consultas e não implementa APIs nem CRUD. Esta Change separa a migração da interface e do serviço de Especialidades.
