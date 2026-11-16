## ADDED Requirements

### Requirement: Restringir profissionais cadastrados a médicos

O escopo do sistema SHALL tratar Profissionais exclusivamente como médicos. O catálogo de Especialidades SHALL relacionar-se aos médicos em cardinalidade N:N. Durante a transição, um médico poderá possuir zero ou mais vínculos; para agendar uma consulta, a especialidade escolhida SHALL estar vinculada ao médico. Os vínculos SHALL referenciar registros existentes e impedir duplicidade do mesmo par.

#### Scenario: Definir o escopo de profissionais

- **WHEN** o cadastro e a consulta de profissionais forem implementados conforme o escopo revisado
- **THEN** cada profissional representa um médico e não uma categoria genérica de prestador

#### Scenario: Associar zero ou mais especialidades durante a transição

- **WHEN** um médico é relacionado a uma ou mais especialidades
- **THEN** cada associação é um vínculo N:N com o catálogo, sem depender de texto livre duplicado, e o médico pode permanecer sem vínculos durante a transição

#### Scenario: Exigir vínculo para agendamento

- **WHEN** uma consulta é agendada para um médico e uma especialidade
- **THEN** a especialidade informada deve estar vinculada ao médico selecionado; mera existência isolada dos registros não basta

### Requirement: Administrar médicos e vincular suas contas

Admin SHALL poder listar, cadastrar, consultar, editar e excluir médicos conforme as regras de integridade e retenção aprovadas. Uma conta autenticada com perfil Médico SHALL estar vinculada ao respectivo registro Profissional, e o backend SHALL usar esse vínculo para limitar consultas, atendimentos e autoria.

Médico SHALL NOT acessar o CRUD administrativo de Profissionais nem escolher ou alterar livremente o próprio vínculo profissional no payload. A cardinalidade e a unicidade do vínculo conta–Profissional, bem como o fluxo de provisionamento, SHALL ser definidos antes da implementação.

#### Scenario: Administrar cadastro de médicos

- **WHEN** Admin solicita uma operação permitida de gerenciamento de médico
- **THEN** o backend autoriza pelo perfil e preserva as referências e regras de integridade

#### Scenario: Restringir o acesso do médico autenticado

- **WHEN** Médico solicita sua agenda ou registra um atendimento
- **THEN** o backend deriva o médico autorizado da conta vinculada e não aceita identidade profissional arbitrária enviada pelo cliente

#### Scenario: Negar administração ao Médico

- **WHEN** Médico tenta listar ou alterar cadastros administrativos de médicos
- **THEN** o backend nega a operação independentemente da interface
