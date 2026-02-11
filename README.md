# Football Stats API - Versão Profissional (v7)

Esta versão transforma sua API em uma plataforma robusta, automatizada e inteligente para estatísticas de futebol global (2022-2026).

## 🚀 Novidades da Versão 7

1.  **Suporte a PostgreSQL:** Migração do SQLite para um banco de dados profissional, garantindo que seus dados nunca sejam perdidos e suportando múltiplos acessos simultâneos.
2.  **Agendamento Automático:** Script `scheduler.py` para automatizar a coleta de dados, mantendo sua base sempre atualizada sem intervenção manual.
3.  **Motor de Predição:** Novo endpoint `/predict` que utiliza inteligência baseada em médias históricas para sugerir tendências de gols e escanteios.

## 🛠️ Configuração do Banco de Dados (PostgreSQL)

Para que a API funcione no Koyeb ou em qualquer servidor, você deve configurar as seguintes variáveis de ambiente:

*   `DB_HOST`: Endereço do seu banco (ex: `ep-lucky-sun-123.us-east-2.aws.neon.tech`)
*   `DB_NAME`: Nome do banco de dados
*   `DB_USER`: Usuário do banco
*   `DB_PASSWORD`: Senha do banco

**Dica:** Recomendo usar o [Neon.tech](https://neon.tech) para um banco PostgreSQL gratuito e persistente.

## 📈 Novos Endpoints

### 1. Predição de Partida
Calcula a expectativa de gols e escanteios para um confronto baseado no histórico dos dois times.
*   **URL:** `/predict/{time_casa}/{time_fora}`
*   **Exemplo:** `/predict/Palmeiras/Flamengo`

### 2. Estatísticas de Time (Melhorado)
Analisa o desempenho detalhado de um time nos últimos N jogos.
*   **URL:** `/stats/team/{nome_do_time}?last_n=15`

### 3. Filtros por Liga e Temporada
*   **URL:** `/matches?league=Premier League&season=2024-2025`

## 🤖 Automação

O arquivo `scheduler.py` pode ser rodado como um processo separado. Ele executará o scraper periodicamente para manter seus dados sempre atualizados.

---
Desenvolvido para cobertura global de futebol (2022-2026).
