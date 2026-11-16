## 1. Reconciliar requisitos aprovados

- [x] 1.1 Atualizar proposta, design, specs e documentação de domínio para refletir perfis Admin/Médico, escopo funcional, autorização backend e estado parcial; verificar coerência e que nenhuma capacidade é descrita como já implementada sem evidência.
- [x] 1.2 Registrar as decisões já aprovadas e as pendências de identidade, permissões, vínculos, status, métricas, cardinalidades, retenção e dados fictícios; verificar que nenhuma pendência foi convertida em requisito inventado.
- [x] 1.3 Validar esta Change com `openspec validate revisar-escopo-modelo-clinica --strict --no-interactive` e revisar `git diff`/`git status`; verificar que somente arquivos documentais autorizados foram alterados.

## 2. Resolver decisões bloqueadoras

- [ ] 2.1 Definir o fluxo de autenticação no Xano, os papéis, o provisionamento Admin/Médico e a reutilização ou extensão segura da tabela `user`; verificar login e autorização em ambiente não-live.
- [ ] 2.2 Definir a cardinalidade e unicidade do vínculo conta Médico–Profissional e o ciclo de criação, desativação e recuperação; verificar que o backend deriva a identidade profissional da sessão autenticada.
- [ ] 2.3 Definir fuso e período de “hoje”, semântica de consultas “agendadas” e status incluídos em “não realizadas”; verificar as contagens com cenários de status aprovados.
- [ ] 2.4 Aprovar catálogo, status inicial, transições, ocupação de horário, duração/conflito e retenção/exclusão; verificar integridade e prevenção de conflitos no backend.
- [ ] 2.5 Confirmar cardinalidades do prontuário e dos registros de atendimento, campos clínicos, autoria imutável, edição/exclusão, auditoria e regras para provar atendimento realizado; verificar cenários de acesso por papel.
- [ ] 2.6 Confirmar ambiente Xano seguro não-live, política de autorização de cada API e uso exclusivo de dados fictícios; verificar que nenhuma integração ou teste real acessa registros preexistentes.

## 3. Implementar em Changes dependentes

- [ ] 3.1 Planejar uma Change de autenticação/autorização Xano com testes Admin/Médico e restrição por médico; verificar acesso negado no backend mesmo com chamadas diretas à API.
- [ ] 3.2 Reconciliar `crud-pacientes-profissionais-xano-streamlit` com os controles por perfil e concluir validações remotas autorizadas; verificar CRUD por Admin e negar CRUD administrativo para Médico.
- [ ] 3.3 Reconciliar `modelar-especialidades-consultas-xano` com decisões de schema, catálogo, status, relações e conflitos; verificar que a especialidade pertence ao médico e que regras são aplicadas no Xano.
- [ ] 3.4 Implementar dashboards Admin e Médico usando APIs autorizadas; verificar as seis métricas administrativas e que o Médico só recebe sua agenda do dia.
- [ ] 3.5 Implementar prontuário e registros de atendimento no Xano com autoria e acesso mínimo; verificar que Médico só registra paciente atendido por ele e que Admin pode gerenciar conforme política aprovada.
- [ ] 3.6 Migrar Especialidades e Consultas do SQLite para APIs Xano com dados fictícios e estratégia reversível; verificar integridade, contagens e fluxos integrados antes de remover dependências.
- [ ] 3.7 Após validar todas as migrações, remover inicialização e serviço SQLite em Change própria; verificar que nenhuma página ou teste funcional depende do SQLite e que o arquivo local só é tratado conforme decisão explícita de retenção.
