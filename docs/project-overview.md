# Project Overview — Sistema de Gestão de Consultório

## 1. Visão geral

Este projeto acadêmico é desenvolvido para a disciplina de Innovation Labs, ministrada pelo professor Bontempo.

O sistema tem como objetivo apoiar a gestão de um consultório, com acesso autenticado para Admin e Médico e funcionalidades para pacientes, médicos, especialidades, consultas e prontuários.

O escopo aprovado não significa que essas funcionalidades já estejam implementadas. O estado atual e as lacunas são descritos na seção “Estado atual e evolução”.

## 2. Problema

Um consultório precisa organizar de forma clara os pacientes, profissionais, dias de atendimento, horários disponíveis e agendamentos.

Quando essas informações não estão centralizadas, podem ocorrer problemas como conflitos de horários, dificuldade para visualizar a disponibilidade dos profissionais e falhas no controle dos atendimentos.

O sistema busca organizar essas informações e facilitar o gerenciamento da agenda do consultório.

## 3. Objetivos

O objetivo principal é desenvolver um sistema para organizar a administração do consultório e apoiar os atendimentos médicos, protegendo dados por perfil.

Entre os objetivos iniciais estão:

- autenticar usuários com perfil Admin ou Médico;
- administrar pacientes, médicos, especialidades, consultas e prontuários;
- apresentar indicadores administrativos e a agenda diária própria de cada médico;
- vincular consultas a paciente, médico, especialidade, data, horário e status;
- registrar atendimentos com autoria médica preservada;
- validar integridade e conflitos de agenda no backend.

## 4. Público-alvo / usuários

Os perfis de acesso aprovados são:

- **Admin:** administra pacientes, médicos, especialidades, consultas e prontuários, e consulta o dashboard administrativo.
- **Médico:** consulta somente sua agenda diária e os dados necessários aos próprios atendimentos; registra prontuário de paciente efetivamente atendido por ele; não acessa funções administrativas.

Pacientes são entidades atendidas, não perfis de acesso desta versão.

## 5. Escopo

O escopo-alvo aprovado inclui autenticação e os cinco módulos funcionais: Pacientes, Profissionais exclusivamente médicos, Especialidades, Consultas e Prontuários. A página Início é apresentação e navegação, não um módulo clínico. A implementação é incremental; capacidades ainda não disponíveis não devem ser apresentadas como prontas.

## 6. Principais funcionalidades

Requisitos funcionais aprovados para evolução:

- Login para Admin e Médico, com autenticação e autorização impostas pelo Xano.
- Admin: dashboard com quantidades de pacientes e médicos, consultas agendadas, consultas do dia, realizadas e não realizadas; CRUD de pacientes, médicos, consultas e prontuários; consulta ao catálogo de especialidades.
- Médico: dashboard somente com as próprias consultas do dia, horários e quantidade; acesso apenas aos dados necessários ao atendimento; registro clínico somente para paciente efetivamente atendido por ele.
- Consultas vinculadas a paciente, médico, especialidade, data/hora e status; a especialidade deve pertencer ao médico selecionado.
- Prontuários vinculados aos pacientes; registros de atendimento devem preservar médico autor e vínculo com atendimento conforme a modelagem aprovada.
- Os exemplos de demonstração devem utilizar exclusivamente dados fictícios.

## 7. Requisitos e restrições importantes

O backend deverá validar autorização por perfil, identidade do médico, referências e regras de negócio. A interface Streamlit não é mecanismo de segurança.

As consultas deverão ter referências válidas e evitar conflitos conforme regras definidas no backend. Os valores de status, transições e a definição exata de “não realizadas” ainda precisam de decisão. A relação médico–especialidade é N:N; durante a transição, médicos podem não ter vínculo, mas o agendamento exige especialidade vinculada. O campo textual legado não deverá ser convertido automaticamente.

Médicos só poderão registrar atendimento quando o backend confirmar que foram autores do atendimento realizado. Conteúdo clínico deve ficar no registro de atendimento, não duplicado na consulta. As cardinalidades ainda não aprovadas e as regras de retenção/exclusão permanecem pendentes.

## 8. Arquitetura tecnológica

O projeto utilizará o ambiente de desenvolvimento definido para a disciplina.

As principais ferramentas utilizadas serão:

- Visual Studio Code;
- Git;
- GitHub;
- Python;
- Streamlit;
- Xano;
- Xano CLI;
- XanoScript;
- GitHub Copilot;
- Xano Developer MCP;
- OpenSpec.

O Xano é o backend e banco definitivo. O Streamlit será desenvolvido em Python e consumirá somente APIs HTTP do Xano; o frontend não acessará diretamente o banco. Autenticação e autorização por perfil, incluindo limites de dados por médico, deverão ser verificadas nos endpoints do backend.

A URL base das APIs e eventuais credenciais deverão ser fornecidas por configuração externa, sem serem fixadas no código ou em arquivos versionados. Antes de habilitar chamadas, deverão ser confirmadas a URL base e as exigências de autenticação do ambiente.

SQLite é uma persistência local legada e temporária ainda usada por Especialidades e Consultas. A remoção de sua inicialização e serviço depende da migração e validação desses módulos no Xano. O arquivo local não deve ser apagado implicitamente. A integração existente de Pacientes e Profissionais também depende da verificação de autorização no backend antes de ser habilitada para uso integrado.

O projeto será versionado utilizando Git e GitHub.

Para executar o frontend localmente, consulte `frontend/README.md`.

## 9. Princípios de desenvolvimento

O projeto será desenvolvido de forma incremental.

As funcionalidades serão analisadas, especificadas, implementadas e revisadas em etapas menores.

Sempre que possível, as mudanças relevantes deverão ser planejadas antes da implementação.

O desenvolvimento deverá utilizar o OpenSpec para organizar e documentar as mudanças do projeto.

## 10. Segurança e integridade

O sistema deve preservar confidencialidade e integridade de dados pessoais e clínicos. O Xano deve autenticar e autorizar cada operação; ocultar páginas ou controles não é suficiente. Admin acessa funções administrativas; Médico acessa somente sua agenda e dados necessários a atendimentos autorizados. Autoria clínica deve ser derivada da identidade autenticada e preservada. Não se deve habilitar dados clínicos até verificar políticas de acesso, exposição, auditoria e retenção.

Utilizar exclusivamente dados fictícios de demonstração. A configuração externa e o conteúdo versionado não devem expor credenciais, tokens ou dados pessoais.

## 11. Estado atual e evolução

O repositório possui uma interface Streamlit multipágina. Pacientes e Profissionais têm páginas CRUD conectadas a endpoints HTTP do Xano; a implementação não comprova autorização Admin/Médico. Especialidades e Consultas operam somente no SQLite local. Não foram identificados dashboards por perfil nem módulos de prontuário/registro de atendimento. O Xano inspecionado tem recursos de `user`, `paciente` e `profissional`, mas não há evidência suficiente de autenticação, papéis ou autorização por módulo. Esses fatos não equivalem à validação do ambiente publicado.

A evolução deve ocorrer em etapas com OpenSpec: (1) definir e validar autenticação, papéis e vínculo conta–Médico no Xano; (2) reconciliar e proteger os CRUDs existentes; (3) modelar e migrar Especialidades e Consultas; (4) implementar dashboards por perfil; (5) implementar prontuários e registros de atendimento com autoria e acesso mínimo; (6) executar testes integrados com dados fictícios e remover SQLite somente após migração validada. As definições de status, fuso/período dos dashboards, cardinalidades clínicas e retenção são pré-requisitos ainda pendentes.

## 12. Estratégia de desenvolvimento

O desenvolvimento será realizado através de mudanças incrementais.

Antes de implementar funcionalidades relevantes, o grupo deverá analisar o objetivo da mudança, seu impacto e suas regras.

O OpenSpec será utilizado para auxiliar na especificação das mudanças.

O Git e o GitHub serão utilizados para controle de versão, histórico das alterações e organização do desenvolvimento.

## 13. Fonte de verdade e documentação

A documentação do projeto deverá ser mantida nos arquivos de contexto e nas especificações do OpenSpec.

Os documentos principais de contexto deverão representar a visão geral, o domínio e as regras de desenvolvimento do projeto.

As mudanças relevantes deverão ser especificadas, revisadas e registradas antes ou durante sua implementação, de acordo com o fluxo adotado pelo OpenSpec.