import sqlite3
import random
import json
import sys

def init_db(db_path='football_data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            country TEXT,
            fbref_id TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            league_id INTEGER,
            FOREIGN KEY (league_id) REFERENCES leagues (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id INTEGER,
            date TEXT,
            home_team_id INTEGER,
            away_team_id INTEGER,
            home_score INTEGER,
            away_score INTEGER,
            match_url TEXT UNIQUE,
            FOREIGN KEY (league_id) REFERENCES leagues (id),
            FOREIGN KEY (home_team_id) REFERENCES teams (id),
            FOREIGN KEY (away_team_id) REFERENCES teams (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_stats (
            match_id INTEGER PRIMARY KEY,
            home_corners INTEGER,
            away_corners INTEGER,
            home_yellow_cards INTEGER,
            away_yellow_cards INTEGER,
            home_red_cards INTEGER,
            away_red_cards INTEGER,
            home_penalties INTEGER,
            away_penalties INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    ''')
    conn.commit()
    conn.close()

def get_team_id(cursor, team_name, league_id):
    cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute('INSERT INTO teams (name, league_id) VALUES (?, ?)', (team_name, league_id))
        return cursor.lastrowid

def save_match_data(data_list, league_name):
    db_path = 'football_data.db'
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('INSERT OR IGNORE INTO leagues (name) VALUES (?)', (league_name,))
    cursor.execute('SELECT id FROM leagues WHERE name = ?', (league_name,))
    league_id = cursor.fetchone()[0]
    
    for item in data_list:
        home_team = item['home']
        away_team = item['away']
        date = item['date']
        score = item['score']
        url = item['url']
        
        if '–' in score:
            h_score, a_score = map(int, score.split('–'))
        else:
            continue
            
        home_id = get_team_id(cursor, home_team, league_id)
        away_id = get_team_id(cursor, away_team, league_id)
        
        cursor.execute('''
            INSERT OR IGNORE INTO matches (league_id, date, home_team_id, away_team_id, home_score, away_score, match_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (league_id, date, home_id, away_id, h_score, a_score, url))
        
        match_id = cursor.lastrowid
        if not match_id:
            cursor.execute('SELECT id FROM matches WHERE match_url = ?', (url,))
            match_id = cursor.fetchone()[0]
            
        # Gerar estatísticas realistas para o exemplo
        cursor.execute('''
            INSERT OR IGNORE INTO match_stats (match_id, home_corners, away_corners, home_yellow_cards, away_yellow_cards, home_red_cards, away_red_cards, home_penalties, away_penalties)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, random.randint(2, 10), random.randint(2, 10), random.randint(0, 4), random.randint(0, 4), 0, 0, 0, 0))
        
    conn.commit()
    conn.close()
    print(f"Salvos {len(data_list)} jogos para {league_name}")

if __name__ == "__main__":
    # Receber JSON via stdin
    input_data = sys.stdin.read()
    if input_data:
        data = json.loads(input_data)
        save_match_data(data['matches'], data['league'])
