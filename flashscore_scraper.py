
import sqlite3
import time
import json

def save_to_db(matches):
    conn = sqlite3.connect('football_data.db')
    cursor = conn.cursor()
    
    # Garantir que a tabela tenha as colunas necessárias para estatísticas detalhadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id TEXT PRIMARY KEY,
            league TEXT,
            season TEXT,
            date TEXT,
            home_team TEXT,
            away_team TEXT,
            home_score INTEGER,
            away_score INTEGER,
            home_corners INTEGER,
            away_corners INTEGER,
            home_yellow_cards INTEGER,
            away_yellow_cards INTEGER,
            home_red_cards INTEGER,
            away_red_cards INTEGER,
            home_penalties INTEGER,
            away_penalties INTEGER
        )
    ''')
    
    for m in matches:
        cursor.execute('''
            INSERT OR REPLACE INTO matches (
                id, league, season, date, home_team, away_team, home_score, away_score,
                home_corners, away_corners, home_yellow_cards, away_yellow_cards,
                home_red_cards, away_red_cards, home_penalties, away_penalties
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            m.get('id'), m.get('league'), m.get('season'), m.get('date'),
            m.get('home_team'), m.get('away_team'), m.get('home_score'), m.get('away_score'),
            m.get('home_corners', 0), m.get('away_corners', 0),
            m.get('home_yellow_cards', 0), m.get('away_yellow_cards', 0),
            m.get('home_red_cards', 0), m.get('away_red_cards', 0),
            m.get('home_penalties', 0), m.get('away_penalties', 0)
        ))
    
    conn.commit()
    conn.close()

# Este script será chamado via browser_console_exec para extrair os dados
# O código JS abaixo é o que será executado no console do navegador
EXTRACT_JS = """
function extractFlashscoreData() {
    const matches = [];
    const rows = document.querySelectorAll('.event__match');
    const league = document.querySelector('.heading__name')?.innerText || 'Unknown';
    const season = document.querySelector('.heading__info')?.innerText || 'Unknown';

    rows.forEach(row => {
        const id = row.id.replace('g_1_', '');
        const date = row.querySelector('.event__time')?.innerText;
        const homeTeam = row.querySelector('.event__participant--home')?.innerText;
        const awayTeam = row.querySelector('.event__participant--away')?.innerText;
        const homeScore = parseInt(row.querySelector('.event__score--home')?.innerText) || 0;
        const awayScore = parseInt(row.querySelector('.event__score--away')?.innerText) || 0;

        matches.push({
            id, league, season, date,
            home_team: homeTeam,
            away_team: awayTeam,
            home_score: homeScore,
            away_score: awayScore
        });
    });
    return matches;
}
return extractFlashscoreData();
"""
