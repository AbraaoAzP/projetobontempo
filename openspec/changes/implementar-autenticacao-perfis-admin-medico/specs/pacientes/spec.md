## ADDED Requirements

### Requirement: Restringir operações sobre pacientes por perfil autenticado

Admin SHALL poder listar, cadastrar, consultar, editar e excluir pacientes conforme as regras de integridade e retenção aprovadas. Médico SHALL acessar somente os dados mínimos de pacientes necessários aos próprios atendimentos autorizados e SHALL NOT acessar o CRUD administrativo. O Xano SHALL autorizar cada operação; controles visuais do Streamlit SHALL NOT substituir essa verificação.

#### Scenario: Admin administra pacientes

- **WHEN** uma conta autenticada Admin solicita uma operação permitida sobre pacientes
- **THEN** o Xano verifica o perfil e aplica as regras de integridade antes de retornar ou alterar dados

#### Scenario: Médico acessa dados necessários ao próprio atendimento

- **WHEN** Médico autenticado consulta dados de paciente relacionado a atendimento próprio autorizado
- **THEN** o backend retorna somente os campos necessários ao atendimento

#### Scenario: Médico tenta CRUD administrativo ou consulta global

- **WHEN** Médico tenta cadastrar, editar, excluir ou listar globalmente pacientes, inclusive por chamada direta à API
- **THEN** o Xano nega a operação sem expor dados globais ou alterar registros
