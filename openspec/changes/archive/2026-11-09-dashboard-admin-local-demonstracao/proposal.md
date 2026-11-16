## Why

A página Início apresenta somente atalhos e não oferece uma visão administrativa útil para a demonstração. Um dashboard local, com a origem dos dados explicitada e integrações pendentes sinalizadas, permite demonstrar indicadores reais da base SQLite sem sugerir que os dados estejam sincronizados com o Xano.

## What Changes

- Transformar a página Início em um dashboard administrativo com totais de pacientes, profissionais e especialidades somente quando APIs Xano existentes estiverem explicitamente configuradas e autorizadas; caso contrário, mostrar esses indicadores indisponíveis.
- Calcular totais, consultas do dia, distribuição por status, gráfico temporal e próximas consultas a partir do SQLite local, identificando essa origem sem apresentar dados clínicos sensíveis.
- Preservar os atalhos de navegação existentes para os módulos administrativos e aplicar a identidade visual Bontempo.
- Manter a implementação SQLite de Consultas e os dados existentes sem migração, exclusão ou alteração.
- Não habilitar novas chamadas, publicar recursos Xano, alterar dados remotos ou modificar autenticação.

## Capabilities

### New Capabilities

- `dashboard-admin`: apresenta indicadores e agenda administrativa com origem dos dados claramente identificada e estados explícitos de indisponibilidade.

### Modified Capabilities

- `interface-web`: substituir a página inicial meramente institucional por um dashboard e ampliar os atalhos, preservando a navegação e os limites de segurança.

## Impact

- Afeta a página inicial em `frontend/app.py` e poderá extrair a composição dos indicadores para um módulo de serviço reutilizável.
- Reutiliza listagens existentes em `frontend/services/database.py` para Consultas e o cliente Xano existente somente para APIs autorizadas de Pacientes/Profissionais; não adiciona dependências nem modifica o schema SQLite.
- Não altera contratos ou recursos Xano. Especialidades fica indisponível enquanto não houver integração confirmada; nenhuma fonte remota é inferida a partir de arquivos locais.
- Exige testes Streamlit com dados sintéticos e verificação de estados vazios/indisponíveis, sem dados médicos reais.
