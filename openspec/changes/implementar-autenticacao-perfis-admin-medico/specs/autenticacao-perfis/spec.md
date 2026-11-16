## Purpose

Define autenticação, sessão e autorização por perfil para que operações administrativas e dados clínicos sejam acessíveis somente a identidades verificadas pelo backend Xano.

## ADDED Requirements

### Requirement: Autenticar Admin e Médico pelo Xano

O sistema SHALL autenticar credenciais de usuários com perfil Admin ou Médico por meio dos recursos nativos de autenticação do Xano aprovados para o ambiente. Credenciais inválidas ou contas inativas SHALL ser rejeitadas sem revelar se a conta existe. Senhas SHALL ser processadas e armazenadas somente pelos mecanismos seguros do Xano; SHALL NOT ser retornadas por APIs nem persistidas pelo Streamlit.

#### Scenario: Login válido

- **WHEN** um usuário ativo envia credenciais válidas ao endpoint de login
- **THEN** o Xano autentica a conta e retorna somente os dados de sessão necessários, incluindo um token de autenticação válido e o perfil determinado pelo backend

#### Scenario: Credenciais inválidas

- **WHEN** um usuário envia credenciais inválidas ou pertencentes a uma conta inativa
- **THEN** o backend responde com HTTP 401 e mensagem genérica de autenticação, sem retornar token nem informar se a conta existe

### Requirement: Provisionar contas sem cadastro público

O Xano SHALL permitir que somente um Admin autenticado e autorizado provisione contas Admin ou Médico. O cliente SHALL NOT escolher ou alterar o próprio perfil. O vínculo Médico–Profissional SHALL ser 1:1: cada conta Médico deverá ter exatamente um Profissional e cada Profissional poderá estar vinculado a no máximo uma conta Médico. O processo de bootstrap da primeira conta Admin deverá ser definido e aprovado antes da ativação do provisionamento.

#### Scenario: Admin provisiona uma conta Médico

- **WHEN** um Admin autenticado e autorizado provisiona uma conta Médico e a vincula a um Profissional ainda não associado
- **THEN** o backend cria a conta com perfil Médico e vínculo exclusivo, sem retornar senha ou hash

#### Scenario: Médico tenta provisionar ou alterar perfil

- **WHEN** um Médico tenta criar conta ou alterar o próprio perfil/vínculo, inclusive por chamada direta à API
- **THEN** o Xano responde com HTTP 403 e não cria nem altera contas

#### Scenario: Profissional já vinculado

- **WHEN** um Admin tenta vincular uma segunda conta Médico ao mesmo Profissional
- **THEN** o Xano rejeita a operação e mantém o vínculo único sem criar uma conta parcialmente configurada

### Requirement: Manter e encerrar a sessão autenticada

O Streamlit SHALL manter a sessão somente no estado de sessão do servidor e enviar o token Xano em chamadas protegidas. O logout SHALL remover o estado local e invalidar a sessão no backend conforme o mecanismo de revogação aprovado. Tokens e credenciais SHALL NOT ser colocados em URL, arquivos versionados, logs ou conteúdo visível ao usuário.

#### Scenario: Manter sessão após login

- **WHEN** o login é validado pelo Xano
- **THEN** o Streamlit mantém a sessão autenticada e envia o token somente às APIs protegidas necessárias

#### Scenario: Encerrar sessão por logout

- **WHEN** o usuário solicita logout
- **THEN** o Streamlit limpa o estado autenticado, o backend invalida a sessão e chamadas subsequentes com essa sessão são rejeitadas

#### Scenario: Tratar token expirado

- **WHEN** uma API protegida informa que a autenticação expirou
- **THEN** o Streamlit descarta a sessão local, não repete silenciosamente uma operação de escrita e solicita novo login

### Requirement: Aplicar autorização Admin no backend

O Xano SHALL verificar identidade autenticada e perfil Admin em cada endpoint de função administrativa. O acesso administrativo SHALL incluir CRUD de pacientes, médicos, consultas e prontuários e consulta ao catálogo de especialidades, sujeito às regras de integridade e retenção aprovadas. Ocultar controles no Streamlit SHALL NOT conceder autorização.

#### Scenario: Admin executa operação administrativa

- **WHEN** uma conta autenticada Admin solicita uma operação administrativa permitida
- **THEN** o Xano verifica seu perfil e aplica as regras de integridade antes de retornar ou alterar dados

#### Scenario: Médico tenta operação administrativa direta

- **WHEN** uma conta autenticada Médico chama diretamente um endpoint administrativo
- **THEN** o Xano rejeita a chamada sem depender da navegação apresentada pelo Streamlit

### Requirement: Restringir Médico à própria identidade e aos atendimentos autorizados

Cada conta ativa com perfil Médico SHALL resolver para exatamente um registro Profissional, e cada registro Profissional SHALL estar vinculado a no máximo uma conta Médico. O backend SHALL derivar a identidade profissional da sessão autenticada e SHALL NOT confiar em identificador de médico enviado pelo cliente. Médico SHALL acessar somente seu dashboard, sua agenda e os dados de paciente necessários aos atendimentos autorizados, e SHALL registrar prontuário somente após o backend confirmar atendimento realizado por esse Médico. Médico SHALL NOT acessar funções administrativas.

#### Scenario: Médico consulta a própria agenda

- **WHEN** uma conta Médico autenticada consulta agenda ou dashboard
- **THEN** o Xano restringe a resposta às consultas do registro Profissional vinculado à conta, sem aceitar outro identificador de médico informado pelo cliente

#### Scenario: Médico tenta consultar outro médico

- **WHEN** uma conta Médico solicita agenda ou dados de atendimento de outro médico, inclusive por chamada direta
- **THEN** o Xano rejeita ou restringe a resposta ao escopo próprio

#### Scenario: Médico registra atendimento permitido

- **WHEN** o Médico vinculado solicita registro de prontuário para atendimento confirmado como realizado por ele
- **THEN** o Xano grava a autoria a partir da sessão autenticada e aceita somente os dados autorizados

#### Scenario: Médico tenta registrar atendimento não realizado

- **WHEN** o Médico tenta registrar atendimento sem consulta realizada vinculada ao próprio registro Profissional
- **THEN** o Xano rejeita a operação e não cria registro clínico

### Requirement: Negar acesso a endpoints protegidos sem autorização

Endpoints protegidos SHALL rejeitar solicitações sem autenticação válida, com sessão revogada ou sem perfil/escopo permitido. Falta, invalidade, expiração ou revogação de autenticação SHALL retornar HTTP 401; identidade autenticada sem perfil/escopo permitido SHALL retornar HTTP 403. As respostas SHALL ser distinguíveis sem incluir dados pessoais, segredos ou detalhes internos.

#### Scenario: Chamada sem sessão

- **WHEN** uma pessoa chama diretamente um endpoint protegido sem token válido
- **THEN** o Xano retorna HTTP 401 e não retorna nem altera dados protegidos

#### Scenario: Sessão revogada

- **WHEN** uma chamada apresenta token associado a sessão encerrada ou revogada
- **THEN** o Xano retorna HTTP 401 e não retorna nem altera dados protegidos

#### Scenario: Perfil sem permissão

- **WHEN** uma conta autenticada solicita recurso fora do seu perfil ou escopo
- **THEN** o Xano retorna HTTP 403 e não retorna nem altera o recurso
