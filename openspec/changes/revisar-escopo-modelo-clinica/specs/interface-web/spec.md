## MODIFIED Requirements

### Requirement: Disponibilizar a navegação principal

A aplicação web SHALL disponibilizar a página Início e navegação para os cinco módulos funcionais aprovados: Pacientes, Profissionais (médicos), Especialidades médicas, Consultas e Prontuários.

#### Scenario: Abrir a aplicação

- **WHEN** uma pessoa acessa a aplicação web após a implementação futura do escopo revisado
- **THEN** a página Início é apresentada e a navegação para os cinco módulos aprovados está disponível

#### Scenario: Navegar entre as páginas

- **WHEN** uma pessoa seleciona um módulo funcional na navegação
- **THEN** a aplicação apresenta o módulo selecionado e mantém a página Início e os demais módulos acessíveis

### Requirement: Distinguir a entrega inicial da integração GET posterior

A entrega inicial SHALL permanecer acessível sem realizar chamadas HTTP ao Xano. Uma Change posterior pode integrar somente listagens GET explicitamente aprovadas, mantendo as chamadas reais desabilitadas por padrão e sem alterar retroativamente o comportamento da entrega inicial. O escopo-alvo revisado acrescenta a navegação para Especialidades, Consultas e Prontuários em Changes futuras.

O acesso às páginas da entrega inicial SHALL NOT depender da configuração ou da disponibilidade das APIs do Xano. A configuração de URLs, sem habilitação externa explícita, SHALL NOT iniciar requisições.

#### Scenario: Acessar a entrega inicial sem integração com o Xano

- **WHEN** uma pessoa inicia a versão atualmente implementada e navega entre Início, Pacientes e Profissionais sem URL base configurada e sem APIs do Xano disponíveis
- **THEN** as páginas da primeira entrega são apresentadas e a navegação funciona sem realizar requisições HTTP ao Xano

#### Scenario: Manter a integração GET posterior desabilitada por padrão

- **WHEN** URLs de listagem estão configuradas, mas a integração posterior não foi explicitamente habilitada
- **THEN** as páginas permanecem acessíveis sem chamadas HTTP ao Xano e informam que a integração está desabilitada

### Requirement: Apresentar páginas informativas dos módulos

As páginas Pacientes, Profissionais, Especialidades, Consultas e Prontuários SHALL identificar o respectivo módulo. A apresentação de cada módulo SHALL refletir apenas funcionalidades efetivamente implementadas e não poderá simular consultas, cadastros ou dados clínicos.

#### Scenario: Abrir Pacientes

- **WHEN** uma pessoa seleciona Pacientes na navegação
- **THEN** vê o título do módulo Pacientes e a indicação de que suas funcionalidades dependem de implementação própria

#### Scenario: Abrir Profissionais

- **WHEN** uma pessoa seleciona Profissionais na navegação
- **THEN** vê o título do módulo Profissionais, restrito ao escopo de médicos, e a indicação de que suas funcionalidades dependem de implementação própria

#### Scenario: Abrir Especialidades, Consultas ou Prontuários

- **WHEN** uma pessoa seleciona Especialidades, Consultas ou Prontuários na navegação após suas páginas serem adicionadas em Changes futuras
- **THEN** vê o título do módulo correspondente e a interface não apresenta funcionalidade inexistente como concluída

#### Scenario: Não simular funcionalidade clínica

- **WHEN** um módulo ainda não possui implementação ou fonte real de dados
- **THEN** a página informa seu estado sem simular registros, consultas ou operações

### Requirement: Preservar o escopo funcional da interface

O sistema SHALL oferecer login para os perfis Admin e Médico e apresentar Início e os cinco módulos funcionais: Pacientes, Profissionais (médicos), Especialidades médicas, Consultas e Prontuários. A navegação e os controles SHALL refletir o perfil autenticado, mas não substituir autorização no backend.

Admin SHALL ter acesso aos módulos e operações administrativas aprovados, incluindo os CRUDs e dashboard descritos nesta Change. Médico SHALL ter acesso à própria agenda diária, aos dados necessários ao atendimento e à criação de registro de prontuário somente de paciente efetivamente atendido por ele; funções administrativas SHALL ser negadas.

Esta Change SHALL limitar-se à revisão de escopo e modelo: não SHALL implementar telas, integração HTTP, CRUD, autenticação ou acesso a dados. A interface final usará APIs HTTP do Xano, nunca acesso direto ao banco. Não SHALL apresentar dados fictícios como se fossem registros reais; ambientes de demonstração SHALL usar exclusivamente dados fictícios.

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** a pessoa inicia a versão atualmente implementada antes da entrega futura de autenticação e navega sem configuração ou disponibilidade do Xano
- **THEN** as páginas existentes permanecem acessíveis sem chamadas HTTP ao Xano, preservando o comportamento da entrega atual

#### Scenario: Conferir o escopo das páginas

- **WHEN** o escopo da interface final é revisado
- **THEN** identifica Início, Pacientes, Profissionais, Especialidades, Consultas e Prontuários, sem oferecer função não implementada como concluída

#### Scenario: Exigir autenticação para módulos protegidos

- **WHEN** uma pessoa tenta abrir um módulo protegido sem sessão autenticada
- **THEN** a interface solicita autenticação e o backend não retorna dados protegidos

#### Scenario: Apresentar módulos conforme o perfil

- **WHEN** Admin ou Médico navega após autenticação
- **THEN** a interface apresenta apenas as funções pertinentes ao perfil, sem considerar ocultação visual como autorização

#### Scenario: Manter os limites arquiteturais

- **WHEN** uma implementação futura integra o frontend ao backend
- **THEN** o frontend usa somente APIs HTTP confirmadas e não acessa diretamente o banco de dados

#### Scenario: Não simular registros reais

- **WHEN** a aplicação é executada em ambiente de demonstração
- **THEN** os registros apresentados são exclusivamente fictícios e não são confundidos com dados reais de pacientes

## ADDED Requirements

### Requirement: Apresentar cards de navegação para o escopo aprovado

A página Início SHALL apresentar a função institucional e permitir alcançar os cinco módulos funcionais aprovados por navegação. A apresentação não SHALL criar módulo funcional de Agenda separado nem exibir números ou dados clínicos fictícios.

#### Scenario: Acessar um módulo pela página Início

- **WHEN** a pessoa seleciona um card ou link de módulo na página Início
- **THEN** a aplicação navega para o módulo existente correspondente, sem simular dados ou operações

#### Scenario: Apresentar somente o escopo aprovado

- **WHEN** a página Início lista os módulos funcionais
- **THEN** apresenta Pacientes, Profissionais, Especialidades, Consultas e Prontuários, mantendo Início como apresentação e sem adicionar Agenda como módulo autônomo

### Requirement: Exibir dashboards de acordo com o perfil

O dashboard de Admin SHALL apresentar as quantidades de pacientes e médicos cadastrados, consultas agendadas, consultas do dia, consultas realizadas e não realizadas. O dashboard de Médico SHALL apresentar somente as consultas próprias do dia, horários e quantidade, além dos dados de paciente necessários aos atendimentos autorizados.

Os dados SHALL ser obtidos por APIs do Xano e as restrições de escopo SHALL ser impostas no backend. A definição do período e dos status usados nos indicadores permanece pendente de decisão.

#### Scenario: Exibir dashboard Admin

- **WHEN** Admin acessa o dashboard
- **THEN** vê os seis indicadores aprovados sem receber autorização baseada apenas na interface

#### Scenario: Exibir dashboard Médico

- **WHEN** Médico acessa o dashboard
- **THEN** vê somente sua agenda do dia, horários e quantidade de consultas

#### Scenario: Restringir consultas fora do perfil

- **WHEN** Médico tenta obter indicadores globais ou a agenda de outro médico
- **THEN** o backend nega o acesso mesmo que a solicitação seja enviada diretamente à API
