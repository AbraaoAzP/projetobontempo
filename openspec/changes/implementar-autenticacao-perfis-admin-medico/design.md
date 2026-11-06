## Context

Consulte [proposal.md](./proposal.md) para escopo e motivação; os contratos de comportamento estão nas quatro specs desta Change.

Evidências somente de arquivos versionados e de metadados consultados:

- `xano/table/user.xs` define `auth = false`, nome, e-mail e campo `password` com visibilidade interna/sensível. Isso não comprova o schema publicado nem a segurança dos registros existentes.
- `xano/api/autentication/` contém endpoints CRUD genéricos de `user` (coleção e item), sem fluxo versionado de login/logout nem declaração explícita de autorização por perfil. Não foi feita chamada a endpoints de registros.
- `xano/table/profissional.xs` não tem vínculo com `user`. As cardinalidades e o ciclo de vida da associação ainda requerem decisão.
- Os arquivos de projeto contêm uma configuração candidata de credencial Swagger no grupo de API. Seu valor não é reproduzido aqui; validade, exposição e necessidade de revogação/rotação deverão ser verificadas com o responsável pelo Xano.
- A listagem somente de leitura de branches do workspace retornou apenas `v1`, com `live = true` e `backup = false`; não há branch/ambiente não-live visível. Essa listagem não confirma outras restrições de escrita. Nenhum recurso foi alterado.
- A documentação Xano consultada descreve `auth = true` para tabela de autenticação, campos `password`, `security.check_password`, `security.create_auth_token`, identidade `$auth.id` e padrões de sessão/refresh. Isso demonstra recursos nativos candidatos, não confirma compatibilidade/configuração deste workspace nem fornece, por si só, revogação de token.

## Goals / Non-Goals

**Goals:**

- Usar autenticação nativa Xano e manter as decisões de papel, vínculo profissional e autorização no backend.
- Garantir que o logout tenha efeito no backend, além de limpar a sessão Streamlit.
- Definir como falhas 401/403 e expiração terminam ou preservam a sessão.
- Estabelecer uma matriz de testes de permissões e um ambiente seguro, sem dados reais.

**Non-Goals:**

- Definir políticas clínicas pendentes, como retenção, cardinalidades de prontuário ou semântica de status de consulta.
- Criar usuários, cadastrar credenciais, acessar registros pessoais, alterar Xano, ativar endpoints ou modificar código nesta etapa de planejamento.
- Usar a credencial Swagger candidata ou incluir qualquer segredo nos testes/documentos.

## Decisions

### Reutilizar os recursos nativos de autenticação Xano, com validação antes de implementar

Preferir a autenticação nativa Xano na tabela `user`, incluindo verificação segura de senha, token Xano e identidade `$auth.id`. A documentação suporta geração de token e os arquivos já usam o tipo `password`, mas a tabela está declarada com `auth = false`; portanto, a reutilização depende de confirmar em branch não-live a configuração necessária, compatibilidade do schema e comportamento dos endpoints. Não criar mecanismo JWT externo nem confiar em um endpoint CRUD de `user` como login.

Alternativa considerada: implementar autenticação e emissão de tokens próprias. Rejeitada como primeira opção por duplicar recursos já documentados pelo Xano e aumentar o risco de armazenamento de senha/token. Se a validação não-live mostrar incompatibilidade, a equipe deve revisar o design antes de implementar uma alternativa.

### Tratar papel e vínculo como dados autoritativos do backend

Admin e Médico são papéis atribuídos por fluxo controlado no backend; não haverá cadastro público nem seleção de perfil pelo cliente. Foi decidido que cada conta Médico se vincula a exatamente um registro Profissional e que cada Profissional pode ter no máximo uma conta Médico (relação 1:1 para contas vinculadas). O provisionamento será controlado por Admin autorizado. Cada endpoint protegido verificará a identidade autenticada, o papel atual e, para operações médicas, o escopo do próprio Profissional. Papel enviado no payload ou mantido apenas no estado visual não autoriza operações.

A tabela `user` é candidata à reutilização, não uma decisão de schema já validada. O processo seguro de bootstrap da primeira conta Admin, recuperação/desativação de contas e migração de contas existentes precisam de confirmação antes de alterar o schema ou criar usuários.

Alternativa considerada: confiar em claims de papel emitidas no login sem revalidar no backend. Rejeitada por poder manter permissões obsoletas após mudança de papel ou vínculo.

### Revogar a sessão no servidor no logout

Usar token Xano com expiração e identificador de sessão não sensível, mantendo o estado ativo/revogado no backend. O backend deverá validar a sessão ativa em toda operação protegida; logout revoga esse estado e limpa `st.session_state`. O token nunca será gravado em URL, disco, logs ou repositório. A duração do token deverá ser configurada e validada no ambiente isolado antes de aprovação.

Alternativa considerada: apenas remover o token do `st.session_state`. Rejeitada porque uma cópia ainda válida do token poderia continuar acessando APIs até expirar, contrariando logout efetivo. Refresh token somente será adicionado se necessário e com rotação/revogação no backend.

### Negar por padrão e proteger também os endpoints CRUD existentes

Cada endpoint será privado por padrão e validará autenticação, perfil e escopo antes de consultar ou alterar dados. Os endpoints genéricos de CRUD de `user` deverão ser restritos ou substituídos por operações controladas; respostas jamais incluem senha, hash, token ou campos internos. A autorização não será delegada à navegação Streamlit.

Admin tem operações administrativas aprovadas. Médico tem apenas dashboard/agenda próprios, os campos mínimos necessários ao atendimento e registro de prontuário após o backend confirmar atendimento realizado e autoria. As regras médicas não devem aceitar um `profissional_id` fornecido livremente pelo cliente.

Alternativa considerada: esconder rotas e botões por perfil no frontend. Rejeitada por não proteger chamadas diretas às APIs.

### Manter a sessão Streamlit no estado de servidor e falhar de forma explícita

Guardar token e dados mínimos da identidade na sessão Streamlit do servidor, nunca em query string, arquivos ou persistência do navegador. Resposta 401 limpa a sessão e retorna ao login; resposta 403 informa acesso negado, preservando a sessão válida. Operações de escrita não serão repetidas automaticamente após expiração. Falha de Xano/configuração não produz login local nem conteúdo clínico de fallback.

### Bloquear validação integrada até existir ambiente não-live autorizado

Não testar credenciais reais nem escrever em `v1` live. Antes da implementação ou integração, o grupo deverá disponibilizar e autorizar branch ou workspace não-live, com dados fictícios e mecanismo de rollback. A verificação da credencial Swagger candidata deve ser feita pelo responsável, sem copiar o valor para Issues, logs, testes ou esta Change.

## Risks / Trade-offs

- [Risco: não há ambiente não-live visível e a única branch listada é live] → Bloquear alterações e testes integrados até ser disponibilizado e autorizado um ambiente isolado; não escrever na branch live.
- [Risco: o estado remoto da tabela `user`, políticas dos endpoints e disponibilidade de autenticação nativa diferem dos arquivos locais] → Inventariar somente metadados e validar o fluxo em ambiente isolado antes de propor schema ou habilitar clientes.
- [Risco: endpoints CRUD genéricos de usuário podem expor operações ou campos indevidos] → Revisar configuração de autenticação, projeções e permissões de cada endpoint antes de liberar login; restringir operações administrativas ao backend.
- [Risco: logout apenas no Streamlit não invalida token copiado] → Exigir revogação de sessão no backend e testar reuso de token depois de logout.
- [Risco: vínculo ou papel desatualizado permite acesso indevido] → Derivar e validar papel/vínculo no backend e definir cardinalidade, provisionamento e ciclo de vida antes de migrar.
- [Risco: a configuração Swagger versionada pode ser credencial ativa] → Verificação pelo responsável e eventual rotação/revogação tratadas de forma segura e autorizada, sem divulgar o valor.
- [Trade-off: checar estado de sessão em cada endpoint aumenta leituras/complexidade] → Preferir essa validação para cumprir revogação imediata; medir somente após o fluxo seguro estar validado.

## Migration Plan

1. Obter autorização para workspace/branch não-live e confirmar ambiente de dados fictícios, backup e rollback; não realizar mudança remota até isso ocorrer.
2. Verificar de forma segura a credencial Swagger candidata e inventariar o schema, endpoints, autenticação e permissões efetivamente existentes sem consultar registros.
3. Confirmar o bootstrap inicial de Admin, recuperação/desativação de contas, compatibilidade da tabela `user`, expiração e revogação; registrar o processo antes de schema/API. O vínculo 1:1 conta Médico–Profissional e o provisionamento controlado por Admin já foram definidos para esta Change.
4. Implementar e testar autenticação, sessões, autorização e proteção dos endpoints primeiro no ambiente não-live; somente depois conectar o Streamlit.
5. Testar matriz Admin/Médico, chamadas diretas, expiração, revogação e rollback com usuários e dados fictícios.
6. Planejar eventual promoção/publicação em Change e autorização próprias. Esta Change não autoriza deploy nem mudança de `v1` live.

Rollback: no ambiente isolado, desabilitar novas rotas/sessões, revogar tokens e restaurar configurações/schema com procedimento aprovado. Não remover nem sobrescrever contas existentes sem inventário e autorização.

## Open Questions

- Qual processo seguro fará o bootstrap da primeira conta Admin e como serão recuperação e desativação? Contas Médico serão provisionadas por Admin autorizado, sem cadastro público.
- A configuração Swagger candidata é uma credencial ativa, quem é o responsável por verificá-la e qual processo autorizado será usado para revogar/rotacionar se necessário?
- Qual branch/workspace não-live será disponibilizado e autorizado para implementação e testes?
- A autenticação nativa e o mecanismo de revogação de sessão serão compatíveis com o workspace em ambiente não-live?
