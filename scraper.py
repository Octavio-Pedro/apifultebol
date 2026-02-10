import requests
from bs4 import BeautifulSoup
import time
import random
import sqlite3
import re

class FootballScraper:
    def __init__(self, db_path='football_data.db'):
        self.db_path = db_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
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

    def get_team_id(self, team_name, league_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM teams WHERE name = ?', (team_name,))
        result = cursor.fetchone()
        if result:
            team_id = result[0]
        else:
            cursor.execute('INSERT INTO teams (name, league_id) VALUES (?, ?)', (team_name, league_id))
            team_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return team_id

    def scrape_league_schedule(self, league_name, fbref_url):
        print(f"Iniciando coleta para: {league_name}")
        response = requests.get(fbref_url, headers=self.headers)
        if response.status_code != 200:
            print(f"Erro ao acessar {fbref_url}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Adicionar liga se não existir
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO leagues (name, fbref_id) VALUES (?, ?)', (league_name, fbref_url.split('/')[-2]))
        cursor.execute('SELECT id FROM leagues WHERE name = ?', (league_name,))
        league_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        table = soup.find('table', {'id': re.compile('sched_.*')})
        if not table:
            print("Tabela de jogos não encontrada.")
            return

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            if row.get('class') and 'spacer' in row.get('class'):
                continue
            
            date_cell = row.find('td', {'data-stat': 'date'})
            home_cell = row.find('td', {'data-stat': 'home_team'})
            away_cell = row.find('td', {'data-stat': 'away_team'})
            score_cell = row.find('td', {'data-stat': 'score'})
            report_cell = row.find('td', {'data-stat': 'match_report'})

            if not (date_cell and home_cell and away_cell and score_cell and report_cell):
                continue

            date = date_cell.text.strip()
            home_team = home_cell.text.strip()
            away_team = away_cell.text.strip()
            score = score_cell.text.strip()
            report_link = report_cell.find('a')

            if not report_link or not score or '–' not in score:
                continue

            match_url = "https://fbref.com" + report_link.get('href')
            home_score, away_score = map(int, score.split('–'))

            home_id = self.get_team_id(home_team, league_id)
            away_id = self.get_team_id(away_team, league_id)

            # Salvar partida
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO matches (league_id, date, home_team_id, away_team_id, home_score, away_score, match_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (league_id, date, home_id, away_id, home_score, away_score, match_url))
                match_id = cursor.lastrowid
                if not match_id: # Já existia
                    cursor.execute('SELECT id FROM matches WHERE match_url = ?', (match_url,))
                    match_id = cursor.fetchone()[0]
                
                # Simular coleta de estatísticas detalhadas (seria necessário acessar a match_url)
                # Para este protótipo, vamos gerar alguns dados fictícios baseados no placar
                # Em uma versão real, faríamos requests.get(match_url) aqui.
                cursor.execute('''
                    INSERT OR IGNORE INTO match_stats (match_id, home_corners, away_corners, home_yellow_cards, away_yellow_cards, home_red_cards, away_red_cards, home_penalties, away_penalties)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (match_id, random.randint(2, 12), random.randint(2, 12), random.randint(0, 5), random.randint(0, 5), 0, 0, 0, 0))
                
            except Exception as e:
                print(f"Erro ao salvar partida: {e}")
            
            conn.commit()
            conn.close()
            
        print(f"Coleta concluída para {league_name}.")

if __name__ == "__main__":
    scraper = FootballScraper()
    # Exemplo: Brasileirão 2026 (URL fictícia baseada na estrutura real)
    scraper.scrape_league_schedule("Brasileirão Série A", "https://fbref.com/en/comps/24/schedule/Serie-A-Scores-and-Fixtures")
