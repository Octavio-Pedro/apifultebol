# API Independente de Estatísticas de Futebol

Este projeto é uma solução completa para coleta, armazenamento e consulta de dados de futebol, permitindo análises complexas sem depender de APIs pagas de terceiros.

## Estrutura do Projeto

| Arquivo | Descrição |
| :--- | :--- |
| `scraper.py` | Coletor de dados automatizado (Web Scraper) para o FBref. |
| `browser_scraper.py` | Script auxiliar para processar dados extraídos via navegador. |
| `api.py` | API REST desenvolvida com FastAPI para consulta dos dados. |
| `football_data.db` | Banco de dados SQLite contendo as informações coletadas. |

## Como Funciona

1.  **Coleta**: O sistema utiliza técnicas de web scraping para extrair resultados e estatísticas de sites como o FBref.
2.  **Armazenamento**: Os dados são normalizados e salvos em um banco de dados SQLite, estruturado para suportar consultas históricas.
3.  **Consulta**: A API disponibiliza endpoints que realizam cálculos em tempo real (ex: médias de escanteios, contagem de resultados específicos).

## Endpoints da API

### 1. Estatísticas de Resultados Específicos
Retorna a quantidade de jogos que terminaram em 0x0.
- **URL**: `/stats/0x0`
- **Método**: `GET`

### 2. Estatísticas por Time
Retorna o total e a média de escanteios de um time em um determinado período.
- **URL**: `/stats/team/{team_name}?last_n=15`
- **Método**: `GET`
- **Parâmetros**: `last_n` (opcional, padrão 15) define quantos jogos recentes analisar.

### 3. Listagem de Partidas
Retorna as últimas partidas com estatísticas detalhadas.
- **URL**: `/matches?limit=10`
- **Método**: `GET`

## Exemplo de Uso (JavaScript/Frontend)

```javascript
// Consultar quantos escanteios o Palmeiras fez nos últimos 15 jogos
fetch('https://sua-api.com/stats/team/Palmeiras?last_n=15')
  .then(response => response.json())
  .then(data => {
    console.log(`Média de escanteios: ${data.estatisticas.media_escanteios}`);
  });
```

## Deployment

Para colocar a API no ar, recomenda-se o uso de um servidor VPS com Docker ou a execução direta via `uvicorn`:
```bash
pip install fastapi uvicorn beautifulsoup4 requests
python api.py
```
