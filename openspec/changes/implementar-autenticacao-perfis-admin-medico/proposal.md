## Why

O sistema ainda não possui evidência de login ou autorização efetiva por perfil, embora seus dados clínicos exijam acesso restrito a Admin e Médico. É necessário estabelecer um contrato verificável para autenticação Xano, sessão Streamlit e autorização por endpoint antes de habilitar qualquer fluxo administrativo ou clínico.

## What Changes

- Definir login e logout usando os recursos nativos de autenticação do Xano, sujeitos à validação em ambiente não-live.
- Vincular a sessão do Streamlit à identidade autenticada pelo backend e tratar expiração, falha de autenticação e acesso negado sem confiar em controles visuais.
- Definir papéis Admin e Médico, vínculo 1:1 entre conta Médico e Profissional e provisionamento controlado por Admin, além de autorização backend para funções administrativas, agenda própria e registros clínicos autorizados.
- Especificar testes positivos e negativos para ambos os perfis, incluindo chamadas diretas aos endpoints e sessões expiradas.
- Inventariar e tratar com segurança os recursos de usuário existentes; verificar a possível credencial Swagger mencionada no design sem reproduzir seu valor.

Fora do escopo desta Change: criar contas reais, executar alterações no Xano, habilitar APIs em `v1` live, integrar ou alterar código Python/XanoScript, usar dados pessoais ou clínicos reais, publicar/deploy, ou decidir políticas clínicas ainda pendentes.

## Capabilities

### New Capabilities

- `autenticacao-perfis`: login/logout Xano, sessão Streamlit, papéis, vínculo conta–Profissional, autorização backend e respostas de autenticação.

### Modified Capabilities

- `interface-web`: exigir sessão para áreas protegidas, apresentar funções conforme perfil e tratar expiração/negação sem substituir autorização backend.
- `pacientes`: restringir operações administrativas ao Admin e limitar dados acessíveis ao Médico aos atendimentos autorizados.
- `profissionais`: restringir o CRUD administrativo ao Admin e usar o vínculo autenticado para determinar o Médico autorizado.

## Impact

- Xano: a listagem somente de leitura do workspace retornou apenas `v1` como live; não foi identificado branch/ambiente não-live. A tabela local versionada `user` tem autenticação desativada, contém campo de senha do tipo `password`, e os arquivos mostram CRUD genérico, não fluxo de login/logout nem autorização por perfil. O estado publicado e suas políticas ainda precisam de verificação; a listagem não confirma outras restrições de escrita.
- Autenticação nativa Xano: a documentação consultada descreve tabela habilitada para autenticação, tipo `password`, `security.check_password`, `security.create_auth_token`, identidade `$auth.id` e padrões de sessão. A aplicabilidade à tabela e ao ambiente do projeto precisa ser validada sem escrita remota.
- Streamlit: a sessão deverá manter somente o estado necessário para chamar APIs autenticadas e terminar com logout ou expiração; nenhuma credencial ou token será versionado ou colocado na URL.
- Dependências: coordenar a proteção dos CRUDs com `crud-pacientes-profissionais-xano-streamlit` e `integrar-listagens-xano-streamlit`, e garantir que APIs futuras de Especialidades/Consultas e Prontuários respeitem a mesma autorização. A implementação e os testes integrados dependem da disponibilização e autorização de ambiente Xano não-live.
- Segurança: há um possível valor de credencial Swagger em arquivo versionado de grupo de APIs. Sua validade, exposição e necessidade de revogação/rotação são pendências; este planejamento não reproduz nem altera o valor.
- Nenhum código, usuário, dado, tabela, endpoint, permissão, branch ou configuração remota será alterado nesta Change de planejamento.
