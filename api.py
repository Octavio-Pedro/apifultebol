from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Football Stats API", description="API independente para estatísticas de futebol")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("API Iniciando na porta 8000...")


# Configuração de CORS para permitir acesso de outros domínios (como sites criados pelo Manus)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchResponse(BaseModel):
    id: int
    league: str
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
    return {
        "message": "Bem-vindo à API de Estatísticas de Futebol!",
        "status": "Online",
        "endpoints": {
            "matches": "/matches",
            "team_stats": "/stats/team/{team_name}",
            "zero_zero_stats": "/stats/0x0"
        }
    }

@app.get("/matches", response_model=List[MatchResponse])
def get_matches(limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT m.id, l.name as league, m.date, t1.name as home_team, t2.name as away_team, 
               m.home_score, m.away_score, s.home_corners, s.away_corners,
               s.home_yellow_cards, s.away_yellow_cards
        FROM matches m
        JOIN leagues l ON m.league_id = l.id
        JOIN teams t1 ON m.home_team_id = t1.id
        JOIN teams t2 ON m.away_team_id = t2.id
        JOIN match_stats s ON m.id = s.match_id
        ORDER BY m.date DESC
        LIMIT ?
    '''
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "league": row["league"],
            "date": row["date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "corners": {"home": row["home_corners"], "away": row["away_corners"]},
            "cards": {"home_yellow": row["home_yellow_cards"], "away_yellow": row["away_yellow_cards"]}
        })
    return results

@app.get("/stats/0x0")
def get_zero_zero_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches WHERE home_score = 0 AND away_score = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return {"total_jogos_0x0": count}

@app.get("/stats/team/{team_name}")
def get_team_stats(team_name: str, last_n: int = 15):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM teams WHERE name LIKE ?", (f"%{team_name}%",))
    team = cursor.fetchone()
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="Time não encontrado")
    
    team_id = team[0]
    
    query = '''
        SELECT 
            COUNT(*) as total_jogos,
            SUM(CASE WHEN home_team_id = ? THEN home_corners ELSE away_corners END) as total_escanteios,
            AVG(CASE WHEN home_team_id = ? THEN home_corners ELSE away_corners END) as media_escanteios
        FROM (
            SELECT m.id, m.home_team_id, s.home_corners, s.away_corners
            FROM matches m
            JOIN match_stats s ON m.id = s.match_id
            WHERE m.home_team_id = ? OR m.away_team_id = ?
            ORDER BY m.date DESC
            LIMIT ?
        )
    '''
    cursor.execute(query, (team_id, team_id, team_id, team_id, last_n))
    result = cursor.fetchone()
    conn.close()
    
    return {
        "team": team_name,
        "periodo": f"últimos {last_n} jogos",
        "estatisticas": {
            "jogos_analisados": result["total_jogos"],
            "total_escanteios": result["total_escanteios"],
            "media_escanteios": round(result["media_escanteios"], 2) if result["media_escanteios"] else 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
