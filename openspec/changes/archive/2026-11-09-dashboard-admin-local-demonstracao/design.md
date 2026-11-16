## Context

Consulte [proposal.md](./proposal.md) para a motivação e as especificações delta em `specs/`. A página inicial atual constrói atalhos em `frontend/app.py`; a persistência local e as consultas disponíveis estão em `frontend/services/database.py`. A API Xano existente para Pacientes/Profissionais é controlada por configuração, e as mudanças de autenticação e autorização permanecem pendentes. Não há contrato de API integrado para Especialidades ou Consultas.

## Goals / Non-Goals

**Goals:**

- Reutilizar leituras existentes do SQLite para compor os indicadores locais sem modificar seu schema ou registros.
- Tornar a proveniência dos números inequívoca na interface e manter o estado de cada integração Xano separado.
- Apresentar um painel responsivo com componentes Streamlit já disponíveis no projeto.
- Limitar a agenda inicial a data, horário e status enquanto não houver autorização verificada para expor identificadores de pacientes.

**Non-Goals:**

- Ativar ou alterar chamadas Xano, definir contratos novos ou afirmar disponibilidade de endpoints apenas porque há arquivos Xano locais.
- Migrar, semear, editar ou excluir dados SQLite ou remotos.
- Implementar autenticação, autorização, prontuários ou mudanças no fluxo existente de Consultas.
- Remover a inicialização SQLite existente ou mudar os dados já cadastrados.

## Decisions

1. **Separar a origem por entidade.** Consultas e agenda usam as funções de leitura existentes do SQLite, com rótulo local/não sincronizado. Pacientes e Profissionais usam somente os GETs já implementados e somente quando `XANO_API_ENABLED=true`, a URL base do recurso estiver explicitamente configurada e `XANO_AUTHORIZATION` estiver presente; respostas remotas são reduzidas imediatamente a contagens. Sem qualquer pré-condição, a API falhar ou retornar resposta inválida, o indicador fica indisponível/erro e nunca recebe fallback SQLite. Especialidades fica indisponível porque o frontend ainda não tem cliente e contrato confirmado para essa capacidade. Essa política atende ao pedido de usar somente integração configurada e autorizada sem presumir disponibilidade por existirem arquivos Xano locais. Alternativa considerada: buscar todas as entidades no SQLite; rejeitada para Pacientes/Profissionais/Especialidades pelo requisito de fonte Xano.

2. **Extrair agregações sem nova persistência.** Criar funções pequenas em serviço de dashboard para consultas do dia, distribuição por status, série temporal dos próximos sete dias e próximas consultas ativas ordenadas. Reutilizar uma consulta SQLite dedicada que retorna somente início e status da consulta, sem carregar nomes de paciente/profissional, e `get_statuses`; não usar listagens SQLite de pacientes, profissionais ou especialidades como fallback. Alternativa considerada: consultar o SQLite diretamente em `app.py` ou reutilizar a listagem completa de consultas com dados pessoais; ambas rejeitadas para reduzir duplicação e exposição desnecessária.

3. **Usar componentes nativos do Streamlit e identidade visual existente.** Organizar os quatro totais em cards, destacar consultas de hoje, apresentar distribuição e agenda em tabelas/cartões legíveis e reutilizar os estilos de `frontend/ui.py`. Não adicionar dependências. Dados pessoais e observações clínicas não serão exibidos na lista inicial.

4. **Preservar alterações já existentes na aplicação.** A implementação futura deverá integrar o dashboard à função de início vigente sem restaurar o carregamento de exemplos ou remover edições preexistentes em `frontend/app.py`. SQLite continuará sendo inicializado e a navegação existente será mantida.

## Risks / Trade-offs

- [Os dados locais podem estar desatualizados ou não refletir o Xano] → Rotular consultas e agenda como locais/não sincronizadas, e separar os indicadores Xano por fonte.
- [Um endpoint existente pode não estar acessível ou a credencial pode não ter permissão de leitura] → Fazer somente GET quando a configuração exigida estiver presente; apresentar erro/indisponibilidade sem fallback e sem ocultar a falha.
- [A base local pode estar vazia] → Exibir zero e estados vazios, sem criar dados de demonstração automaticamente.
- [Uma consulta da agenda pode conter identificadores pessoais] → Mostrar somente data, horário e status no dashboard; manter o detalhamento nas telas existentes até os controles de acesso serem aprovados.
- [A função inicial contém edições preexistentes] → Integrar com patch pequeno e verificar o diff específico antes da conclusão, sem reverter alterações alheias.

## Migration Plan

Não há migração. Implementar localmente, testar com fixtures sintéticas e preservar o arquivo SQLite existente. Rollback consiste em remover somente os componentes do dashboard introduzidos nesta Change, sem tocar nos registros SQLite ou nas edições preexistentes.
