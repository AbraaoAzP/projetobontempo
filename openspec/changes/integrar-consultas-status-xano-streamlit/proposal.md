## Why

A página Consultas ainda grava e consulta dados exclusivamente no SQLite, enquanto o Xano já disponibiliza endpoints de Consulta e Status da Consulta. Integrar a agenda ao backend permitirá usar os registros reais de Pacientes, Profissionais, Especialidades e Status sem sincronizar nem alterar os dados locais existentes.

## What Changes

- Integrar o CRUD da página Consultas às operações já existentes e confirmadas do Xano, sem criar, publicar ou alterar endpoints remotos.
- Carregar do Xano pacientes, profissionais, especialidades e status para os formulários; confirmar como a relação profissional-especialidade é fornecida antes de filtrar opções.
- Preservar validações de data, horário, referências, associação de especialidade e conflitos, respeitando o contrato e as garantias implementadas no backend.
- Apresentar estados claros de sucesso, lista vazia, configuração ausente, erro HTTP, transporte e resposta incompatível.
- Manter as gravações remotas desabilitadas em testes automatizados e usar transporte HTTP simulado. Não enviar POST, PATCH ou DELETE reais sem autorização específica.
- Manter o SQLite, seus dados e a inicialização necessária ao Dashboard; não migrar nem remover o banco nesta mudança.

**Fora do escopo:** alterar tabelas, endpoints, permissões ou configurações remotas do Xano; migrar ou excluir dados SQLite; modificar o Dashboard ou autenticação Admin/Médico, exceto correções estritamente necessárias para evitar erros.

## Capabilities

### New Capabilities

- `consultas`: operações de Consulta pela API Xano, catálogo de Status da Consulta, seleção de entidades relacionadas e validações da agenda na interface.

### Modified Capabilities

- `interface-web`: permitir que a página Consultas use contratos Xano confirmados, preservando Dashboard, autenticação fora de escopo e as demais páginas.

## Impact

- Código potencialmente afetado: `frontend/pages/4_Consultas.py`, `frontend/services/xano.py` e testes da página/cliente Xano.
- Configuração: variáveis externas para URLs e habilitação das APIs de Consultas e Status, definidas somente após confirmação dos contratos.
- Contratos identificados no painel estão registrados em `design.md`: campos da tabela Consulta, GET da coleção e por ID, inputs e rotas de POST/PATCH/DELETE, timestamp Unix em milissegundos, referências não nulas e `observacoes` anulável. Permanecem pendentes a relação Profissional–Especialidade, a semântica de nulo/vazio no PATCH e as garantias do backend sobre referências, status e conflitos. As escritas da página continuam desabilitadas até a validação final.
- O Dashboard e `frontend/services/database.py` continuam dependendo do SQLite; a remoção do banco exige etapa posterior e não é parte desta integração.
