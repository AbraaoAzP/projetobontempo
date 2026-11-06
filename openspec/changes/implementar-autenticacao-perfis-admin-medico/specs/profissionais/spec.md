## ADDED Requirements

### Requirement: Restringir administração de médicos e resolver o vínculo autenticado

Admin SHALL poder listar, cadastrar, consultar, editar e excluir médicos conforme as regras de integridade e retenção aprovadas. Médico SHALL NOT acessar o CRUD administrativo de Profissionais nem escolher ou alterar sua identidade profissional no cliente. O Xano SHALL resolver a conta Médico autenticada ao respectivo registro Profissional antes de autorizar agenda, atendimento ou autoria clínica.

Cada conta Médico SHALL estar vinculada a exatamente um Profissional, e cada Profissional SHALL estar vinculado a no máximo uma conta Médico. O provisionamento SHALL ser realizado por Admin autorizado; detalhes de bootstrap, recuperação e desativação deverão ser aprovados antes da alteração do schema.

#### Scenario: Admin administra médicos

- **WHEN** uma conta autenticada Admin solicita uma operação permitida de gerenciamento de médico
- **THEN** o Xano verifica o perfil e aplica as regras de integridade antes de retornar ou alterar dados

#### Scenario: Médico obtém a própria identidade profissional

- **WHEN** uma conta Médico autenticada consulta agenda ou registra atendimento
- **THEN** o backend resolve o registro Profissional vinculado à sessão e ignora qualquer identificador arbitrário enviado pelo cliente

#### Scenario: Médico tenta administrar profissionais

- **WHEN** Médico tenta listar globalmente, cadastrar, editar ou excluir médicos, inclusive por chamada direta à API
- **THEN** o Xano nega a operação sem expor cadastros administrativos nem alterar registros
