# Descobertas da Pesquisa - API de Futebol Independente

## Fontes de Dados Identificadas
- **FBref**: Excelente para estatísticas detalhadas de partidas, incluindo gols, cartões e métricas avançadas.
- **Flashscore**: Bom para resultados em tempo real e estatísticas básicas (escanteios, cartões).
- **SofaScore**: Interface rica, mas requer scraping mais complexo devido ao carregamento dinâmico.

## Estrutura de Dados do FBref
- **URLs de Competição**: `https://fbref.com/en/comps/<ID>/schedule/<Nome>-Scores-and-Fixtures`
- **URLs de Partida**: `https://fbref.com/en/matches/<ID>/<Nome-da-Partida>`
- **Seletores Úteis**:
    - Tabelas de estatísticas usam o atributo `data-stat`.
    - Exemplo: `td[data-stat="goals"]`, `td[data-stat="corners"]`, `td[data-stat="cards_yellow"]`.
    - O FBref usa comentários HTML para esconder algumas tabelas, o que pode exigir um tratamento especial no scraping (remover tags de comentário para processar o conteúdo).

## Desafios de Scraping
- **Ad-blockers e Pop-ups**: O site exibe pop-ups que podem interferir na navegação automatizada.
- **Rate Limiting**: O FBref é conhecido por bloquear IPs que fazem muitas requisições rápidas. É necessário usar delays e possivelmente proxies/rotação de User-Agent.
- **Tabelas Dinâmicas**: Algumas estatísticas avançadas são carregadas via JavaScript ou estão dentro de comentários HTML.

## Próximos Passos (Fase 2)
- Modelar o banco de dados para suportar consultas complexas (ex: "últimos 15 jogos").
- Definir a arquitetura da API (Python/FastAPI parece ideal).
