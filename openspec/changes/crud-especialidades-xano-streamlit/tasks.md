## 1. Confirmar contrato e limites Xano

- [x] 1.1 Registrar as rotas e campos informados pelo usuário para o grupo existente: GET/POST `/especialidade`, GET/PATCH/DELETE `/especialidade/{especialidade_id}`, campos `id`, `created_at` e `nome`.
- [x] 1.2 Fazer leitura real autorizada da coleção sem registrar valores de registros; verificar status e forma da resposta. Em 2026-11-09, GET respondeu HTTP 200 com lista vazia; a página Streamlit foi exercitada com GET real sem exceções e mostrou o estado vazio. Após autorização explícita, POST/GET por ID/PATCH/GET/DELETE/GET final foram validados com um único registro sintético, removido ao final; nenhum valor ou ID foi registrado.
- [x] 1.3 Manter o uso sem autenticação conforme solicitado, sem interpretar `Public` como prova de segurança e sem alterar configurações de segurança, scripts ou publicação Xano. Escritas remotas só serão executadas após apresentar plano e obter autorização explícita.

## 2. Integrar o cliente HTTP existente

- [x] 2.1 Implementar GET coleção/ID, POST, PATCH e DELETE usando apenas as rotas informadas e o transporte existente; validar `id` e `nome`, trim de entrada, timeout, falhas HTTP e respostas incompatíveis.
- [x] 2.2 Validar rotas, payloads, flags, parsing e erros com transporte mockado, sem chamadas HTTP reais.
- [x] 2.3 Habilitar a integração por padrão com flags externas de opt-out para leitura e escrita; manter base URL configurável externamente e sem credenciais versionadas.

## 3. Implementar a página Streamlit

- [x] 3.1 Exibir listagem do Xano, estado vazio, carregamento, erros e configuração desabilitada, sem fallback SQLite.
- [x] 3.2 Implementar cadastro, consulta individual e edição; validar nome obrigatório, trim e duplicidade contra o catálogo carregado, sem apresentar a validação local como garantia de unicidade concorrente do backend.
- [x] 3.3 Implementar exclusão do ID selecionado somente após confirmação explícita; apresentar erros do Xano sem sucesso fictício. Testar a interface com mocks, sem DELETE remoto.
- [x] 3.4 Não alterar Dashboard, `frontend/app.py`, Consultas, Prontuários ou outras Changes.

## 4. Preservar, validar e concluir

- [x] 4.1 Preservar SQLite, sua inicialização e o catálogo local ainda usado por Consultas; não copiar ou migrar dados.
- [x] 4.2 Atualizar a documentação com o contrato informado, o resultado do GET real, os limites de autorização e os controles de configuração.
- [x] 4.3 Executar a suíte completa de testes, validar OpenSpec strict, revisar `git diff --check` e verificar que os testes não fizeram mutações remotas nem alteraram arquivos fora do escopo. Resultado: 72 testes passaram; OpenSpec strict válido; `git diff --check` sem erros. Os testes usam mocks e não enviaram mutações remotas.
- [x] 4.4 Apresentar o plano de POST, PATCH e DELETE usando somente uma especialidade sintética criada para o teste; aguardar autorização explícita antes de executar as mutações. O usuário autorizou em 2026-11-09. POST, PATCH e DELETE foram executados somente no registro criado para o teste, e o GET final confirmou sua remoção. Nenhum registro preexistente foi alterado.
- [ ] 4.5 Após as validações autorizadas, revisar e fazer commit seletivo somente dos arquivos desta Change; arquivar em commit separado somente quando todos os critérios estiverem concluídos.

## Limites confirmados

Não criar nem publicar scripts Xano nesta Change, pois os endpoints informados já existem. O usuário autorizou a integração real e leituras; cada validação remota por POST, PATCH ou DELETE depende de um plano prévio e autorização explícita. Os testes automatizados devem continuar usando mocks. A garantia de unicidade concorrente e o comportamento de integridade referencial da API ainda não foram confirmados.
