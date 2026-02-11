
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
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
    conn = sqlite3.connect('football_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    conn = get_db_connection()
    cursor = conn.cursor()
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
        "status": "Online",
        "ligas_disponiveis": leagues,
        "temporadas_disponiveis": seasons,
        "endpoints": {
            "matches": "/matches?league=Premier League&season=2024-2025",
            "team_stats": "/stats/team/{team_name}?last_n=15",
            "zero_zero_stats": "/stats/0x0?league=La Liga&season=2022-2023"
        }
    }

@app.get("/matches", response_model=List[MatchResponse])
def get_matches(league: Optional[str] = None, season: Optional[str] = None, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT id, league, season, date, home_team, away_team, 
               home_score, away_score, home_corners, away_corners,
               home_yellow_cards, away_yellow_cards, home_red_cards, away_red_cards
        FROM matches
        WHERE 1=1
    '''
    params = []
    if league:
        query += " AND league LIKE ?"
        params.append(f"%{league}%")
    if season:
        query += " AND season = ?"
        params.append(season)
    
    query += " ORDER BY date DESC LIMIT ?"
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

@app.get("/stats/0x0")
def get_zero_zero_stats(league: Optional[str] = None, season: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT COUNT(*) FROM matches WHERE home_score = 0 AND away_score = 0"
    params = []
    if league:
        query += " AND league LIKE ?"
        params.append(f"%{league}%")
    if season:
        query += " AND season = ?"
        params.append(season)
        
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return {"league": league if league else "Todas", "season": season if season else "Todas", "total_jogos_0x0": count}

@app.get("/stats/team/{team_name}")
def get_team_stats(team_name: str, last_n: int = 15):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar jogos onde o time participou
    query = '''
        SELECT 
            home_team, away_team, home_score, away_score, 
            home_corners, away_corners, home_team == ? as is_home
        FROM matches
        WHERE home_team LIKE ? OR away_team LIKE ?
        ORDER BY date DESC
        LIMIT ?
    '''
    search_term = f"%{team_name}%"
    cursor.execute(query, (team_name, search_term, search_term, last_n))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Time não encontrado ou sem jogos registrados")
    
    total_escanteios = 0
    jogos_analisados = len(rows)
    
    for row in rows:
        if row['is_home']:
            total_escanteios += (row['home_corners'] or 0)
        else:
            total_escanteios += (row['away_corners'] or 0)
            
    media_escanteios = total_escanteios / jogos_analisados if jogos_analisados > 0 else 0
    
    return {
        "team": team_name,
        "periodo": f"últimos {jogos_analisados} jogos",
        "estatisticas": {
            "jogos_analisados": jogos_analisados,
            "total_escanteios": total_escanteios,
            "media_escanteios": round(media_escanteios, 2)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
