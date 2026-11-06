## 1. Preparar e validar o ambiente

- [ ] 1.1 Obter autorização para um workspace/branch Xano não-live e confirmar que o inventário de branches mostra destino isolado; manter `v1` live sem escrita.
- [ ] 1.2 Comparar por metadados somente leitura o schema publicado de `user` e os endpoints de autenticação/CRUD com os arquivos versionados; registrar diferenças sem consultar registros.
- [ ] 1.3 Solicitar ao responsável a verificação da possível credencial Swagger e registrar apenas o resultado e a ação autorizada (manter, revogar ou rotacionar), sem copiar seu valor para arquivos, issues ou logs.
- [ ] 1.4 Validar em ambiente não-live a compatibilidade da autenticação nativa Xano (`auth = true`, campo `password`, verificação de senha, token e `$auth.id`) com conta e dados sintéticos; registrar o resultado sem credenciais reais.
- [ ] 1.5 Aprovar o bootstrap seguro da primeira conta Admin, recuperação e desativação de contas; verificar o fluxo documentado não depende de cadastro público nem de segredos versionados.

## 2. Implementar identidade e autenticação no Xano

- [ ] 2.1 Aplicar em branch não-live o schema aprovado para perfil e vínculo 1:1 conta Médico–Profissional; validar restrições de unicidade e ausência de vínculos duplicados com dados sintéticos.
- [ ] 2.2 Implementar provisionamento controlado por Admin para contas Admin/Médico, sem cadastro público; testar que Médico e chamadas sem sessão recebem HTTP 403/401 e não criam nem alteram contas.
- [ ] 2.3 Implementar login/logout com autenticação nativa, expiração e revogação no backend; testar credenciais inválidas, conta inativa e reutilização do token após logout sem retornar senha ou hash.
- [ ] 2.4 Proteger os endpoints existentes de `user` com autenticação, autorização e projeção segura; testar chamadas diretas para que nenhum perfil obtenha senha, hash, token ou CRUD não autorizado.

## 3. Aplicar autorização por perfil e escopo

- [ ] 3.1 Proteger endpoints existentes de Pacientes e Profissionais para operações administrativas Admin e acesso Médico mínimo e próprio; testar cada operação por chamada HTTP direta.
- [ ] 3.2 Implementar a resolução do Profissional a partir da conta Médico autenticada sem aceitar `profissional_id` do cliente; testar vínculo 1:1 e negar acesso à agenda/atendimento de outro médico.
- [ ] 3.3 Aplicar o mesmo contrato de autorização às APIs de agenda, consultas e prontuários quando implementadas; validar que Médico só registra atendimento confirmado como realizado por ele e que autoria vem da sessão.

## 4. Integrar sessão e interface Streamlit

- [ ] 4.1 Implementar cliente HTTP autenticado e login/logout Streamlit usando estado de sessão; testar envio do token somente em chamadas protegidas e ausência de token em URL, disco e logs.
- [ ] 4.2 Restringir páginas e navegação ao perfil Admin ou Médico; testar acesso direto a páginas protegidas sem sessão e que a interface não simula autenticação quando Xano está indisponível.
- [ ] 4.3 Tratar HTTP 401 como sessão encerrada e retorno ao login, HTTP 403 como acesso negado com sessão mantida e falhas de serviço como erro explícito; verificar que escritas não são repetidas automaticamente.

## 5. Verificar permissões e integração

- [ ] 5.1 Executar matriz de testes de API com dados sintéticos: Admin permitido em funções administrativas; Médico negado em CRUD administrativo e limitado à própria agenda; chamadas anônimas, expiradas e revogadas retornam HTTP 401; perfil/escopo incompatível retorna HTTP 403.
- [ ] 5.2 Testar registro clínico por Médico: permitir somente atendimento realizado vinculado ao próprio Profissional, rejeitar outro médico/consulta não realizada e confirmar autoria derivada da identidade autenticada.
- [ ] 5.3 Executar testes automatizados Streamlit/cliente para login, logout, expiração e acesso negado; confirmar ausência de tokens, credenciais e dados pessoais nas saídas de teste.
- [ ] 5.4 Revisar autorização em todos os endpoints tocados, executar testes relevantes e validar a Change com OpenSpec em modo estrito antes de qualquer proposta separada de publicação.
