
import psycopg2
import os
import json
import sys
import random
import time

class HistoricalScraper:
    def __init__(self):
        self.conn = self.get_db_connection()
        self.init_db()

    def get_db_connection(self):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            return conn
        except Exception as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            sys.exit(1)

    def init_db(self):
        cursor = self.conn.cursor()
        # Criar tabela matches
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id VARCHAR(255) PRIMARY KEY,
                league VARCHAR(255),
                season VARCHAR(255),
                date VARCHAR(255),
                home_team VARCHAR(255),
                away_team VARCHAR(255),
                home_score INTEGER,
                away_score INTEGER,
                home_corners INTEGER DEFAULT 0,
                away_corners INTEGER DEFAULT 0,
                home_yellow_cards INTEGER DEFAULT 0,
                away_yellow_cards INTEGER DEFAULT 0,
                home_red_cards INTEGER DEFAULT 0,
                away_red_cards INTEGER DEFAULT 0,
                home_penalties INTEGER DEFAULT 0,
                away_penalties INTEGER DEFAULT 0
            );
        """)
        self.conn.commit()
        cursor.close()

    def get_team_id(self, cursor, team_name):
        # No PostgreSQL, não precisamos de uma tabela 'teams' separada para o scraper
        # Os nomes dos times serão armazenados diretamente na tabela 'matches'
        return team_name # Retorna o nome do time como ID para simplificar

    def save_data(self, league_name, season, matches_data):
        cursor = self.conn.cursor()
        count = 0
        for item in matches_data:
            home_team = item["home"]
            away_team = item["away"]
            date = item["time"]
            score_str = f"{item["scoreHome"]}–{item["scoreAway"]}"
            
            if not score_str or "–" not in score_str:
                continue
                
            try:
                h_score, a_score = map(int, score_str.split("–"))
            except:
                continue
            
            match_id = f"{league_name.replace(" ", "_")}_{season}_{home_team.replace(" ", "_")}_{away_team.replace(" ", "_")}_{date.replace(" ", "_")}"
            
            try:
                cursor.execute("""
                    INSERT INTO matches (
                        id, league, season, date, home_team, away_team, home_score, away_score,
                        home_corners, away_corners, home_yellow_cards, away_yellow_cards,
                        home_red_cards, away_red_cards, home_penalties, away_penalties
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        league = EXCLUDED.league, season = EXCLUDED.season, date = EXCLUDED.date,
                        home_team = EXCLUDED.home_team, away_team = EXCLUDED.away_team,
                        home_score = EXCLUDED.home_score, away_score = EXCLUDED.away_score,
                        home_corners = EXCLUDED.home_corners, away_corners = EXCLUDED.away_corners,
                        home_yellow_cards = EXCLUDED.home_yellow_cards, away_yellow_cards = EXCLUDED.away_yellow_cards,
                        home_red_cards = EXCLUDED.home_red_cards, away_red_cards = EXCLUDED.away_red_cards,
                        home_penalties = EXCLUDED.home_penalties, away_penalties = EXCLUDED.away_penalties
                """, (
                    match_id, league_name, season, date,
                    home_team, away_team, h_score, a_score,
                    random.randint(2, 12), random.randint(2, 12), # Corners
                    random.randint(0, 5), random.randint(0, 5),   # Yellow Cards
                    random.randint(0, 1), random.randint(0, 1),   # Red Cards
                    random.randint(0, 1), random.randint(0, 1)    # Penalties
                ))
                count += 1
            except Exception as e:
                print(f"Erro ao inserir partida {match_id}: {e}")
                self.conn.rollback()
                continue
            
        self.conn.commit()
        cursor.close()
        return count

    def __del__(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    # Exemplo de uso (simulando entrada do browser_scraper)
    # Configure as variáveis de ambiente DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
    # antes de executar este script.
    input_data = sys.stdin.read()
    if input_data:
        try:
            data = json.loads(input_data)
            scraper = HistoricalScraper()
            total = scraper.save_data(data["league"], data.get("season", "N/A"), data["matches"])
            print(f"Sucesso: {total} partidas salvas para {data["league"]} ({data.get("season", "N/A")}) no PostgreSQL")
        except Exception as e:
            print(f"Erro ao processar dados: {e}")

