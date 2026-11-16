## MODIFIED Requirements

### Requirement: Preservar o escopo funcional da interface

A interface SHALL oferecer login para os perfis Admin e Médico e navegação para Início e os cinco módulos funcionais aprovados: Pacientes, Profissionais (médicos), Especialidades, Consultas e Prontuários. Páginas e operações protegidas SHALL exigir sessão autenticada; a navegação SHALL refletir o perfil, sem substituir autorização no Xano.

Admin SHALL visualizar e acessar funções administrativas aprovadas. Médico SHALL visualizar somente seu dashboard, sua agenda e as funções clínicas autorizadas. Chamadas ao backend SHALL usar APIs HTTP do Xano; nenhuma página SHALL acessar diretamente o banco de dados ou exibir dados reais como demonstração.

#### Scenario: Acessar as páginas sem autenticação ou integração

- **WHEN** uma pessoa inicia a aplicação sem sessão e o Xano está indisponível ou não configurado
- **THEN** a interface apresenta somente o acesso público necessário ao login e uma mensagem explícita de indisponibilidade, sem exibir páginas, dados ou operações protegidas nem simular login

#### Scenario: Conferir o escopo das páginas

- **WHEN** uma pessoa navega após autenticação
- **THEN** a interface oferece os módulos aprovados conforme o perfil autenticado e não apresenta como disponível uma função não implementada

#### Scenario: Exigir login para acessar função protegida

- **WHEN** uma pessoa sem sessão tenta abrir diretamente uma página ou ação protegida
- **THEN** a interface solicita login e o backend não retorna dados protegidos

#### Scenario: Encerrar interface após expiração

- **WHEN** uma chamada protegida retorna autenticação expirada
- **THEN** a interface limpa o estado de sessão e retorna ao login sem repetir automaticamente operações de escrita

#### Scenario: Tratar acesso não autorizado

- **WHEN** o backend nega uma operação ao perfil atual
- **THEN** a interface apresenta mensagem de acesso negado sem expor detalhes internos e sem tratar a resposta como lista vazia ou sucesso
