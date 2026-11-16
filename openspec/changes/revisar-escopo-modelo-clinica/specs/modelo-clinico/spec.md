## Purpose

Registrar o modelo conceitual aprovado para a clínica, distinguindo decisões do grupo de cardinalidades ainda pendentes e de capacidades que não existem na implementação local.

## ADDED Requirements

### Requirement: Respeitar o escopo funcional e os perfis aprovados

O escopo funcional SHALL contemplar Pacientes, Profissionais exclusivamente médicos, Especialidades médicas, Consultas e Prontuários. A página Início SHALL permanecer como apresentação e navegação, não como módulo clínico adicional.

O sistema SHALL incluir acesso autenticado para os perfis Admin e Médico. A existência de tabela ou endpoints de usuário em artefatos locais não SHALL, por si só, comprovar que autenticação e autorização estão implementadas, nem autorizar a remoção desses recursos.

#### Scenario: Conferir o escopo da versão

- **WHEN** o escopo funcional da clínica é revisado
- **THEN** os cinco módulos, a página Início e os perfis Admin e Médico são identificados, sem apresentar capacidades não implementadas como concluídas

#### Scenario: Encontrar recursos locais de usuário

- **WHEN** a revisão encontra tabela ou endpoints locais de usuário
- **THEN** registra-os como candidatos à reutilização e verifica separadamente se suportam autenticação, perfil e autorização, sem presumir publicação ou removê-los

### Requirement: Autenticar e autorizar usuários no backend

O sistema SHALL autenticar usuários com perfil Admin ou Médico e SHALL aplicar autorização no Xano em cada endpoint protegido. Controles de tela no Streamlit SHALL NOT ser considerados controle de acesso. A implementação poderá reutilizar a tabela `user` se a revisão técnica confirmar que ela suporta o fluxo de autenticação aprovado.

Toda conta de Médico SHALL estar vinculada ao respectivo registro Profissional, e o backend SHALL derivar o médico autorizado da identidade autenticada, não de um identificador profissional livremente informado pelo cliente. A cardinalidade e a restrição de unicidade do vínculo SHALL ser definidas antes de implementar o schema.

#### Scenario: Autorizar operações conforme perfil

- **WHEN** Admin ou Médico solicita uma operação protegida
- **THEN** o Xano verifica autenticação, perfil e escopo do recurso antes de retornar ou alterar dados

#### Scenario: Negar acesso por interface ou endpoint direto

- **WHEN** um usuário Médico tenta acessar função administrativa ou dado de outro médico por URL/API direta
- **THEN** o backend nega a operação independentemente da navegação ou estado visual do Streamlit

#### Scenario: Vincular a conta ao médico correto

- **WHEN** uma conta autenticada com perfil Médico consulta agenda ou registra atendimento
- **THEN** o backend usa o vínculo verificado dessa conta com Profissional e não confia em autoria ou vínculo fornecido apenas no payload

#### Scenario: Reutilizar recurso de usuário após verificação

- **WHEN** a implementação avalia a tabela e os endpoints existentes de `user`
- **THEN** reutiliza-os somente se o fluxo, armazenamento seguro de credenciais, perfil e controles de acesso forem confirmados, sem presumir que endpoints genéricos existentes realizem login

### Requirement: Separar consulta e registro clínico

Uma Consulta SHALL relacionar um paciente, um médico e um status, além dos dados necessários à agenda. Diagnóstico, anotações clínicas e conduta SHALL pertencer a REGISTRO_ATENDIMENTO, não ser duplicados como atributos clínicos de CONSULTA.

Uma consulta apenas agendada SHALL NOT exigir REGISTRO_ATENDIMENTO. Uma consulta realizada poderá gerar no máximo um registro clínico próprio associado à consulta e ao prontuário do paciente. A autoria SHALL identificar o médico autenticado que efetivamente realizou o atendimento; o backend SHALL verificar que a consulta está realizada e pertence ao médico vinculado à conta.

#### Scenario: Manter uma consulta agendada sem registro clínico

- **WHEN** uma consulta está somente agendada
- **THEN** a consulta pode existir sem REGISTRO_ATENDIMENTO

#### Scenario: Registrar atendimento realizado

- **WHEN** uma consulta é realizada e gera um registro clínico
- **THEN** REGISTRO_ATENDIMENTO referencia a consulta e o prontuário do paciente, preserva a autoria do médico que realizou a consulta e contém diagnóstico, anotações clínicas e conduta

#### Scenario: Impedir registro de atendimento não realizado pelo médico autenticado

- **WHEN** um Médico tenta registrar atendimento sem consulta realizada vinculada ao próprio perfil profissional
- **THEN** o backend rejeita a operação e não cria nem atribui autoria ao registro clínico

#### Scenario: Evitar duplicação de conteúdo clínico na consulta

- **WHEN** o modelo de CONSULTA e REGISTRO_ATENDIMENTO é definido
- **THEN** diagnóstico, anotações clínicas e conduta são atribuídos ao registro clínico, sem duplicação em CONSULTA

### Requirement: Preservar o prontuário longitudinal do paciente

Um paciente poderá possuir zero ou um PRONTUARIO, e todo PRONTUARIO SHALL pertencer a exatamente um paciente. O prontuário SHALL organizar os registros de atendimento que formam o histórico clínico do paciente.

A interpretação de que um prontuário pode conter vários REGISTROS_ATENDIMENTO é uma proposta coerente com o histórico, mas a cardinalidade exata deverá ser confirmada pelo grupo antes da implementação.

#### Scenario: Paciente sem prontuário

- **WHEN** um paciente ainda não possui histórico clínico registrado
- **THEN** o paciente pode existir sem PRONTUARIO

#### Scenario: Manter histórico clínico associado ao paciente

- **WHEN** há registros clínicos de um paciente
- **THEN** cada registro pertence ao prontuário desse paciente, sem permitir prontuários duplicados para o mesmo paciente

#### Scenario: Confirmar cardinalidade do prontuário

- **WHEN** a modelagem física é preparada
- **THEN** a cardinalidade de PRONTUARIO para REGISTRO_ATENDIMENTO está explicitamente aprovada, sem transformar a notação ambígua “PRONTUARIO 1 REGISTRO_ATENDIMENTO” em uma restrição presumida

### Requirement: Manter STATUS_CONSULTA no modelo e definir sua integridade

STATUS_CONSULTA SHALL permanecer como entidade conceitual relacionada a CONSULTA. A regra candidata é que cada consulta possua exatamente um status atual e que um status possa ser referenciado por várias consultas; catálogo permitido, transições, histórico de mudanças e obrigatoriedade deverão ser confirmados antes da implementação.

#### Scenario: Preservar a entidade de status

- **WHEN** o modelo conceitual de consultas é revisado
- **THEN** STATUS_CONSULTA continua representado como entidade, e não é descartado em favor de texto livre sem aprovação

#### Scenario: Revisar status e transições

- **WHEN** as regras de status são especificadas para implementação
- **THEN** valores permitidos, status inicial, transições e eventual histórico estão documentados e aprovados

### Requirement: Permitir administração de consultas e consulta do catálogo

Admin SHALL poder listar, cadastrar, consultar, editar e excluir consultas, vinculando cada consulta a paciente, médico, especialidade, data/hora e status válidos. Admin SHALL poder consultar o catálogo de especialidades atendidas. A criação e edição de consulta SHALL validar no backend a existência das referências e o vínculo médico–especialidade.

Esta Change não define campos físicos, duração, transições ou política de conflito ainda não aprovados.

#### Scenario: Administrar consulta

- **WHEN** Admin solicita uma operação permitida de consulta com referências válidas
- **THEN** o backend aplica autorização e regras de integridade antes de retornar ou persistir os dados

#### Scenario: Listar especialidades atendidas

- **WHEN** Admin consulta o catálogo de especialidades
- **THEN** recebe especialidades existentes do backend, sem depender de texto livre duplicado no cadastro do médico

#### Scenario: Negar administração de consulta ao Médico

- **WHEN** Médico tenta criar, editar, excluir ou consultar globalmente consultas
- **THEN** o backend nega a função administrativa e permite somente consultas no escopo autorizado do próprio médico

### Requirement: Confirmar cardinalidades e restrições antes da implementação

Antes de implementar o modelo clínico, a especificação SHALL documentar para cada relação suas cardinalidades mínima e máxima, chaves estrangeiras, unicidade, obrigatoriedade, comportamento de exclusão e consistência transacional.

A relação MÉDICO–ESPECIALIDADE é N:N: um médico pode ter zero ou mais vínculos durante a transição e uma especialidade pode estar vinculada a zero ou mais médicos. Uma consulta só poderá ser agendada com uma especialidade efetivamente vinculada ao médico escolhido. A implementação deverá definir FKs e impedir duplicidade do par médico-especialidade.

#### Scenario: Preservar a cardinalidade aprovada de especialidades

- **WHEN** o modelo físico de médicos e especialidades é proposto
- **THEN** implementa a relação N:N aprovada, permite zero vínculos por médico durante a transição e documenta FKs, unicidade do par e a exigência de vínculo para agendar consultas

#### Scenario: Evitar implementação com integridade indefinida

- **WHEN** ainda há cardinalidade, unicidade, chave estrangeira ou regra de exclusão clínica pendente além da relação N:N Médico–Especialidade aprovada
- **THEN** a implementação dependente dessa regra permanece bloqueada até a decisão ser registrada

### Requirement: Proteger dados clínicos conforme perfil e autoria

Antes de persistir ou disponibilizar dados de prontuário e atendimento por API ou interface, a mudança que implementar essa capacidade SHALL apresentar e obter aprovação para controles de confidencialidade, acesso por perfil, exposição, retenção e auditoria.

O acesso SHALL ser autorizado no backend por perfil, relação com o médico e necessidade funcional. Admin pode listar, cadastrar, editar e excluir prontuários conforme política de retenção e integridade aprovada; Médico pode consultar somente os dados necessários aos próprios atendimentos e registrar prontuário de paciente efetivamente atendido por ele, sem funções administrativas de prontuário. A autoria do registro SHALL ser preservada e não editável pelo cliente. Esta Change especifica o requisito, mas não implementa login, políticas ou controles.

#### Scenario: Planejar acesso a dados clínicos

- **WHEN** uma implementação futura pretende persistir ou expor dados clínicos
- **THEN** os controles de proteção e os riscos decorrentes da ausência de login estão documentados e aprovados antes de habilitar o acesso

#### Scenario: Não presumir exposição pública

- **WHEN** autenticação, autorização ou restrições por médico não foram confirmadas no Xano
- **THEN** as APIs e a integração com dados clínicos permanecem bloqueadas, sem presumir que estejam privadas

#### Scenario: Preservar autoria do registro clínico

- **WHEN** um registro de atendimento é criado pelo Médico autenticado
- **THEN** o backend grava sua autoria a partir da sessão e impede que o cliente substitua ou remova esse vínculo

### Requirement: Apresentar indicadores por perfil

O dashboard Admin SHALL apresentar quantidade de pacientes cadastrados, médicos cadastrados, consultas agendadas, consultas do dia, consultas realizadas e consultas não realizadas. O dashboard Médico SHALL apresentar somente as consultas do próprio médico no dia corrente, seus horários e a quantidade correspondente.

As contagens e filtros SHALL ser obtidos por APIs autorizadas do Xano. A definição do período “hoje”, do fuso horário, do significado de “consultas agendadas” e dos status considerados “não realizadas” SHALL ser aprovada antes da implementação.

#### Scenario: Consultar indicadores administrativos

- **WHEN** Admin abre o dashboard
- **THEN** são apresentados os seis indicadores aprovados a partir de dados autorizados do backend

#### Scenario: Consultar a agenda diária do médico

- **WHEN** Médico abre o dashboard
- **THEN** vê somente suas consultas do dia, com horários, pacientes necessários ao atendimento e quantidade de consultas

#### Scenario: Negar indicadores administrativos ao médico

- **WHEN** Médico tenta consultar métricas globais ou agenda de outro médico
- **THEN** o backend nega ou restringe a resposta ao escopo permitido
