## 1. Inventário e pré-condições remotas

- [ ] 1.1 Obter por consulta somente de leitura o inventário remoto de tabelas, campos, validações, permissões e métodos/rotas de Pacientes e Profissionais; registrar somente metadados e não copiar valores de registros pessoais. Campos, rotas CRUD e URLs base dos dois grupos foram confirmados; autenticação, contagem/existência de registros e algumas validações ainda não foram verificadas.
- [ ] 1.2 Comparar o inventário remoto com `xano/table/` e `xano/api/`, incluindo obrigatoriedade de telefone, comportamento do PATCH, projeção das respostas e autenticação; verificar que cada discrepância está documentada antes de escolher um contrato Python. No código local, `validar_telefone_paciente` retorna booleano `true` ou interrompe entradas inválidas; o POST/PATCH de Pacientes não verificava o retorno e os endpoints de Profissionais esperavam incorretamente um campo `.valid`. Os quatro endpoints locais foram alinhados ao retorno booleano, mas a correspondência com o estado publicado continua pendente de inventário autorizado.
- [ ] 1.3 Confirmar que tabelas e campos atuais atendem ao CRUD pretendido sem migração; se faltar schema ou for necessária alteração de autenticação/permissão, bloquear esse trabalho e exigir Change e autorização específicas antes de continuar.
- [x] 1.4 Registrar o bloqueio de publicação (`v1` live e `allow_push: false`) e confirmar que nenhum `workspace push` amplo ou contorno de permissão é usado; publicação continua bloqueada até autorização explícita.

## 2. Cliente HTTP Xano e testes simulados

- [x] 2.1 Implementar serviço HTTP reutilizável para coleção, item, criação, edição e exclusão usando as rotas e parâmetros confirmados de Pacientes e Profissionais; validar respostas incluindo `{"success": true}` em DELETE, com timeout e erros explícitos verificados por contratos simulados.
- [x] 2.2 Configurar as URLs base confirmadas por recurso com possibilidade de sobrescrita externa; não presumir autenticação, manter credenciais fora do repositório, e falhar explicitamente para base URL vazia ou inválida.
- [x] 2.3 Adicionar testes com transporte simulado para GET de coleção e item, POST, PATCH, DELETE, erros HTTP 400, 401, 403, 404, 409 e 500, timeout, conexão, JSON inválido e payload/resposta incompatíveis; verificar que nenhum teste acessa a rede ou usa dados reais.
- [x] 2.4 Verificar que o cliente envia somente os campos fornecidos em PATCH e preserva valores opcionais vazios explicitamente; comportamento remoto permanece condicionado à confirmação do contrato publicado.
- [x] 2.5 Alinhar os endpoints XanoScript locais de Pacientes e Profissionais ao retorno booleano da função `validar_telefone_paciente`; validar sintaxe dos cinco arquivos relacionados com o Xano Developer MCP e confirmar que nenhuma publicação remota foi executada.

## 3. Integrar as páginas de Pacientes e Profissionais

- [x] 3.1 Integrar a página de Pacientes ao CRUD Xano confirmado para listar, consultar, cadastrar, editar e excluir; exigir confirmação de exclusão, atualizar a lista após operações, validar formulários e verificar erros sem fallback SQLite.
- [x] 3.2 Integrar a página de Profissionais ao CRUD Xano confirmado para listar, consultar, cadastrar, editar e excluir, preservando a especialidade textual; verificar sucesso, validação de telefone e tratamento de HTTP 429 sem repetição da escrita nem fallback SQLite.
- [x] 3.3 Exigir confirmação explícita antes de DELETE em ambas as páginas e verificar que a operação não é chamada antes da confirmação.
- [x] 3.4 Preservar SQLite para Especialidades e Consultas enquanto esses módulos não forem migrados; executar testes existentes e verificar que continuam funcionando.
- [x] 3.5 Documentar que Changes subsequentes deverão migrar Especialidades e Consultas ao Xano e então remover o serviço, a inicialização e as dependências SQLite; verificar que a arquitetura final não prevê suporte permanente a dois bancos e que o arquivo de dados local permanece sem remoção implícita.
- [x] 3.6 Completar na página de Pacientes o cadastro, a consulta individual, a edição e a exclusão por endpoints Xano confirmados; manter chamadas desabilitadas por padrão atrás de `XANO_API_ENABLED` e testar somente com mocks nesta etapa.

## 4. Documentar e validar a integração local

- [x] 4.1 Documentar configuração externa, operações disponíveis, estados de erro, tratamento de HTTP 429, validação local de telefone e o caráter transitório do SQLite; verificar que as instruções não contêm credenciais.
- [x] 4.2 Executar a suíte de testes automatizados do frontend sem rede, usando mocks; verificar CRUD, validações, confirmação de exclusão, HTTP 429 sem repetição, configuração, erros e testes dos módulos SQLite restantes. Verificação local nesta etapa: 53 testes passaram.
- [x] 4.3 Revisar `git diff` e `git status`; verificar que alterações não incluem mudanças em arquivos visuais preexistentes, dados locais SQLite ou recursos Xano remotos.

## 5. Verificação remota autorizada

- [x] 5.1 Validar somente leitura das coleções de Pacientes e Profissionais pelas APIs reais, confirmar status HTTP, resposta em lista compatível com o cliente e carregamento das páginas Streamlit sem erros; registrar apenas metadados e quantidade, sem expor dados pessoais nem executar operações de escrita.
- [ ] 5.2 Após autorização específica, validar o CRUD remoto com registros sintéticos criados para o teste; verificar listagem, leitura, criação e edição sem alterar registros preexistentes. Validação parcial em 2026-10-27: Pacientes ID 19 passou POST/GET/PATCH e confirmação por GET (HTTP 200); Profissionais POST respondeu HTTP 429, sem ID confirmado, então a sequência foi interrompida e não repetida. Nesta etapa não foi feita nova escrita; o 429 não permite concluir se houve persistência. Evidência manual relatada pelo usuário em 2026-11-06: CREATE, READ/listagem, UPDATE e DELETE de Pacientes e Profissionais aprovados na aplicação com Xano habilitado. O relato não confirma que os registros eram sintéticos nem que registros preexistentes foram preservados; portanto, não comprova todos os critérios desta tarefa.
- [ ] 5.3 Testar DELETE somente com o identificador retornado pela criação sintética do próprio teste; verificar que nenhum registro preexistente foi removido. O relato manual do usuário em 2026-11-06 informa DELETE aprovado para ambos os módulos, mas não confirma a origem dos IDs nem que nenhum registro preexistente foi removido; tarefa permanece pendente.
- [x] 5.4 Os endpoints CRUD necessários foram informados como existentes no Xano; nenhuma publicação foi necessária ou executada. Se a verificação posterior identificar endpoint ausente, interromper até autorização explícita e mecanismo seletivo compatível com `allow_push: false`, sem publicação ampla.

## 6. Remoção final da persistência legada

- [ ] 6.1 Após a migração e validação de Especialidades e Consultas em Changes próprias, remover inicialização, serviço e dependências SQLite; verificar que todas as páginas usam exclusivamente APIs HTTP do Xano e que a suíte não depende de SQLite.
- [ ] 6.2 Manter o arquivo de banco SQLite preexistente intacto até decisão explícita sobre retenção ou migração e verificar que a remoção de código não o apaga.

## Evidências manuais relatadas pelo usuário

Em 2026-11-06, o usuário informou que executou manualmente os testes na aplicação Streamlit, com a integração Xano habilitada, com os seguintes resultados:

| Módulo | CREATE | READ/listagem | UPDATE | DELETE |
|---|---|---|---|---|
| Pacientes | Aprovado | Aprovado | Aprovado | Aprovado |
| Profissionais | Aprovado | Aprovado | Aprovado | Aprovado |

O usuário também informou que o HTTP 429 observado anteriormente não impediu o cadastro nesta execução. Estes resultados são evidências relatadas pelo usuário, não testes automatizados nem uma execução ou verificação independente nesta etapa. Não foram incluídos IDs, dados pessoais, credenciais ou detalhes de registros.

O relato não comprova que os arquivos XanoScript locais foram publicados, que a implementação publicada corresponde a esses arquivos ou que controles de segurança e autenticação foram verificados.

## Pendências e limites da evidência

- **Segurança e autorização:** inventariar e confirmar as permissões e proteções dos endpoints no backend. Os testes CRUD relatados não demonstram autorização adequada nem acesso restrito.
- **Autenticação:** confirmar o mecanismo de autenticação exigido e a autorização aplicável aos endpoints; isso também permanece pendente na Change `implementar-autenticacao-perfis-admin-medico`.
- **Publicação XanoScript:** não houve publicação nesta etapa. A validação local de sintaxe registrada em 2.5 não comprova publicação ou estado equivalente no Xano live; a publicação continua bloqueada conforme 1.4.
- **Validações remotas adicionais:** confirmar que os testes usaram registros sintéticos criados para esse fim, que as leituras e alterações não afetaram registros preexistentes e que os DELETE usaram exclusivamente IDs dessas criações; concluir o inventário e a comparação remotos das tarefas 1.1–1.3.
- **Migração legada:** as tarefas 6.1–6.2 dependem da migração de Especialidades e Consultas em Changes próprias e da decisão explícita sobre retenção do arquivo SQLite.
