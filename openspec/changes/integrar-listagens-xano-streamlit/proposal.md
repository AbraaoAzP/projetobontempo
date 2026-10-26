## Why

As páginas Pacientes e Profissionais do Streamlit ainda apresentam tabelas vazias e não consomem o Xano. Os endpoints GET de listagem informados pelo grupo retornaram coleções JSON em testes locais; integrar somente essas leituras permitirá exibir os registros de demonstração sem antecipar escrita, autenticação ou os módulos clínicos ainda não implementados.

## What Changes

- Integrar as páginas existentes de Pacientes e Profissionais exclusivamente às respectivas operações HTTP GET de listagem.
- Centralizar configuração, transporte HTTP, timeout e validação de resposta em um cliente Python reutilizável, com URLs completas fornecidas externamente por variável de ambiente.
- Substituir as tabelas vazias por registros realmente recebidos, mantendo as colunas e o layout atuais; apresentar estados explícitos de lista vazia, configuração ausente e falha de integração.
- Evitar chamadas repetidas durante reruns da interface com cache de curta duração e atualização manual.
- Preservar desabilitados os controles de busca e criação; não adicionar cadastro, edição, exclusão, login ou gerenciamento de usuários.
- Manter `especialidade` como texto da resposta atual de Profissionais, sem introduzir relacionamento com catálogo.
- Planejar testes automatizados com respostas HTTP simuladas para sucesso, lista vazia, erro HTTP, timeout, falha de conexão e JSON/formato inesperado.
- Manter as chamadas reais desabilitadas por padrão e exigir habilitação externa explícita somente após confirmação de dados exclusivamente fictícios, acesso adequadamente restrito e autorização do grupo; os GETs já testados sem credenciais não são evidência de segurança.

**Fora do escopo:** chamadas POST, PATCH, PUT ou DELETE; alteração de Xano, tabelas, endpoints, registros ou suas configurações de segurança; autenticação/login; consultas clínicas, prontuários, Especialidades como módulo, relacionamento N, ou outras capacidades da Change `revisar-escopo-modelo-clinica`; mudanças nas cardinalidades ou no modelo de dados.

## Capabilities

### New Capabilities

Nenhuma. O trabalho integra listagens nas capacidades de interface, pacientes e profissionais já especificadas; não cria capacidade clínica nova.

### Modified Capabilities

- `interface-web`: substituir o contrato de páginas somente informativas/tabelas vazias pela apresentação das listagens GET e seus estados de resposta, preservando navegação, identidade visual e ausência de operações de escrita.
- `pacientes`: especificar consumo GET da listagem existente, campos exibidos, lista vazia e erros de leitura.
- `profissionais`: especificar consumo GET da listagem existente, incluindo `especialidade` textual, lista vazia e erros de leitura.

## Impact

- Chamadas reais permanecem desabilitadas por padrão; `XANO_LISTAGENS_ENABLED=true` só poderá ser definido externamente após confirmar dados exclusivamente fictícios, acesso adequadamente restrito e autorização explícita do grupo.
- Futura implementação: `frontend/pages/1_Pacientes.py`, `frontend/pages/2_Profissionais.py`, novo módulo reutilizável sob `frontend/services/`, `frontend/requirements.txt` e `frontend/README.md`; avaliar ajuste mínimo em `frontend/app.py` ou `frontend/ui.py` somente se necessário para consistência visual.
- Configuração: duas variáveis externas com URLs completas dos GETs de Pacientes e Profissionais; nenhum token, segredo ou URL embutida no código versionado.
- Dependência prevista para a implementação: `requests` declarada diretamente caso seja escolhida como cliente HTTP; testes usando biblioteca padrão para simular respostas, sem dados reais.
- Xano: somente os endpoints GET existentes e informados pelo grupo são consumidores; os arquivos locais indicam rotas e projeções de campos equivalentes, mas não comprovam integralmente o ambiente publicado.
- A Change `revisar-escopo-modelo-clinica` foi consultada somente para delimitar conflitos: não será alterada, aplicada, arquivada nem será dependência desta Change. A leitura se limita às listagens atuais de Pacientes e Profissionais, mantendo especialidade textual e adiando os demais módulos.
