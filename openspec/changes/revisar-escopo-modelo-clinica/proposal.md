## Why

O escopo aprovado agora inclui acesso autenticado para Admin e Médico, enquanto a Change ainda exclui login e papéis. Esta revisão reconcilia os requisitos de acesso, módulos e modelo clínico com o estado parcial do sistema sem implementar funcionalidades nem presumir que os recursos Xano versionados estejam publicados ou protegidos.

## What Changes

- Registrar os cinco módulos funcionais — Pacientes, Médicos, Especialidades, Consultas e Prontuários — e os dois perfis aprovados, Admin e Médico, distinguindo escopo-alvo de funcionalidades implementadas.
- Especificar login e autorização obrigatoriamente no backend Xano; avaliar a reutilização da tabela `user` e o vínculo de contas Médico aos registros de Profissional sem presumir que os recursos existentes já atendem a esses requisitos.
- Definir o acesso funcional de cada perfil: Administração completa para Admin; agenda própria do dia e dados mínimos para atendimento para Médico; registro clínico somente para paciente efetivamente atendido pelo médico autor.
- Especificar os indicadores dos dashboards administrativos e a agenda diária do médico, registrando as definições que ainda dependem de decisão.
- Manter a relação N:N Médico–Especialidade, os vínculos de consulta, o prontuário longitudinal e a separação entre Consulta e Registro de Atendimento; preservar como pendentes as cardinalidades e regras ainda não aprovadas.
- Identificar dependências entre autenticação/autorização, os CRUDs Xano existentes, a modelagem de Especialidades/Consultas e a migração gradual da persistência SQLite legada.
- Atualizar `docs/project-overview.md` e `docs/domain-model.md` para distinguir requisitos aprovados, pendências e estado real da implementação.

**Fora do escopo:** implementar qualquer funcionalidade; alterar código Python, XanoScript, tabelas, registros, endpoints ou permissões; migrar ou remover SQLite; criar novas Changes; decidir silenciosamente questões pendentes; usar dados reais de pacientes; executar archive, commit, push, merge ou deploy.

## Capabilities

### New Capabilities

- `modelo-clinico`: definir perfis, vínculos de identidade, regras de acesso e relações clínicas necessárias ao escopo aprovado.

### Modified Capabilities

- `pacientes`: definir administração pelo Admin e acesso do Médico somente quando necessário a atendimento autorizado, preservando integridade clínica.
- `profissionais`: restringir o cadastro administrativo a médicos e especificar o vínculo da conta de Médico ao registro profissional.
- `interface-web`: acrescentar login, navegação e dashboards conforme o perfil, sem considerar controles visuais como autorização.

## Impact

- Artefatos OpenSpec existentes: `modelo-clinico`, `pacientes`, `profissionais` e `interface-web`; nenhuma Change ou arquivo novo é criado nesta etapa.
- Documentação: atualizar `docs/project-overview.md` e `docs/domain-model.md` com escopo-alvo, estado parcial, entidades, relações e pendências.
- Referências Xano observadas: tabelas `user`, `paciente` e `profissional` e endpoints correspondentes. A existência de arquivos locais ou recursos remotos não comprova autenticação, autorização por papel ou segurança efetiva.
- Dependências: proteger e reconciliar os CRUDs da Change `crud-pacientes-profissionais-xano-streamlit`; definir schema e regras de Especialidades/Consultas com `modelar-especialidades-consultas-xano`; migrar os módulos que ainda usam SQLite antes da remoção definitiva.
- Não há alteração de código, APIs, dados, tabelas, permissões, dependências ou configuração Xano nesta etapa. O estado atual será descrito sem declarar os requisitos aprovados como implementados.
