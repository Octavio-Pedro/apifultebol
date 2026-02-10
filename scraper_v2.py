import sqlite3
import random
import json
import sys
import time

class MultiLeagueScraper:
    def __init__(self, db_path='football_data.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
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

    def get_team_id(self, cursor, team_name, league_id):
        cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            cursor.execute('INSERT INTO teams (name, league_id) VALUES (?, ?)', (team_name, league_id))
            return cursor.lastrowid

    def save_league_data(self, league_name, matches_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Inserir ou obter ID da liga
        cursor.execute('INSERT OR IGNORE INTO leagues (name) VALUES (?)', (league_name,))
        cursor.execute('SELECT id FROM leagues WHERE name = ?', (league_name,))
        league_id = cursor.fetchone()[0]
        
        count = 0
        for item in matches_data:
            home_team = item['home']
            away_team = item['away']
            date = item['date']
            score = item['score']
            url = item['url']
            
            if not score or '–' not in score:
                continue
                
            try:
                h_score, a_score = map(int, score.split('–'))
            except:
                continue
                
            home_id = self.get_team_id(cursor, home_team, league_id)
            away_id = self.get_team_id(cursor, away_team, league_id)
            
            cursor.execute('''
                INSERT OR IGNORE INTO matches (league_id, date, home_team_id, away_team_id, home_score, away_score, match_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (league_id, date, home_id, away_id, h_score, a_score, url))
            
            match_id = cursor.lastrowid
            if not match_id:
                cursor.execute('SELECT id FROM matches WHERE match_url = ?', (url,))
                match_id = cursor.fetchone()[0]
                
            # Gerar estatísticas simuladas para o protótipo (em produção seria scraping real da match_url)
            cursor.execute('''
                INSERT OR IGNORE INTO match_stats (match_id, home_corners, away_corners, home_yellow_cards, away_yellow_cards, home_red_cards, away_red_cards, home_penalties, away_penalties)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (match_id, random.randint(2, 12), random.randint(2, 12), random.randint(0, 5), random.randint(0, 5), 0, 0, 0, 0))
            count += 1
            
        conn.commit()
        conn.close()
        return count

if __name__ == "__main__":
    # Receber JSON via stdin para processamento em lote
    input_data = sys.stdin.read()
    if input_data:
        try:
            data = json.loads(input_data)
            scraper = MultiLeagueScraper()
            total = scraper.save_league_data(data['league'], data['matches'])
            print(f"Sucesso: {total} partidas salvas para {data['league']}")
        except Exception as e:
            print(f"Erro ao processar dados: {e}")
