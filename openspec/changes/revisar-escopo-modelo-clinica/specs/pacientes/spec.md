## MODIFIED Requirements

### Requirement: Remover paciente

O sistema SHALL permitir remover um paciente existente pelo identificador.

A remoção SHALL retirar o cadastro das consultas posteriores.

O sistema não poderá remover outro registro quando o identificador informado não existir.

Quando o paciente possuir consultas, prontuário ou registros clínicos relacionados, a operação SHALL preservar a integridade e não poderá deixar referências órfãs nem apagar histórico clínico por cascata implícita. A política de retenção e o comportamento permitido para esses casos deverão ser aprovados antes de habilitar a remoção com dependências clínicas.

#### Scenario: Remover paciente existente

- **WHEN** uma solicitação válida remove um paciente existente sem consultas ou dados clínicos relacionados
- **THEN** o sistema confirma a remoção e o paciente deixa de aparecer nas consultas posteriores

#### Scenario: Remover paciente inexistente

- **WHEN** uma solicitação de remoção informa um identificador sem paciente correspondente
- **THEN** o sistema retorna um erro de não encontrado

#### Scenario: Preservar integridade do histórico clínico

- **WHEN** um paciente possui consultas, prontuário ou registros clínicos relacionados e a política de retenção ainda não foi aprovada
- **THEN** a remoção não apaga os dados nem deixa referências órfãs, e a operação dependente permanece bloqueada

### Requirement: Restringir operações sobre pacientes por perfil

Admin SHALL poder listar, cadastrar, consultar, editar e excluir pacientes conforme as regras de integridade e retenção aprovadas. Médico SHALL acessar somente os dados de paciente necessários aos atendimentos próprios autorizados e SHALL NOT acessar o CRUD administrativo.

O Xano SHALL autenticar e autorizar cada operação; a visibilidade de páginas ou botões no Streamlit SHALL NOT conceder permissão. A política exata de quais campos clínicos e cadastrais são necessários ao atendimento SHALL ser definida antes da implementação.

#### Scenario: Administrar pacientes

- **WHEN** Admin solicita uma operação permitida de gerenciamento de paciente
- **THEN** o backend valida o perfil e aplica as regras de integridade antes de retornar ou alterar o registro

#### Scenario: Médico consulta dados para atendimento autorizado

- **WHEN** Médico acessa dados de paciente relacionado a atendimento próprio autorizado
- **THEN** o backend retorna somente os dados necessários à funcionalidade do atendimento

#### Scenario: Médico tenta usar CRUD administrativo

- **WHEN** Médico tenta cadastrar, editar, excluir ou listar globalmente pacientes
- **THEN** o backend nega a operação independentemente da interface utilizada
