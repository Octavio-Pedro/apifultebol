# Arquitetura do Sistema e Modelo de Dados

O sistema será composto por três componentes principais: o **Coletor de Dados (Scraper)**, o **Banco de Dados (PostgreSQL/SQLite)** e a **API de Consulta (FastAPI)**. Esta estrutura garante que os dados sejam coletados de forma independente e fiquem disponíveis para consultas rápidas e complexas.

## Componentes do Sistema

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Coletor** | Python (BeautifulSoup/Requests) | Extrai dados do FBref e outras fontes, processa e salva no banco. |
| **Banco de Dados** | SQLite (para protótipo) / PostgreSQL | Armazena o histórico de partidas, times e estatísticas detalhadas. |
| **API REST** | Python (FastAPI) | Disponibiliza endpoints para que outros sites consultem as estatísticas. |

## Modelo de Dados (Entidade-Relacionamento)

Para suportar as consultas solicitadas pelo usuário, o banco de dados será estruturado da seguinte forma:

### Tabela: `leagues`
Armazena informações sobre os campeonatos.
- `id`: Identificador único (PK).
- `name`: Nome do campeonato (ex: Brasileirão Série A).
- `country`: País de origem.
- `fbref_id`: ID usado no site FBref para facilitar o scraping.

### Tabela: `teams`
Armazena informações sobre os clubes.
- `id`: Identificador único (PK).
- `name`: Nome do time.
- `league_id`: Referência ao campeonato (FK).

### Tabela: `matches`
Armazena os dados básicos de cada partida.
- `id`: Identificador único (PK).
- `league_id`: Referência ao campeonato (FK).
- `date`: Data da partida.
- `home_team_id`: Time da casa (FK).
- `away_team_id`: Time visitante (FK).
- `home_score`: Gols do time da casa.
- `away_score`: Gols do time visitante.
- `match_url`: Link original para referência ou re-scraping.

### Tabela: `match_stats`
Armazena estatísticas detalhadas de cada partida.
- `match_id`: Referência à partida (FK).
- `home_corners`: Escanteios do time da casa.
- `away_corners`: Escanteios do time visitante.
- `home_yellow_cards`: Cartões amarelos do time da casa.
- `away_yellow_cards`: Cartões amarelos do time visitante.
- `home_red_cards`: Cartões vermelhos do time da casa.
- `away_red_cards`: Cartões vermelhos do time visitante.
- `home_penalties`: Pênaltis para o time da casa.
- `away_penalties`: Pênaltis para o time visitante.

## Estratégia de Consulta

As perguntas específicas do usuário serão resolvidas através de queries SQL otimizadas:
- **Jogos 0x0**: `SELECT COUNT(*) FROM matches WHERE home_score = 0 AND away_score = 0`
- **Escanteios nos últimos 15 jogos**: `SELECT SUM(CASE WHEN home_team_id = :id THEN home_corners ELSE away_corners END) FROM match_stats JOIN matches ON matches.id = match_stats.match_id WHERE (home_team_id = :id OR away_team_id = :id) ORDER BY date DESC LIMIT 15`
