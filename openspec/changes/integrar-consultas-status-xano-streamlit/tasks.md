## 1. Confirmar contratos e configuração

- [x] 1.1 Registrar a fonte oficial e o contrato vigente de cada operação de Consulta e Status (método, rota, parâmetros, campos, resposta e requisitos de autorização); verificar que nenhum detalhe foi deduzido do SQLite ou de outra entidade. Os detalhes observados e as lacunas de schema estão em design.md.
- [ ] 1.2 Confirmar por contrato as fontes de Pacientes, Profissionais, Especialidades e a relação Profissional–Especialidade. Os scripts versionados confirmam os catálogos, mas só declaram `profissional.especialidade` como texto opcional e não mostram uma relação; confirmar no painel se existe uma referência, tabela de associação ou API autoritativa antes de concluir.
- [x] 1.3 Definir configuração externa e habilitação explícita da integração, respeitando os requisitos de autorização do contrato; verificar que não há URL sensível, token ou credencial versionados e que chamadas não ocorrem sem configuração.

## 2. Integrar operações Xano

- [x] 2.1 Estender o cliente HTTP existente para GET da coleção e por ID, validar os campos confirmados de Consulta e converter o timestamp Unix em milissegundos; verificar rotas, parsing, tipos e falhas com transporte simulado, sem executar escritas reais.
- [x] 2.2 Carregar os catálogos Xano confirmados para os formulários; sem fonte confirmada da relação Profissional–Especialidade, manter o seletor sem opções e desabilitado, sem inferência do campo textual. Verificar catálogo vazio, relação indisponível e ausência de fallback SQLite com mocks.
- [ ] 2.3 Implementar as operações CRUD de Consulta existentes no contrato e apresentar os erros retornados sem alegar garantias não confirmadas; verificar cada operação com transporte HTTP simulado.
- [ ] 2.4 Implementar a leitura do catálogo e a atualização de Status somente conforme contrato confirmado; verificar opções retornadas, estado vazio e rejeição/falha por mocks, sem hardcode do catálogo local como remoto.

## 3. Integrar a página e preservar dependências locais

- [x] 3.1 Conectar a página Consultas às leituras Xano confirmadas, listar os campos de Consulta conhecidos, carregar catálogos e preparar formulários com referências selecionáveis; verificar estados vazio/erro e GET por ID com mocks. POST, PATCH e DELETE permanecem desabilitados até validar relação e regras de integridade.
- [x] 3.2 Manter o Dashboard consultando Consultas e Status locais, com a origem local identificada; verificar que seus testes continuam passando e que os indicadores não usam dados Xano como substituição.
- [x] 3.3 Preservar arquivo, dados, schema, serviço e inicialização SQLite enquanto houver dependências; verificar no diff e nos testes que esta integração não migra, sincroniza, sobrescreve nem exclui dados locais.

## 4. Verificar a integração

- [x] 4.1 Executar testes automatizados da página, cliente Xano e Dashboard com transporte simulado; verificar que nenhum teste envia escritas remotas ou depende de rede.
- [ ] 4.2 Revisar configuração, contratos usados e estados de falha antes de habilitar a integração; verificar que operações sem contrato ou autorização confirmada permanecem indisponíveis e que não há fallback silencioso.
- [x] 4.3 Executar `openspec validate integrar-consultas-status-xano-streamlit --strict --no-interactive` e verificar que a Change passa sem alterar outras Changes.
