## Why

A relação N:N entre Profissionais e Especialidades já é usada pela página de
Consultas, mas o frontend ainda não permite criar ou remover esses vínculos.
Com os contratos POST e DELETE visualmente confirmados no painel Xano, esta
Change pode concluir o gerenciamento dessa associação sem depender do campo
textual legado de Especialidade.

## What Changes

- Adicionar no XanoClient métodos HTTP para criar e excluir registros de
  `profissional_especialidade`.
- Permitir que a página de Profissionais liste as especialidades vinculadas,
  crie novos vínculos e remova vínculos existentes.
- Validar IDs positivos, referências existentes e duplicidade do par
  Profissional–Especialidade antes da gravação.
- Invalidação de cache após criação ou exclusão para manter os dados do
  frontend atualizados.
- Cobrir os métodos e a interação da página com testes que usam transporte
  HTTP e componentes Streamlit simulados.
- Preservar `profissional.especialidade` como campo legado e manter o uso dos
  vínculos relacionais já confirmado pela página de Consultas.

**Fora do escopo:** migração automática do campo textual legado; alteração
das tabelas ou endpoints no Xano live; autenticação e perfis; remoção do
SQLite global; testes remotos com dados reais.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `profissionais`: passa a permitir o gerenciamento explícito dos vínculos
  relacionais com Especialidades sem substituir o campo textual legado.
- `interface-web`: passa a oferecer criação e remoção confirmada de vínculos
  na página de Profissionais e atualização dos dados em cache.

## Impact

- Frontend: `frontend/pages/2_Profissionais.py`,
  `frontend/services/xano.py` e `frontend/services/xano_cache.py`.
- Testes: `frontend/tests/test_crud_pages.py`, `frontend/tests/test_xano.py`
  e testes simulados relacionados ao gerenciamento de vínculos.
- Configuração: uso das bases e flags já existentes para o recurso
  `profissional_especialidade`, mantendo escritas desabilitadas por configuração
  até sua habilitação deliberada.
- Integração: a página de Consultas continua consumindo o GET da coleção para
  restringir Especialidades ao vínculo confirmado.
