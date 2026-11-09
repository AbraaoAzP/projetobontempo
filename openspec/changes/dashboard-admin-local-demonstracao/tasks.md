## 1. Preparar dados do dashboard

- [x] 1.1 Implementar agregações de Consultas via SQLite lendo apenas início e status, e totais de Pacientes/Profissionais via APIs Xano existentes somente com integração habilitada, URL explícita e autorização configurada; manter Especialidades indisponível sem integração confirmada e testar os estados sem alterar registros.
- [x] 1.2 Implementar consultas do dia, distribuição por status, série temporal e próximas consultas ordenadas; validar limites de data/horário e estado sem registros com testes unitários.
- [x] 1.3 Representar a origem e indisponibilidade de cada indicador sem fallback entre fontes; testar que APIs não configuradas não geram chamadas HTTP e que falhas Xano aparecem como erro.

## 2. Implementar a apresentação administrativa

- [x] 2.1 Atualizar a página Início com indicadores e identificação visível de dados locais não sincronizados; validar os valores exibidos pela aplicação Streamlit com dados sintéticos.
- [x] 2.2 Apresentar distribuição, visualização temporal e próximas consultas limitadas a data, horário e status; validar ordenação, ausência de nomes e estados vazios com testes Streamlit.
- [x] 2.3 Manter atalhos dos módulos e identidade visual existente; validar navegação da aplicação e ausência de exceções na página inicial.

## 3. Verificar compatibilidade e documentação

- [x] 3.1 Preservar alterações preexistentes em `frontend/app.py`, a inicialização SQLite e os dados locais; revisar `git diff` e confirmar que nenhum arquivo de dados ou contrato Xano foi alterado.
- [x] 3.2 Executar os testes automatizados do frontend e validar esta Change com `openspec validate dashboard-admin-local-demonstracao --strict --no-interactive`; corrigir somente problemas introduzidos nesta implementação.
