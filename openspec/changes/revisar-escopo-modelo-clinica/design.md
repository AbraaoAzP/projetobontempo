## Context

Consulte [proposal.md](./proposal.md) para o motivo e o limite desta Change. As deltas em `specs/` definem os requisitos aprovados e as questões que continuam sujeitas à decisão do grupo. Esta revisão é documental e não habilita os módulos nem altera controles remotos.

Evidências observadas no workspace:

- `xano/table/` contém `user`, `paciente` e `profissional`. As tabelas de paciente e profissional têm somente ID e dados básicos; `profissional.especialidade` é texto opcional. Não foram encontradas tabelas de especialidade, consulta, status de consulta, prontuário ou registro de atendimento, nem chaves estrangeiras ou índices de unicidade para essas relações.
- `xano/api/` contém endpoints CRUD de pacientes e profissionais e endpoints CRUD de `user` no grupo localmente nomeado `Autentication`. Os arquivos examinados não declaram login, criação de sessão, papel, nem referência aos usuários nos endpoints de pacientes e profissionais. Isso descreve apenas os arquivos locais e não comprova a configuração ou a exposição do ambiente Xano publicado.
- As tabelas locais declaram `auth = false`; isso não comprova controles efetivos de acesso nas APIs publicadas ou na infraestrutura.
- O inventário somente de leitura confirmou o workspace Xano `153318`, com a única branch `v1` marcada como live e `allow_push = false`. O Xano contém `user`, `paciente` e `profissional`, mas não há evidência de papéis Admin/Médico, vínculo entre conta e médico ou autorização por módulo.
- As especificações consolidadas de pacientes e profissionais descrevem CRUD e dados pessoais básicos. Profissionais ainda permitem especialidade em texto livre. A entrega inicial tinha Início, Pacientes e Profissionais sem chamadas HTTP e tabelas vazias; uma Change posterior planeja/implementa listagens GET condicionais, mantendo-as desabilitadas por padrão até as verificações de segurança e autorização.
- O CRUD de Pacientes e Profissionais já está integrado por HTTP no Streamlit; Especialidades e Consultas continuam dependentes do SQLite local. A existência de telas/rotas não significa que os requisitos novos de autenticação e autorização estejam atendidos.
- O arquivo de referência PDF indicado não está disponível no workspace. A Change usa como fonte para as decisões aprovadas o pedido do grupo e registra as inferências como pendentes.

## Goals / Non-Goals

**Goals:**

- Consolidar no OpenSpec o escopo funcional aprovado e um contrato conceitual para as relações clínicas.
- Registrar os perfis Admin e Médico, seus limites funcionais e a exigência de aplicar autenticação e autorização no Xano.
- Tornar verificáveis os bloqueios de modelagem, integridade e proteção de dados que precisam de aprovação antes de mudanças físicas ou de API.
- Distinguir o que existe nos arquivos locais, o que foi aprovado pelo grupo e o que ainda é hipótese.

**Non-Goals:**

- Implementar autenticação, autorização, dashboards, operações clínicas ou qualquer mudança no frontend ou backend.
- Alterar Xano, banco, dados, endpoints, permissões ou configuração publicada.
- Presumir que a notação “PRONTUARIO 1 REGISTRO_ATENDIMENTO” defina cardinalidade física sem confirmação; a relação N:N Médico–Especialidade está aprovada, mas suas restrições físicas ainda precisam de validação.

## Decisions

### Separar entidade conceitual de evidência de implementação

As tabelas e endpoints são descritos conforme evidência local/remota explicitamente identificada, não como prova de segurança ou autorização. A Change não cria estrutura física; cada futura implementação deverá validar o ambiente e mapear dados e dependências antes de migração.

Alternativa considerada: tratar os arquivos Xano locais como prova de que APIs estão implantadas. Isso foi rejeitado porque o workspace não confirma publicação, permissões ou autenticação do ambiente alvo.

### Tratar decisões aprovadas como contrato e cardinalidades incertas como bloqueios

Os cinco módulos, os perfis Admin e Médico, o médico como único tipo de profissional, a relação N:N Médico–Especialidade com zero vínculos possíveis durante a transição, a exigência de vínculo para agendar consultas, o prontuário opcional por paciente, o registro clínico associado à consulta realizada e a localização dos campos clínicos em REGISTRO_ATENDIMENTO são requisitos aprovados. Login e autorização no backend também são obrigatórios. Permanecem pendentes os detalhes técnicos de identidade e associação de contas, as contagens do dashboard, a interpretação de “não realizadas”, a quantidade de registros por prontuário, o catálogo e as transições de STATUS_CONSULTA e as políticas de retenção/exclusão.

Como hipótese para revisão, um prontuário longitudinal tende a conter múltiplos registros. A especificação exige que essa hipótese seja aprovada, não a transforma em restrição de banco nesta Change.

Alternativa considerada: escolher unilateralmente cardinalidades usuais de agenda clínica. Isso foi rejeitado porque a cardinalidade de prontuário–registro, o histórico de status e a retenção clínica ainda têm impacto de domínio e integridade; a cardinalidade Médico–Especialidade já foi aprovada pelo grupo.

### Manter diagnóstico e conteúdo clínico no registro de atendimento

CONSULTA representa a agenda e o estado da consulta, enquanto REGISTRO_ATENDIMENTO contém diagnóstico, anotações clínicas e conduta. Uma consulta apenas agendada pode existir sem prontuário ou registro; uma consulta realizada pode ter no máximo um registro próprio conforme decisão do grupo.

Alternativa considerada: colocar campos clínicos em CONSULTA por simplicidade. Isso duplica semânticas e acopla agendamento a documentação clínica, contrariando as decisões aprovadas.

### Não inferir autenticação nem remover artefatos de usuário

As capacidades futuras exigem login e dois perfis de acesso, mas não determinam, por si sós, os campos, o fluxo de provisionamento, o mecanismo de sessão ou as permissões concretas do Xano. A tabela e os endpoints locais de `user` serão avaliados para possível reutilização, sem presumir que implementem autenticação segura. Contas de Médico devem ser vinculadas ao respectivo registro Profissional; a cardinalidade e a garantia de unicidade desse vínculo precisam ser definidas antes do schema. Nenhum endpoint administrativo ou clínico poderá depender apenas de ocultação de páginas ou controles do Streamlit.

Alternativas de autenticação/autorização devem ser avaliadas contra os recursos já disponíveis no Xano antes da implementação. Remover ou substituir `user` é fora do escopo desta Change e exigiria evidência de dependências e aprovação próprias.

### Separar permissões por perfil no contrato

Admin pode operar os módulos administrativos e consultar/gerenciar prontuários. Médico tem acesso à própria agenda diária, aos dados necessários ao atendimento e à criação de registro de prontuário somente após atendimento realizado por ele. Médico não acessa operações administrativas nem pode atribuir a si autoria ou atendimento que o backend não confirme. A verificação de papel, vínculo profissional, autoria e atendimento deve ocorrer no backend Xano em toda API relevante.

Esta matriz registra os limites aprovados, mas não escolhe se uma regra será aplicada por middleware, grupos de API, funções ou outra configuração Xano. A estratégia deve ser validada no ambiente não-live antes de habilitar o Streamlit.

### Tratar dashboards como projeções do backend

Dashboard Admin deve expor contagens de pacientes, médicos, consultas agendadas, consultas do dia, realizadas e não realizadas. Dashboard Médico deve restringir a agenda ao médico autenticado e ao dia corrente, mostrando horários e quantidade de consultas. Não se fixa uma implementação ou definição de status nesta Change: fuso horário, período, distinção entre agendada para hoje e total agendado, status considerados “não realizados” e tratamento de cancelamentos permanecem pendentes.

Alternativa considerada: calcular indicadores a partir de dados carregados no Streamlit. Foi rejeitada como fonte de autorização e integridade; agregações e filtros por perfil devem vir do Xano, evitando expor coleções amplas ao frontend.

### Bloquear exposição clínica até aprovação de salvaguardas

Embora login e papéis agora façam parte do escopo aprovado, a futura persistência ou exposição de prontuários ainda exige validação de confidencialidade, controle de acesso por papel e autoria, exposição de APIs, auditoria e retenção antes de ser habilitada. A ausência atual de evidência de controles no Xano não pode ser tratada como autorização.

Alternativa considerada: adiar qualquer análise de segurança até a integração frontend–backend. Isso foi rejeitado porque dados clínicos podem ser expostos por APIs independentemente do frontend e as regras de segurança devem ser tratadas no backend.

## Risks / Trade-offs

- [A autorização atual não está comprovada e endpoints podem estar expostos] → Não habilitar operações clínicas nem chamadas reais até verificar autenticação e autorização no backend por perfil, em ambiente não-live.
- [Uma conta pode ser associada ao médico errado ou a vários registros] → Aprovar a cardinalidade, unicidade e o processo de vinculação; o Xano deve derivar a identidade profissional da sessão autenticada.
- [Cardinalidades ainda ambíguas podem causar duplicidade, órfãos ou migração destrutiva] → Obter decisão explícita sobre prontuário–registro, consulta–status, consulta–registro e exclusões; implementar Médico–Especialidade como N:N com integridade validada e consulta condicionada a vínculo existente.
- [Indicadores de dashboard podem divergir por definição de status ou fuso] → Aprovar janela temporal, categorias e fonte das contagens antes de criar endpoints.
- [O campo de especialidade em texto livre permite grafias inconsistentes e não identifica uma especialidade referenciada] → Tratar o catálogo e a conversão dos valores existentes numa Change de modelo/migração aprovada.
- [SQLite contém funcionalidades que ainda não existem no backend definitivo] → Migrar e validar Especialidades/Consultas antes de remover serviço, inicialização ou arquivo local; não manter SQLite na arquitetura final.
- [Regras atuais de exclusão de paciente e profissional não consideram dados dependentes futuros] → Definir retenção e comportamento de exclusão antes de criar referências clínicas; impedir cascatas implícitas.
- [Os arquivos locais podem divergir do Xano publicado] → Inspecionar o ambiente de destino e planejar backup, migração reversível e reconciliação antes da implementação.
- [Há metadado local com aparência de credencial no grupo Xano de autenticação] → Não reproduzir o valor; confirmar se está ativo e, se necessário, tratar sua rotação em fluxo seguro antes de publicar ou usar o grupo.

## Migration Plan

Não há migração nem implementação nesta Change. A documentação aprovada registra o alvo sem afirmar que as funcionalidades existem. As etapas futuras devem ser separadas e ordenadas:

1. Definir o fluxo de autenticação Xano, perfis, vínculo de Médico a Profissional e controles de acesso; verificar em ambiente não-live antes de habilitar qualquer cliente.
2. Reconciliar a Change `crud-pacientes-profissionais-xano-streamlit` com a autorização por perfil e concluir o CRUD protegido sem alterar registros preexistentes.
3. Decidir pendências de domínio e reconciliar a Change `modelar-especialidades-consultas-xano` para schema, status, agenda, especialidades e regras backend.
4. Implementar os dashboards por perfil e as operações de prontuário/atendimento após aprovar regras e proteger APIs.
5. Migrar Especialidades e Consultas do SQLite, validar contratos/dados fictícios e só então remover inicialização e serviço SQLite em Change própria, preservando o arquivo até aprovação de retenção.

A Change `integrar-listagens-xano-streamlit` também tem como pré-condição a verificação de segurança; suas listagens não substituem autorização. A Change `implementar-mvp-local-sqlite` documenta o legado e não deve ser interpretada como arquitetura final.

Cada etapa deverá ter critérios de reversão próprios. Não remover `user`, `paciente` ou `profissional`; qualquer transformação de especialidade em catálogo ou adição de relações deve preservar IDs e dados existentes, com plano de rollback aprovado antes da execução.

## Pontos para aprovação do grupo

- `PRONTUARIO 1 REGISTRO_ATENDIMENTO`: confirmar quantos registros um prontuário pode conter e a unicidade correspondente.
- Médico–Especialidade: relação N:N aprovada, com zero ou mais vínculos por médico durante a transição; exigir vínculo entre médico e especialidade para agendamento e validar FKs e unicidade do par na Change de implementação.
- Conta Médico–Profissional: definir cardinalidade, unicidade, provisionamento, recuperação de acesso e comportamento de desativação; reutilizar `user` somente após confirmar suporte técnico.
- `STATUS_CONSULTA`: aprovar valores, status inicial, transições, possibilidade de histórico e quais estados contam como agendados, realizados e não realizados.
- Dashboard: definir fuso horário, janela de “hoje”, significado de consultas “agendadas” e tratamento de cancelamentos/faltas nas contagens.
- Consulta–Registro de Atendimento: confirmar regra de vínculo e como o backend comprova que a consulta foi realizada pelo médico autor.
- Exclusão/retenção: aprovar o comportamento para paciente, médico, consulta, prontuário e registro clínico quando houver dependências.
- Autorização: confirmar mecanismos Xano e escopo das permissões para Admin e Médico, incluindo os endpoints atuais de CRUD e restrições contra acesso direto a dados de outros médicos.
- Dados de demonstração: confirmar que datasets de teste e qualquer fixture remoto são exclusivamente fictícios antes de habilitar acesso integrado.
