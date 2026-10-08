# Tasks

## 1. Persistência e validações

- [x] 1.1 Criar a tabela própria `profissional` com ID gerado, nome obrigatório e campos opcionais de contato/especialidade; verificar no Xano o schema, a chave primária e a ausência de índices únicos em dados pessoais.
- [x] 1.2 Implementar validação backend de nome, telefone e e-mail conforme a spec, reutilizando a regra de telefone definida no design; verificar entrada válida e erros controlados para entradas inválidas antes de persistir.

### Evidências da Task 1.2

- O POST válido retornou HTTP 200, gerou o ID 1 e retornou nome, telefone, e-mail e especialidade.
- POST com nome vazio retornou HTTP 400 (`Missing param: nome`); POST com telefone inválido retornou HTTP 400 (`Telefone inválido`); POST com e-mail inválido retornou HTTP 400 (`Invalid email format`). Nenhuma dessas respostas gerou ID.
- Leitura da Meta API confirmou que os três cadastros inválidos não foram persistidos.
- O endpoint publicado aplica trim e validação de nome, usa o tipo `email` para validar e-mail e chama `validar_telefone_paciente`; as preconditions ocorrem antes de `db.add`.
- GET individual do ID 1 retornou HTTP 200 com os campos esperados; ID inexistente retornou HTTP 404.
- [x] 1.3 Verificar que cadastros inválidos de nome, telefone ou e-mail não criam registros e que falhas de edição não aplicam alterações parciais.

## 2. Cadastro e consulta pela API

- [x] 2.1 Criar o grupo/API de profissionais e o POST de cadastro; verificar ID gerado, resposta limitada aos campos permitidos e rejeição de dados inválidos sem persistência.

### Evidências da Task 2.1

- Grupo/API de profissionais publicado; POST válido retornou HTTP 200 e gerou o ID 1.
- A resposta do POST retornou os campos esperados (`id`, `nome`, `telefone`, `email`, `especialidade`); o artefato local do endpoint projeta somente esses campos.
- POST com nome vazio, telefone inválido e e-mail inválido retornou HTTP 400 em cada caso, sem gerar ID; leitura da Meta API confirmou a ausência dos registros inválidos.
- [ ] 2.2 Implementar GET de listagem; verificar lista vazia sem registros, inclusão de profissionais cadastrados e exposição somente de ID, nome, telefone, e-mail e especialidade.

### Situação da Task 2.2

- O endpoint de listagem foi implementado e validado com HTTP 200 e retorno limitado aos campos permitidos.
- O cenário de lista vazia não foi comprovado comportamentalmente. Nenhum fixture existente foi excluído apenas para produzir artificialmente esse cenário.
- A task permanece pendente até que o cenário obrigatório de lista vazia possa ser verificado.

- [x] 2.3 Implementar GET individual por ID; verificar profissional existente, resposta limitada aos campos permitidos e 404 para ID inexistente sem expor outros registros.

### Evidências da Task 2.3

- Dry-run previewou somente a criação do endpoint `profissional/{profissional_id}` GET; um documento foi publicado no workspace 153318, branch `v1`.
- GET do fixture ID 1 retornou HTTP 200 e exatamente `id`, `nome`, `telefone`, `email` e `especialidade`.
- GET do ID inexistente `2147483647` retornou HTTP 404; a resposta não continha campos de registro profissional.
- [x] 2.4 Verificar que coincidências em nome, telefone, e-mail ou especialidade não impedem cadastros distintos e que os IDs gerados são diferentes.

### Evidências da Task 2.4

- Foram criados dois registros sintéticos com os mesmos dados de negócio: nome `TESTE TASK 2.4 DUPLICADO`, telefone `+55 (11) 91234-5678`, e-mail `task24.duplicado@example.com` e especialidade `TESTE TASK 2.4`.
- Os dois POSTs retornaram HTTP 200; os IDs gerados foram 2 e 3, distintos entre si, apesar da coincidência dos quatro campos.
- Ambos retornaram somente `id`, `nome`, `telefone`, `email` e `especialidade`. Os registros permanecem no Xano; o fixture ID 1 não foi alterado.

## 3. Edição e remoção pela API

- [x] 3.1 Implementar PATCH parcial de nome, telefone, e-mail e especialidade; verificar atualização de valores válidos, preservação de campos omitidos, tratamento documentado de nome vazio e remoção de opcionais enviados vazios.
- [x] 3.2 Verificar que PATCH inválido não altera parcialmente o registro, que o ID não pode ser alterado e que PATCH para profissional inexistente retorna 404 sem criar registro.

### Evidências da Task 3.2

- No profissional de teste ID 3, PATCH com nome válido e telefone inválido retornou HTTP 400; GET antes e depois confirmou que ID, nome, telefone, e-mail e especialidade permaneceram iguais.
- PATCH do ID 3 com `id: 999` retornou o ID 3; GET posterior confirmou que o identificador persistido continuou sendo 3.
- PATCH para o ID inexistente `2147483647` retornou HTTP 404; GET para o mesmo ID também retornou HTTP 404, confirmando que nenhum registro foi criado.
- [x] 3.3 Implementar DELETE físico com verificação de existência; verificar sucesso para profissional existente e 404 para ID inexistente.

### Evidências da Task 3.3

- Dry-run previewou somente a criação do endpoint `profissional/{profissional_id}` DELETE; um documento foi publicado no workspace 153318, branch `v1`.
- GET confirmou que o profissional ID 3 existia antes da remoção. DELETE do ID 3 retornou HTTP 200 com `success: true`.
- Após a remoção, GET individual do ID 3 retornou HTTP 404. A checagem de listagem solicitada retornou HTTP 200 em formato de lista com IDs 1 e 2, sem o ID 3; essa evidência também foi registrada na Task 3.4.
- DELETE do ID inexistente `2147483647` retornou HTTP 404. Os IDs 1 e 2 não foram alterados nem removidos.
- [x] 3.4 Verificar que, após DELETE, o profissional deixa de aparecer no GET individual e na listagem.

### Evidências da Task 3.4

- Após o DELETE do profissional de teste ID 3, GET individual retornou HTTP 404.
- A listagem posterior retornou HTTP 200 em formato de lista com IDs 1 e 2; o ID 3 removido não apareceu. Evidências coletadas durante a verificação da Task 3.3; fixture ID 1 e registro ID 2 preservados.

## 4. Verificação integrada

- [x] 4.1 Validar todos os artefatos XanoScript da capability profissionais com as ferramentas disponíveis e resolver erros antes da publicação.

### Evidências da Task 4.1

- O Xano Developer MCP não estava disponível; foi usado o Xano CLI 1.3.0 com `workspace push --dry-run`, filtrado para os seis arquivos `xano/api/profissionais/*.xs`, a tabela `xano/table/profissional.xs` e a função compartilhada `xano/function/validar_telefone_paciente.xs` (8 de 29 arquivos correspondentes).
- O dry-run não reportou erros de validação XanoScript nem referências não resolvidas. Ele previewou updates da tabela, grupo de API, POST e PATCH; a comparação somente leitura com o pull remoto mostrou diferenças de metadados/serialização e formatação, sem divergência funcional identificada.
- Nenhum artefato Xano foi publicado ou alterado durante a validação; nenhum teste comportamental foi executado, pois a Task 4.1 trata de validação dos artefatos.
- [ ] 4.2 Executar fluxo integrado de cadastro, consulta, edição parcial e remoção em ambiente de teste; verificar os contratos de resposta, validação, ausência de alterações parciais e limpeza dos registros descartáveis.

### Situação da Task 4.2

- A task exige a execução do fluxo integrado em ambiente de teste.
- O workspace disponível possui somente a branch `v1`, marcada como live; não foi encontrado ambiente de teste separado.
- Por segurança, nenhum fluxo integrado foi executado na branch live.
- A task permanece bloqueada por condição de ambiente.

- [ ] 4.3 Confirmar que as tabelas e APIs existentes de `user` e `paciente` permanecem inalteradas e que não foram criadas disponibilidades, agendamentos, relacionamentos ou autenticação nesta Change.

### Situação da Task 4.3

- As alterações encontradas nos endpoints de pacientes são compatíveis com comportamentos documentados no Change `cadastro-pacientes`.
- Não existe evidência cronológica suficiente para determinar quando as linhas atuais foram introduzidas, nem evidência suficiente para atribuir essas alterações ao Change `cadastro-profissionais`.
- Por isso, o critério de preservação das APIs existentes não pode ser considerado comprovado.
- A task permanece pendente.
