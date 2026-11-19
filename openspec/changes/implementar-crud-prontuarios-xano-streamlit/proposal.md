## Why

O backend remoto já expõe um contrato confirmado de Prontuários no Xano,
enquanto o frontend ainda não possui uma página funcional para listar ou
gerenciar esses registros. A entrega acadêmica precisa integrar esse CRUD
incrementalmente, sem SQLite, sem autenticação nesta etapa e sem implementar
Registros de Atendimento.

## What Changes

- Confirmar no cliente Xano os cinco endpoints existentes de Prontuários:
  GET da coleção, POST, GET por ID, PATCH por ID e DELETE por ID.
- Criar uma página Streamlit que lista, consulta, cadastra, edita e exclui
  Prontuários por meio dessas APIs.
- Usar os Pacientes e Profissionais já carregados pelas integrações existentes
  como referências do formulário.
- Validar IDs positivos, campos básicos definidos pelo contrato e respostas
  compatíveis antes de informar sucesso.
- Exigir confirmação explícita para exclusão e manter escritas remotas
  desabilitadas por configuração até autorização explícita.
- Invalidar o cache de Prontuários após mutações bem-sucedidas.
- Adicionar testes locais com transporte HTTP e Streamlit simulados.
- Integrar a página à navegação existente sem migrar dados SQLite ou alterar
  visualizações do Dashboard.

**Fora do escopo:** Registro de Atendimento; autenticação e perfis; autoria
derivada de sessão; campos clínicos não confirmados; autorização backend;
fallback SQLite; migração de dados; alteração dos contratos remotos; execução
de POST/PATCH/DELETE reais sem autorização.

## Capabilities

### New Capabilities

- `prontuarios`: CRUD acadêmico de Prontuários por APIs Xano confirmadas,
  preservando referências a Paciente e Profissional e isolando dados clínicos
  não confirmados.

### Modified Capabilities

- `interface-web`: inclui navegação e disponibilidade da nova página
  Prontuários sem apresentar funcionalidades inexistentes como concluídas.

## Impact

- Frontend: `frontend/pages/5_Prontuarios.py`,
  `frontend/services/xano.py`, `frontend/services/xano_cache.py`,
  configuração externa e navegação principal.
- Testes: testes HTTP simulados em `frontend/tests/test_xano.py` e testes
  Streamlit para a página de Prontuários.
- Configuração: novas variáveis externas para API e escrita de Prontuários,
  com leitura/escrita desabilitadas por padrão até configuração e autorização
  explícitas.
- Persistência: nenhuma dependência ou fallback SQLite nesta Change.
