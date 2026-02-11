
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Football Stats API", description="API independente para estatísticas de futebol global (2022-2026)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL de conexão fornecida pelo usuário (pode ser configurada via variável de ambiente DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_DRPAFgfK9y2M@ep-orange-brook-ai94k6jr-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require")

class MatchResponse(BaseModel):
    id: str
    league: str
    season: str
    date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    corners: dict
    cards: dict

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados")

@app.get("/")
def read_root():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT DISTINCT league FROM matches")
        leagues = [row["league"] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT season FROM matches WHERE season IS NOT NULL")
        seasons = [row["season"] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Erro ao ler banco: {e}")
        leagues, seasons = [], []
    finally:
        conn.close()
        
    return {
        "message": "Bem-vindo à API de Estatísticas de Futebol Global!",
        "status": "Online (Conectado ao Neon.tech)",
        "ligas_disponiveis": leagues,
        "temporadas_disponiveis": seasons,
        "endpoints": {
            "matches": "/matches?league=Premier League&season=2024-2025",
            "team_stats": "/stats/team/{team_name}?last_n=15",
            "predict": "/predict/{time_casa}/{time_fora}"
        }
    }

@app.get("/matches", response_model=List[MatchResponse])
def get_matches(league: Optional[str] = None, season: Optional[str] = None, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = "SELECT * FROM matches WHERE 1=1"
    params = []
    if league:
        query += " AND league ILIKE %s"
        params.append(f"%{league}%")
    if season:
        query += " AND season = %s"
        params.append(season)
    
    query += " ORDER BY date DESC LIMIT %s"
    params.append(limit)
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    except Exception as e:
        logger.error(f"Erro na query: {e}")
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
        
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": str(row["id"]),
            "league": row["league"],
            "season": row["season"] if row["season"] else "N/A",
            "date": row["date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "corners": {"home": row["home_corners"], "away": row["away_corners"]},
            "cards": {
                "home_yellow": row["home_yellow_cards"], 
                "away_yellow": row["away_yellow_cards"],
                "home_red": row["home_red_cards"],
                "away_red": row["away_red_cards"]
            }
        })
    return results

@app.get("/stats/team/{team_name}")
def get_team_stats(team_name: str, last_n: int = 15):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = "SELECT *, (home_team ILIKE %s) as is_home FROM matches WHERE home_team ILIKE %s OR away_team ILIKE %s ORDER BY date DESC LIMIT %s"
    search_term = f"%{team_name}%"
    cursor.execute(query, (search_term, search_term, search_term, last_n))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    
    total_escanteios = sum(row["home_corners"] if row["is_home"] else row["away_corners"] for row in rows)
    media_escanteios = total_escanteios / len(rows)
    
    return {
        "team": team_name,
        "periodo": f"últimos {len(rows)} jogos",
        "estatisticas": {"media_escanteios": round(media_escanteios, 2)}
    }

@app.get("/predict/{team_home}/{team_away}")
def predict_match(team_home: str, team_away: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    def get_avg(name):
        cursor.execute("SELECT AVG(CASE WHEN home_team ILIKE %s THEN home_corners ELSE away_corners END) as avg_c FROM matches WHERE home_team ILIKE %s OR away_team ILIKE %s", (f"%{name}%", f"%{name}%", f"%{name}%"))
        return cursor.fetchone()["avg_c"] or 0

    avg_h = get_avg(team_home)
    avg_a = get_avg(team_away)
    conn.close()
    
    return {
        "confronto": f"{team_home} vs {team_away}",
        "expectativa_escanteios": round(avg_h + avg_a, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
