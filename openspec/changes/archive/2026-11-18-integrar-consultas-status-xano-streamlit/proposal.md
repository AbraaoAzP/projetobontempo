## Why

As consultas já possuem leituras preparadas no Xano, mas o módulo ainda não oferece um CRUD utilizável e ainda mantém um caminho SQLite quando as leituras Xano estão desabilitadas. A Change precisa concluir a operação funcional completa sem confundir listagem remota ou testes automatizados com validação real do módulo.

## What Changes

- Completar cadastro, consulta individual, edição e exclusão de consultas pela API Xano confirmada.
- Remover o fallback SQLite da página Consultas, preservando o banco somente para módulos e indicadores que ainda dependam dele.
- Validar todos os campos obrigatórios, referências válidas, vínculo profissional-especialidade, data, horário e conflitos antes de enviar escritas.
- Converter data e horário locais de Streamlit para timestamp Unix em milissegundos e preservar `observacoes` conforme o contrato.
- Confirmar respostas, erros HTTP, transporte, resposta incompatível e HTTP 429 sem repetir requisições.
- Exigir confirmação explícita na exclusão e manter escritas remotas desabilitadas por configuração até autorização explícita.
- Atualizar os testes automatizados para cobrir o CRUD com transporte e Streamlit simulados, sem escritas reais.

**Fora do escopo:** alterar endpoints, tabelas, permissões ou configurações remotas; autenticação ou perfis; módulos de Prontuários; migração global do SQLite; POST/PATCH/DELETE reais sem autorização.

## Capabilities

### New Capabilities

- Nenhuma nova capability; a funcionalidade permanece dentro de `consultas`.

### Modified Capabilities

- `consultas`: o comportamento passa de preparação de leitura para CRUD completo Xano, sem fallback SQLite e com validações de conflito.
- `interface-web`: a página Consultas deixa de possuir dependência ou apresentação legada SQLite.

## Impact

- Código principal: `frontend/pages/4_Consultas.py`, `frontend/services/xano.py` e `frontend/services/xano_cache.py`.
- Testes principais: `frontend/tests/test_consultations_page.py` e `frontend/tests/test_xano.py`.
- Configuração: `XANO_CONSULTAS_API_ENABLED=true` e `XANO_CONSULTAS_WRITE_ENABLED=false` por padrão até autorização específica.
- Persistência: `frontend/data/bontempo_demo.sqlite3` e `frontend/services/database.py` permanecem preservados enquanto houver dependências externas, mas não serão usados pela página Consultas.
