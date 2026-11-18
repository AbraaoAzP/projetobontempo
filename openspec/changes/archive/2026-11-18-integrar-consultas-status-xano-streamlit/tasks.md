## 1. Confirmar contratos e segurança

- [x] 1.1 Confirmar no painel os contratos POST `/consulta`, PATCH `/consulta/{consulta_id}` e DELETE `/consulta/{consulta_id}`, incluindo campos e respostas conhecidas; registrar em design.md que as escritas não foram executadas.
- [x] 1.2 Confirmar os contratos GET dos catálogos por leitura HTTP real em 2026-11-18: Pacientes, Profissionais, Especialidades, Status e Profissional–Especialidade responderam HTTP 200 com os campos registrados em design.md.
- [x] 1.3 Confirmar a ausência de evidência contratual de duração, disponibilidade e garantia de conflito no backend; o frontend usará bloqueio conservador somente para a mesma combinação profissional/instante, sem afirmar proteção remota.

## 2. Completar operações do cliente Xano

- [x] 2.1 Revisar e testar POST de Consulta com transporte simulado, incluindo referências positivas, timestamp inteiro, observações nula e rejeição de payload incompleto.
- [x] 2.2 Revisar e testar PATCH parcial de Consulta com transporte simulado, preservando campo omitido versus `observacoes: null` e validando os campos permitidos.
- [x] 2.3 Revisar e testar DELETE de Consulta com transporte simulado e identificação de falhas HTTP, sem solicitar confirmação pelo cliente como substituto de autorização.
- [x] 2.4 Manter `XANO_CONSULTAS_WRITE_ENABLED=false` como estado padrão e impedir qualquer chamada remota quando o valor não estiver habilitado.

## 3. Completar a página Consultas

- [x] 3.1 Substituir o ramo SQLite de Consultas por estados Xano exclusivos e verificar que nenhum método SQLite é chamado pela página.
- [x] 3.2 Implementar cadastro com seletores reais de paciente, profissional, especialidade vinculada e status; validar campos, data, horário e timestamp antes do POST.
- [x] 3.3 Implementar consulta individual por ID e preenchimento seguro do formulário de edição sem copiar ou registrar observações privadas em log.
- [x] 3.4 Implementar edição parcial de consultas com referências válidas e vínculo profissional-especialidade confirmado.
- [x] 3.5 Implementar exclusão com seleção, confirmação explícita e tratamento de respostas HTTP; manter o botão desabilitado sem habilitação explícita.
- [x] 3.6 Validar conflito no frontend pela coleção carregada e impedir sobreposição entre consultas efetivamente ocupantes; registrar que a regra definitiva continua no backend.

## 4. Cache e estados de erro

- [x] 4.1 Preservar cache curto somente para leituras e não armazenar erros HTTP em sucesso ou lista vazia.
- [x] 4.2 Tratamento explícito para HTTP 429 e ausência de reruns automáticos ou loop de requisições.
- [x] 4.3 Apresentar estados de configuração ausente, catálogo vazio, resposta incompatível, transporte, 400/401/403/404/409/429 e sucesso somente após resposta compatível.

## 5. Testes e verificação local

- [x] 5.1 Adicionar testes Xano simulados para POST, PATCH e DELETE sem rede e confirmar que nenhuma mutação real é enviada.
- [x] 5.2 Adicionar testes Streamlit simulados para cadastro, consulta individual, edição, exclusão confirmada/cancelada e vínculo profissional-especialidade.
- [x] 5.3 Executar a suíte completa com `frontend/.venv\Scripts\python.exe -m unittest discover -s tests -v`; resultado registrado: 95 testes aprovados.
- [x] 5.4 Executar `openspec validate integrar-consultas-status-xano-streamlit --strict --no-interactive` e revisar os artefatos; resultado válido.
- [x] 5.5 Verificar a interface Streamlit local em modo Xano: `/4_Consultas` respondeu HTTP 200, com escritas desabilitadas e sem POST/PATCH/DELETE reais.

## 6. Validação remota controlada

- [x] 6.1 Apresentar plano remoto sintético com criação, consulta, edição, exclusão e limpeza; aguardar autorização explícita antes de execução. Evidência: em 2026-11-18, o plano foi apresentado e a autorização explícita foi recebida antes da execução controlada.
- [x] 6.2 Após autorização, testar somente registros sintéticos usando a configuração externa e não alterar registros preexistentes. Evidência: em 2026-11-18 foram confirmados POST e GET de criação/leitura, PATCH e GET de atualização, DELETE com resposta 2xx aceita pelo cliente e GET posterior com HTTP 404 real; o registro temporário ID 1 foi removido, a flag persistida de escrita ficou `false` e nenhum registro preexistente foi alterado.
- [x] 6.3 Registrar o resultado ou pendência sem enviar credenciais ou dados pessoais aos artefatos versionados. Evidência: este checkpoint registra apenas o método, os códigos HTTP, a limpeza e a preservação dos registros preexistentes; nenhuma credencial ou dado pessoal foi incluído.
